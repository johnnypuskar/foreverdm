from server.backend.instances.acts.act_type import ActType
from server.backend.instances.acts.act import Act
from server.backend.util.data_update import DataUpdate
from server.backend.database.locations import LocationsTable
from server.backend.database.statblocks import StatblocksTable
from src.stats.statblock import Statblock
from src.combat.map.map import Map
from src.combat.map.map_token import Token
from crosshash import crosshash

class CombatAct(Act):
    def __init__(self, campaign_id, location_id, statblock_ids = set()):
        super().__init__(campaign_id, location_id, statblock_ids)
        self.type = ActType.COMBAT
        self.store_on_close = True

        self.current_turn = 0
        self.map = Map(8, 8)
        for x in range(2, 6):
            self.map.get_tile(x, 2)._wall_top.set_passable(False)
            self.map.get_tile(x, 5)._wall_bottom.set_passable(False)
        for y in range(2, 6):
            self.map.get_tile(2, y)._wall_left.set_passable(False)
            self.map.get_tile(5, y)._wall_right.set_passable(False)

        map_data = LocationsTable.get_location_map(campaign_id, location_id)
        if map_data is not None:
            self.map.import_data(map_data)

        for statblock_id in self._statblock_ids:
            statblock = Statblock.new_from_data(StatblocksTable.get_statblock_data(statblock_id, campaign_id)) 
            self.map.add_token(Token(
                statblock,
                (0, 0, 0),
                self.map
            ))

        self.map_data_property("current_turn", "current_turn")
        self.map_data_property("map", "map")
    
    def get_view_data(self, statblock_id):
        data = super().get_view_data(statblock_id)
        data["map"] = self.map.export_view_data(statblock_id)
        data["hash"] = crosshash(data["map"])
        return data