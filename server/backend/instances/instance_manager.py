from server.backend.errors.error_index import Errors
from server.backend.util.socket_response import SocketResponse
from server.backend.database.statblocks import StatblocksTable
from server.backend.database.locations import LocationsTable
from server.backend.instances.instance import Instance
from server.backend.instances.acts.act_type import ActType
from server.backend.instances.commands.command_factory import CommandFactory

class InstanceManager:
    def __init__(self):
        self.instances = {}
        self.active_statblocks = {}

    def has_instance(self, campaign_id, location_id):
        return (
            self.instances.get(campaign_id) is not None and
            self.instances[campaign_id].get(location_id) is not None
        )

    def add_instance(self, campaign_id, location_id) -> Instance:
        if self.instances.get(campaign_id) is None:
            self.instances[campaign_id] = {}
        
        if self.instances[campaign_id].get(location_id) is None:
            self.instances[campaign_id][location_id] = Instance(campaign_id, location_id)
        
        return self.instances[campaign_id][location_id]
    
    def remove_instance(self, campaign_id, location_id) -> None:
        if self.instances.get(campaign_id) is not None:
            if self.instances[campaign_id].get(location_id) is not None:
                del self.instances[campaign_id][location_id]
                if not self.instances[campaign_id]:
                    del self.instances[campaign_id]

    def add_active_statblock(self, key, campaign_id, statblock_id):
        if self.active_statblocks.get(key) is not None and self.active_statblocks[key] != (campaign_id, statblock_id):
            campaign_id_old, statblock_id_old = self.active_statblocks[key]

            if self.instances.get(campaign_id_old) is not None:
                for location_id, instance in self.instances[campaign_id_old].items():
                    if instance.has_statblock(statblock_id_old):
                        instance.remove_statblock(statblock_id_old)
                        if not instance.has_statblock(statblock_id_old):
                            self.remove_instance(campaign_id_old, location_id)

        self.active_statblocks[key] = (campaign_id, statblock_id)
    
    def is_active_instance(self, campaign_id, location_id):
        if self.instances.get(campaign_id) is None:
            return False
        if self.instances[campaign_id].get(location_id) is None:
            return False
        for statblock_id in self.instances[campaign_id][location_id].act.statblock_ids:
            if (campaign_id, statblock_id) in self.active_statblocks.values():
                return True
        return False

    def remove_active_statblock(self, key):
        if key in self.active_statblocks:
            campaign_id, statblock_id = self.active_statblocks[key]
            del self.active_statblocks[key]

            if not self.is_active_instance(campaign_id, statblock_id):
                location_id = StatblocksTable.get_location(statblock_id, campaign_id)
                del self.instances[campaign_id][location_id]
                if len(self.instances[campaign_id]) == 0:
                    del self.instances[campaign_id]

    def get_instance_data(self, session_id, campaign_id, statblock_id):
        has_statblock, id_data = self._validate(session_id, campaign_id, statblock_id)
        if not has_statblock:
            return SocketResponse(
                signal = "set_instance_data",
                data = {
                    'view': 'CHARACTER_SELECT',
                    'data': id_data
                }
            )
        location_id = id_data

        if not self.has_instance(campaign_id, location_id):
            LocationsTable.validate_location_in_campaign(location_id, campaign_id)

            instance = self.add_instance(campaign_id, location_id)

            act_type, act_data = LocationsTable.get_paused_instance_act_details(location_id, campaign_id)

            if act_type is None or act_data is None:
                instance.set_act_type(ActType.WORLD)
                local_statblocks = LocationsTable.get_statblocks_at_location(location_id, campaign_id)
                for sb_id in local_statblocks:
                    instance.add_statblock(sb_id)
            else:
                instance.set_act_type(act_type)
                instance.act.import_data(act_data)
        else:
            instance = self.instances[campaign_id][location_id]
            instance.add_statblock(statblock_id)

        return SocketResponse(
            signal = "set_instance_data",
            data = {
                'view': instance.act.type,
                'data': instance.get_view_data(statblock_id)
            }
        )
    
    def send_command(self, session_id, campaign_id, statblock_id, command_type, args):
        has_statblock, id_data = self._validate(session_id, campaign_id, statblock_id)
        if not has_statblock:
            return SocketResponse(
                signal = "set_instance_data",
                data = {
                    'view': 'CHARACTER_SELECT',
                    'data': id_data
                }
            )
        location_id = id_data

        if not self.has_instance(campaign_id, location_id):
            raise Errors.NoInstanceFound()
        instance = self.instances[campaign_id][location_id]

        if not instance.has_statblock(statblock_id):
            raise Errors.StatblockNotInInstance()
        
        command = CommandFactory.new(command_type, statblock_id, campaign_id, *args)
        if not command.validate_act(instance.act):
            raise Errors.InvalidCommand(command_type)
        
        result, message = command.execute(instance)

        if not self.is_active_instance(campaign_id, location_id):
            del self.instances[campaign_id][location_id]
            if len(self.instances[campaign_id]) == 0:
                del self.instances[campaign_id]

        return SocketResponse(
            signal = "command_response",
            data = {
                "result": result,
                "message": message,
            }
        )


    def _validate(self, session_id, campaign_id, statblock_id):
        if statblock_id is None:
            statblock_ids = StatblocksTable.validate_user_statblocks_in_campaign(session_id, campaign_id)
            return (False, statblock_ids)

        location_id = StatblocksTable.validate_location_from_credentials(session_id, campaign_id, statblock_id)
        return (True, location_id)


    class ReturnException(Exception):
        def __init__(self, response):
            self.response = response