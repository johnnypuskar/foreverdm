from src.util.lua_manager import LuaManager
from src.util.constants import ScriptData
from src.events.observer import Observer

class Effect(Observer):
    def __init__(self, name, script, globals = {}, duration = -1):
        super().__init__()
        self._name = name
        self._globals = {key: StatblockSubEffectWrapper.create_wrapper(value, self) for key, value in globals.items()}
        self._lua = None
        self._duration = duration

        self._script = ScriptData.ROLL_RESULT + ScriptData.ADD_VALUE + ScriptData.SET_VALUE + ScriptData.MULTIPLY_VALUE + ScriptData.DURATION + ScriptData.SPEED + script

        lua = LuaManager()
        lua.execute("conditions = {}")
        lua.execute(self._script)

        self._conditions = list(lua.globals["conditions"].values())
        
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

    def _synchronize_globals(self, new_globals):
        if isinstance(new_globals, dict):
            for key, value in new_globals.items():
                if isinstance(value, StatblockSubEffectWrapper):
                    for _, existing_value in self._globals.items():
                        if isinstance(existing_value, StatblockSubEffectWrapper) and existing_value._statblock == value._statblock:
                            new_globals[key] = existing_value
                            break
            return new_globals
        elif isinstance(new_globals, (list, tuple)):
            keep_list = isinstance(new_globals, list)
            new_globals = list(new_globals)
            for i in range(len(new_globals)):
                if isinstance(new_globals[i], StatblockSubEffectWrapper):
                    for _, existing_value in self._globals.items():
                        if isinstance(existing_value, StatblockSubEffectWrapper) and existing_value._statblock == new_globals[i]._statblock:
                            new_globals[i] = existing_value
                            break
            return new_globals if keep_list else tuple(new_globals)

    def initialize(self, globals = {}):
        globals = self._synchronize_globals(globals)
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
        args = list(args)
        for i in range(len(args)):
            args[i] = StatblockSubEffectWrapper.create_wrapper(args[i], self)
        args = self._synchronize_globals(args)
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
        args = list(args)
        for i in range(len(args)):
            args[i] = StatblockSubEffectWrapper.create_wrapper(args[i], self)
        args = self._synchronize_globals(args)
        if self._lua is None:
            raise RuntimeError("LuaManager not initialized.")
        return self._lua.run_nested(f'{self._name}.{function_name}', *args)
    
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
        condition_effect = self._statblock._effects._condition_manager.new_condition(condition_name, None, duration)
        return self._statblock.add_effect(condition_effect, duration)

    def remove_effect(self, effect_name = None):
        if effect_name is None:
            self._effect.remove(self._effect._name)
        else:
            self._effect.remove(effect_name)

    def remove_condition(self, condition_name):
        if condition_name not in self._statblock._effects._condition_manager.CONDITIONS.keys():
            raise ValueError(f"{condition_name} is not a valid condition.")
        self._statblock.remove_effect(condition_name)
    
    def __eq__(self, value):
        if isinstance(value, StatblockSubEffectWrapper):
            return self._statblock == value._statblock
        return self._statblock == value
