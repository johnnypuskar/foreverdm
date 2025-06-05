from crosshash import crosshash
from server.backend.instances.commands.command import Command
from server.backend.instances.acts.combat_act import CombatAct
from server.backend.util.data_update import DataUpdate
from server.backend.database.locations import LocationsTable
from server.backend.database.statblocks import StatblocksTable

class MoveTokenCommand(Command):
    TYPE = "MOVE_TOKEN"

    def __init__(self, statblock_id, campaign_id, token_id, to_x, to_y):
        super().__init__(statblock_id, campaign_id)
        self.token_id = token_id
        self.to_x = to_x
        self.to_y = to_y
    
    def validate_act(self, act):
        return isinstance(act, CombatAct)
    
    def execute(self, instance):
        token = instance.act.map.get_token_by_id(self.token_id)
        if token is None:
            return Command.Response(False, "Token not found."), {}
        token.set_position((self.to_x, self.to_y, token.height))

        index = instance.act.map.get_token_index(self.token_id)
        return Command.Response(True, f"Token moved to ({self.to_x}, {self.to_y})."), {
            "updates": [
                DataUpdate.set(self.to_x, "tokens", index, "x"),
                DataUpdate.set(self.to_y, "tokens", index, "y")
            ],
            "hash": crosshash(instance.act.map.export_view_data(self.token_id))
        }
