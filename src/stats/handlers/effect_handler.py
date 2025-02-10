class EffectHandler:
    def __init__(self, statblock):
        self._statblock = statblock
    
    def add_effect(self, effect, duration):
        self._statblock._effects.add(effect, duration, self._statblock)
    
    def remove_effect(self, effect_name):
        self._statblock._effects.remove(effect_name)
    
