from server.backend.instances.acts.act_type import ActType
from server.backend.instances.acts.world_act import WorldAct
from server.backend.instances.acts.combat_act import CombatAct

class ActFactory:

    @staticmethod
    def new(act_type, campaign_id, location_id, statblock_ids = []):
        act_types = {
            ActType.WORLD: WorldAct,
            ActType.COMBAT: CombatAct
        }
        try:
            return act_types[ActType(act_type)](campaign_id, location_id, statblock_ids)
        except KeyError:
            raise ValueError(f"Unknown Act type: {act_type}")