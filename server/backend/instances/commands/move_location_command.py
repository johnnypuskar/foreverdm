from server.backend.instances.commands.command import Command
from server.backend.instances.acts.world_act import WorldAct
from server.backend.database.locations import LocationsTable
from server.backend.database.statblocks import StatblocksTable

class MoveLocationCommand(Command):
    TYPE = "MOVE_LOCATION"

    def __init__(self, statblock_id, campaign_id, destination_location_id):
        super().__init__(statblock_id, campaign_id)
        self.destination_location_id = destination_location_id
    
    def validate_act(self, act):
        return isinstance(act, WorldAct)
    
    def execute(self, instance):
        if not LocationsTable.is_statblock_adjacent(self.statblock_id, self.destination_location_id, self.campaign_id):
            return (False, "Not adjacent to destination.")
        
        StatblocksTable.update_location(self.statblock_id, self.campaign_id, self.destination_location_id)
        instance.remove_statblock(self.statblock_id)
        
        return (True, "Moved.")
