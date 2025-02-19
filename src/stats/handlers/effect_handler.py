class EffectHandler:
    def __init__(self, statblock):
        self._statblock = statblock
    
    def add_effect(self, effect, duration):
        self._statblock._effects.add(effect, duration, self._statblock)
    
    def remove_effect(self, effect_name):
        self._statblock._effects.remove(effect_name)
    
    def add_condition(self, condition_name, duration = -1):
        condition_effect = self._statblock._effects._condition_manager.new_condition(condition_name, None, duration)
        self.add_effect(condition_effect, duration)
    
    def remove_condition(self, condition_name):
        if condition_name not in self._statblock._effects._condition_manager.CONDITIONS.keys():
            raise ValueError(f"{condition_name} is not a valid condition.")
        self.remove_effect(condition_name)
