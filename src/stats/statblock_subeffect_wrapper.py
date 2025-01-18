from src.stats.condition_manager import ConditionManager
from src.stats.effects import SubEffect


class StatblockSubEffectWrapper:
    def __init__(self, statblock, effect):
        self._statblock = statblock
        self._effect = effect

    @staticmethod
    def create_wrapper(obj, effect):
        if isinstance(obj, (int, float, str, bool, type(None), dict)):
            return obj
        return StatblockSubEffectWrapper(obj, effect)

    def __getitem__(self, key):
        return getattr(self, key)
        
    def __getattr__(self, name):
        return getattr(self._statblock, name)
    
    def add_effect(self, subeffect_name, duration, globals = {}):
        subeffect = SubEffect(subeffect_name, self._effect._script, globals)
        return self._statblock.add_effect(subeffect, duration)
    
    def add_condition(self, condition_name, duration = -1):
        condition_manager = ConditionManager()
        condition_effect = condition_manager.new_condition(condition_name, None, duration)
        return self._statblock.add_effect(condition_effect, duration)

    def remove_effect(self, effect_name = None):
        if effect_name is None:
            self._statblock.remove_effect(self._effect._name)
        else:
            self._statblock.remove_effect(effect_name)

    def remove_condition(self, condition_name):
        if condition_name not in ConditionManager.CONDITIONS.keys():
            raise ValueError(f"{condition_name} is not a valid condition.")
        self._statblock.remove_effect(condition_name)

    def __eq__(self, value):
        if isinstance(value, StatblockSubEffectWrapper):
            return self._statblock == value._statblock
        return self._statblock == value