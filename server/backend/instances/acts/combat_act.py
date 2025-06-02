from server.backend.instances.acts.act_type import ActType
from server.backend.instances.acts.act import Act

class CombatAct(Act):
    def __init__(self, campaign_id, location_id, statblock_ids = set()):
        super().__init__(campaign_id, location_id, statblock_ids)
        self.type = ActType.WORLD

        self.current_turn = 0

        self.map_data_property("current_turn", "current_turn")