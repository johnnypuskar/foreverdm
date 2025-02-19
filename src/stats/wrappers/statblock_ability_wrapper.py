from src.util.constants import EventType
from src.stats.abilities.sub_ability import SubAbility
from src.stats.wrappers.statblock_wrapper import StatblockWrapper

class StatblockAbilityWrapper(StatblockWrapper):
    def __init__(self, statblock, ability):
        super().__init__(statblock)
        self._ability = ability

    def add_ability(self, ability_name):
        subability = SubAbility(ability_name, self._ability._script)
        return super().add_ability(subability)
    
    def remove_ability(self, ability_name = None):
        if ability_name is None:
            super().remove_ability(self._ability._name)
        else:
            super().remove_ability(ability_name)
    
    def add_effect(self, effect_name, duration):
        self._statblock._abilities.emit(EventType.ABILITY_APPLIED_EFFECT, effect_name, self._ability._script, duration, self._ability._uuid)
    
    def remove_effect(self, effect_name):
        self._statblock._abilities.emit(EventType.ABILITY_REMOVED_EFFECT, effect_name)

    def spell_attack_roll(self, target, damage_string):
        if "spellcasting_ability" not in self._ability._globals.keys():
            raise ValueError(f"Spellcasting ability not defined in Ability {self._ability._name}.")
        return self.ability_attack_roll(target, self._ability._globals["spellcasting_ability"], damage_string)