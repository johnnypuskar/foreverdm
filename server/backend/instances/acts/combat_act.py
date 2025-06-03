from server.backend.instances.acts.act_type import ActType
from server.backend.instances.acts.act import Act
from server.backend.database.locations import LocationsTable
from src.combat.map.map import Map
from crosshash import crosshash

class CombatAct(Act):
    def __init__(self, campaign_id, location_id, statblock_ids = set()):
        super().__init__(campaign_id, location_id, statblock_ids)
        self.type = ActType.COMBAT
        self.store_on_close = True

        self.map = Map(8, 8)
        map_data = LocationsTable.get_location_map(campaign_id, location_id)
        if map_data is not None:
            self.map.import_data(map_data)

        self.current_turn = 0

        self.map_data_property("current_turn", "current_turn")
        self.map_data_property("map", "map")
    
    def get_view_data(self, statblock_id):
        data = super().get_view_data(statblock_id)
        data["map"] = self.map.export_view_data(statblock_id)
        data["hash"] = crosshash(data["map"])
        return data