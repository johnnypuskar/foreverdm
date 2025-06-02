from server.backend.instances.acts.act_type import ActType
from server.backend.instances.acts.act import Act

from server.backend.database.locations import LocationsTable

class WorldAct(Act):
    def __init__(self, campaign_id, location_id, statblock_ids = set()):
        super().__init__(campaign_id, location_id, statblock_ids)
        self.type = ActType.WORLD

    
    def get_view_data(self, statblock_id):
        data = super().get_view_data(statblock_id)
        data["name"], data["description"], data["adjacent"] = LocationsTable.get_location_details(self.location_id, self.campaign_id)
        return data