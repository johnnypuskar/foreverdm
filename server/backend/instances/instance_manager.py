from src.instances.combat_instance import CombatInstance
from src.instances.world_instance import WorldInstance
from server.backend.database.serializers.statblock_serializer import StatblockSerializer
from server.backend.errors.error_index import Errors
from server.backend.util.socket_response import SocketResponse
from server.backend.database.users import UsersTable
from server.backend.database.statblocks import StatblocksTable
from server.backend.database.locations import LocationsTable

class InstanceManager:
    def __init__(self):
        self.instances = {}

    def validate(session_id, campaign_id):
        if session_id is None:
            raise InstanceManager.ReturnException(
                SocketResponse.Redirect("/login")
            )
        
        user_id = UsersTable.get_user_id(session_id)
        if user_id is None:
            raise InstanceManager.ReturnException(
                SocketResponse.Redirect("/login")
            )
        
        if campaign_id is None:
            raise InstanceManager.ReturnException(
                SocketResponse.Redirect("/campaigns")
            )
        
        if not StatblocksTable.is_user_in_campaign(user_id, campaign_id):
            raise InstanceManager.ReturnException(
                SocketResponse.Redirect("/campaigns")
            )
        
        return user_id


    def connect_user(self, session_id, campaign_id):
        try:
            user_id = self.validate(session_id, campaign_id)
            return SocketResponse(
                signal = 'connect_response',
                data = {
                    'success': True
                }
            )
        except InstanceManager.ReturnException as e:
            return e.response

        
    def get_instance_data(self, session_id, campaign_id, statblock_id):
        try:
            user_id = self.validate(session_id, campaign_id)
            try:
                location_id = StatblocksTable.validate_user_statblock_ownership(user_id, statblock_id, campaign_id)

                if not LocationsTable.is_location_id_in_campaign(location_id, campaign_id):
                    raise Errors.InvalidLocation()
                
                if self.instances.get(location_id) is None:
                    instance_type = LocationsTable.get_paused_instance_type_at_location(location_id, campaign_id)
                    
                    if instance_type == 'COMBAT':
                        instance = CombatInstance()
                    elif instance_type == 'WORLD' or instance_type is None:
                        instance = WorldInstance()
                    else:
                        raise Errors.InstanceTypeError()
                    
                    statblock_ids = StatblocksTable.get_statblocks_at_location_id(location_id, campaign_id)
                    for id in statblock_ids:
                        statblock_data = StatblocksTable.get_statblock_data(id, campaign_id)
                        statblock = StatblockSerializer.from_data(statblock_data)
                        instance.add_statblock(statblock)
                    self.instances[location_id] = instance

                return SocketResponse(
                    signal = 'set_instance_data',
                    data = {
                        'view': self.instances[location_id].type,
                        'data': self.instances[location_id].get_data()
                    }
                )
            except (Errors.StatblockNotInCampaign, Errors.UserNotOwnStatblock):
                return SocketResponse(
                    signal = 'set_instance_data',
                    data = {
                        'view': 'CHARACTER_SELECT',
                        'data': StatblocksTable.get_user_statblocks(user_id, campaign_id)
                    }
                )
        except InstanceManager.ReturnException as e:
            return e.response

    class ReturnException(Exception):
        def __init__(self, response):
            self.response = response