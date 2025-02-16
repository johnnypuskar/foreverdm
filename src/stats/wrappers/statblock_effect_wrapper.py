from src.stats.wrappers.statblock_wrapper import StatblockWrapper
from src.util.constants import EventType
from src.stats.effects.sub_effect import SubEffect

class StatblockEffectWrapper(StatblockWrapper):
    def __init__(self, statblock, effect):
        super().__init__(statblock)
        self._effect = effect

    def add_ability(self, ability_name):
        self._statblock._effects.emit(EventType.EFFECT_GRANTED_ABILITY, ability_name, self._effect._script)

    def remove_ability(self, ability_name):
        self._statblock._effects.emit(EventType.EFFECT_REMOVED_ABILITY, ability_name)

    def add_effect(self, subeffect_name, duration):
        subeffect = SubEffect(subeffect_name, self._effect._script)
        return self._statblock.add_effect(subeffect, duration)

    def remove_effect(self, effect_name = None):
        if effect_name is None:
            self._statblock.remove_effect(self._effect._name)
        else:
            self._statblock.remove_effect(effect_name)