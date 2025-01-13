from src.util.lua_manager import LuaManager
from src.util.constants import EventType, ScriptData
from src.events.observer import Emitter, Observer

class Effect(Observer):
    def __init__(self, name, script, globals = {}, duration = -1):
        super().__init__()
        self._name = name
        self._globals = {key: StatblockSubEffectWrapper.create_wrapper(value, self) for key, value in globals.items()}
        self._lua = None
        self._duration = duration

        self._script = ScriptData.ROLL_RESULT + ScriptData.ADD_VALUE + ScriptData.SET_VALUE + ScriptData.MULTIPLY_VALUE + ScriptData.DURATION + ScriptData.SPEED + script
    
    @property
    def duration(self):
        return self._duration
    
    @duration.setter
    def duration(self, value):
        self._duration = value

    def signal(self, event, *data):
        if event == "set_reference":
            key, value = data
            self._globals[key] = StatblockSubEffectWrapper.create_wrapper(value, self)

    def initialize(self, globals = {}):
        self._lua = LuaManager(self._globals)
        self._lua.connect(self)
        self._lua.merge_globals(globals)
        self._lua.execute(self._script)
        return self._lua

    def has_function(self, function_name):
        if self._lua is None:
            raise RuntimeError("LuaManager not initialized.")
        return function_name in self._lua.get_defined_functions()

    def run(self, function_name, *args):
        if self._lua is None:
            raise RuntimeError("LuaManager not initialized.")
        return self._lua.run(function_name, *args)

    def tick_timer(self):
        if self._duration > 0:
            self._duration -= 1

class SubEffect(Effect):
    def __init__(self, name, script, globals = {}, ability_uuid = None):
        script = ScriptData.USE_TIME + script
        super().__init__(name, script, globals)
        self._ability_uuid = ability_uuid
        
    def has_function(self, function_name):
        if self._lua is None:
            raise RuntimeError("LuaManager not initialized.")
        return function_name in self._lua.globals[self._name]
    
    def run(self, function_name, *args):
        if self._lua is None:
            raise RuntimeError("LuaManager not initialized.")
        return self._lua.run_nested(f'{self._name}.{function_name}', *args)
    
class EffectIndex(Observer, Emitter):
    def __init__(self):
        super().__init__()
        self._effects = {}
    
    def signal(self, event: str, *data):
        if event == EventType.ABILITY_APPLIED_EFFECT:
            # [data] = [effect_name, script, duration, globals, ability_uuid]
            ability_effect = SubEffect(data[0], data[1], data[3], data[4])
            self.add(ability_effect, data[2])
        elif event == EventType.ABILITY_REMOVED_EFFECT:
            # [data] = [effect_name]
            self.remove(data[0])
        elif event == EventType.ABILITY_CONCENTRATION_ENDED:
            # [data] = [ability_uuid]
            keys = list(self.effect_names)
            for effect_name in keys:
                effect = self._effects[effect_name]
                if isinstance(effect, SubEffect) and effect._ability_uuid == data[0]:
                    self.remove(effect_name)

    @property
    def effect_names(self):
        return self._effects.keys()

    def add(self, effect, duration, statblock = None):
        if isinstance(effect, Effect):
            if effect._name in self._effects:
                raise ValueError(f"Effect {effect._name} already exists in index.")
            effect.duration = duration
            self._effects[effect._name] = effect
            effect.initialize({"statblock": StatblockSubEffectWrapper(statblock, effect)})
            if effect.has_function("get_abilities"):
                for effect_ability in effect.run("get_abilities"):
                    self.emit(EventType.EFFECT_GRANTED_ABILITY, effect_ability, effect._script, "run")
            if effect.has_function("on_apply"):
                effect.run("on_apply")
        elif type(effect) is str:
            self.add(Effect("temp_name", effect), duration)
        
    def remove(self, name):
        if name not in self._effects:
            raise ValueError(f"Effect {name} not found in index.")
        removed_effect = self._effects.pop(name)
        removed_effect.initialize()
        if removed_effect.has_function("get_abilities"):
            for effect_ability in removed_effect.run("get_abilities"):
                self.emit(EventType.EFFECT_REMOVED_ABILITY, effect_ability)
    
    def get_function_results(self, function_name, statblock, *args):
        results = []
        # Creating a copy list so that mid-execution dictionary editing does not throw an error
        keys = list(self.effect_names)
        for effect_name in keys:
            effect = self._effects[effect_name]
            effect.initialize({"statblock": StatblockSubEffectWrapper(statblock, effect)})
            if effect.has_function(function_name):
                result = results.append(effect.run(function_name, *args))
                if result is not None:
                    results.append(result)
        return results

    def tick_timers(self, statblock):
        # Creating a copy list so that mid-execution dictionary editing does not throw an error
        keys = list(self.effect_names)
        for effect_name in keys:
            effect = self._effects[effect_name]
            effect.tick_timer()
            if effect.duration == 0:
                effect.initialize({"statblock": StatblockSubEffectWrapper(statblock, effect)})
                if effect.has_function("on_expire"):
                    effect.run("on_expire")
                self.remove(effect_name)

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
    