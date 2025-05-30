from src.stats.effects.conditions.condition import Blinded, Charmed, Deafened, Frightened, Grappled, Incapacitated, Invisible, Paralyzed, Poisoned, Prone, Restrained, Stunned, Unconscious

class ConditionManager:
    CONDITIONS = {
        "blinded": Blinded,
        "charmed": Charmed,
        "deafened": Deafened,
        "frightened": Frightened,
        "grappled": Grappled,
        "incapacitated": Incapacitated,
        "invisible": Invisible,
        "paralyzed": Paralyzed,
        "poisoned": Poisoned,
        "prone": Prone,
        "restrained": Restrained,
        "stunned": Stunned,
        "unconscious": Unconscious
    }

    def __init__(self):
        pass

    def new_condition(self, condition_type, parent_effect_name = None, duration = -1):
        condition_effect = self.CONDITIONS[condition_type](duration)
        if parent_effect_name is not None:
            condition_effect._name = parent_effect_name + "%" + condition_type
        return condition_effect
