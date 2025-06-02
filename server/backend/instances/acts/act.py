from server.backend.instances.acts.act_type import ActType
from server.backend.database.util.data_storer import DataStorer

class Act(DataStorer):
    def __init__(self, campaign_id, location_id, statblock_ids = set()):
        super().__init__()
        self._type = None
        self.campaign_id = campaign_id
        self.location_id = location_id
        self._statblock_ids = statblock_ids

        self.map_data_property("campaign_id", "campaign_id")
        self.map_data_property("location_id", "location_id")
        self.map_data_property("statblock_ids", "statblock_ids")
    
    @property
    def type(self):
        return self._type.value
    
    @type.setter
    def type(self, value: ActType):
        self._type = value

    @property
    def statblock_ids(self):
        return self._statblock_ids

    @statblock_ids.setter
    def statblock_ids(self, value):
        if isinstance(value, list):
            value = set(value)
        self._statblock_ids = value
    
    def get_view_data(self, statblock_id):
        return { "view": self.type }