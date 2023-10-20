from src.stats.elements.numeric_stat import NumericStat
from src.stats.profiles.attacked_profile import AttackedProfile
from src.stats.profiles.modifier_profile import ModifierProfile
from src.stats.profiles.move_profile import MoveProfile
from src.stats.statblock.ability_register import AbilityRegister
from src.stats.statblock.proficiency_register import ProficiencyRegister

class HitPoints:
    def __init__(self, maximum, current = None, temporary = None):
        self._maximum = NumericStat("max hp", maximum)
        self._current = NumericStat("current hp", current if current is not None else maximum)
        self._temporary = NumericStat("temp hp", temporary if temporary is not None else 0)

class Statblock:
    def __init__(self, ability_scores, size, creature_type, hit_points, armor_class, speed, initiative, senses):
        self._ability_scores = ability_scores
        self._size = size
        self._creature_type = creature_type

        self._hit_points = hit_points
        self._armor_class = NumericStat("armor class", armor_class)
        self._speed = speed
        self._initiative = NumericStat("initiative", initiative)
        self._senses = senses

        self._damage_resistances = []
        self._damage_immunities = []
        self._condition_immunities = []

        self._proficiencies = ProficiencyRegister()
        self._abilities = AbilityRegister()
    
    def get_stat_profile(self, profile_type):
        profile_functions = {
            "move": self._profile_move,
            "attack_roll": self._profile_attack_roll,
            "deal_damage": self._profile_deal_damage,
            "attacked": self._profile_attacked,
            "strength_check": lambda: self._profile_ability_check("strength"),
            "dexterity_check": lambda: self._profile_ability_check("dexterity"),
            "constitution_check": lambda: self._profile_ability_check("constitution"),
            "intelligence_check": lambda: self._profile_ability_check("intelligence"),
            "wisdom_check": lambda: self._profile_ability_check("wisdom"),
            "charisma_check": lambda: self._profile_ability_check("charisma")
        }
        return profile_functions[profile_type]()

    def _profile_move(self):
        return MoveProfile(self._speed, self._size, self._creature_type, self._abilities["move"])

    def _profile_attack_roll(self):
        return NotImplementedError("Tried getting attack_roll profile from base statblock class (use character or monster statblock)")

    def _profile_deal_damage(self):
        raise NotImplementedError("Tried getting deal_damage profile from base statblock class (use character or monster statblock)")
    
    def _profile_attacked(self):
        return AttackedProfile(self._armor_class, self._damage_resistances, self._damage_immunities, self._abilities["attacked"])
    
    def _profile_ability_check(self, ability):
        return ModifierProfile(ability, getattr(self._ability_scores, ability), getattr(self._abilities, str(ability) + "_check"))
    
    def _profile_ability_save(self, ability):
        pass




