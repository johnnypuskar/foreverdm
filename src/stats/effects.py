from src.util.lua_manager import LuaManager

class Effect:
    def __init__(self, name, script, globals = {}):
        self._name = name
        self._globals = globals
        self._lua = None
        self._duration = 0

        roll_result_script = '''
        function RollResult(modifiers)
            roll_mod = {
                advantage = false,
                disadvantage = false,
                bonus = 0,
                auto_succeed = false,
                auto_fail = false
            }
            for key, value in pairs(modifiers) do
                roll_mod[key] = value
            end
            return roll_mod
        end

        function AddValue(value)
            return {operation = "add", value = value}
        end

        function SetValue(value)
            return {operation = "set", value = value}
        end

        '''
        self._script = roll_result_script + script
    
    @property
    def duration(self):
        return self._duration
    
    @duration.setter
    def duration(self, value):
        self._duration = value

    def initialize(self, globals):
        self._lua = LuaManager(self._globals)
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

class SubEffect(Effect):
    def __init__(self, name, script, globals = {}):
        super().__init__(name, script, globals)
        
    def has_function(self, function_name):
        if self._lua is None:
            raise RuntimeError("LuaManager not initialized.")
        return function_name in self._lua.globals['subeffects'][self._name]
    
    def run(self, function_name, *args):
        if self._lua is None:
            raise RuntimeError("LuaManager not initialized.")
        return self._lua.run_nested(f'subeffects.{self._name}.{function_name}', *args)
        
class EffectIndex:
    def __init__(self):
        self._effects = {}
    
    @property
    def effect_names(self):
        return self._effects.keys()

    def add(self, effect, duration):
        if isinstance(effect, Effect):
            if effect._name in self._effects:
                raise ValueError(f"Effect {effect._name} already exists in index.")
            effect.duration = duration
            self._effects[effect._name] = effect
        elif type(effect) is str:
            self.add(Effect("temp_name", effect), duration)
        
    def remove(self, name):
        if name not in self._effects:
            raise ValueError(f"Effect {name} not found in index.")
        del self._effects[name]
    
    def get_function_results(self, function_name, statblock, *args):
        results = []
        # Creating a copy list so that mid-execution dictionary editing does not throw an error
        keys = list(self._effects.keys())
        for effect_name in keys:
            effect = self._effects[effect_name]
            effect.initialize({"statblock": StatblockSubEffectWrapper(statblock, effect)})
            if effect.has_function(function_name):
                result = results.append(effect.run(function_name, *args))
                if result is not None:
                    results.append(result)
        return results

class StatblockSubEffectWrapper:
    def __init__(self, statblock, effect):
        self._statblock = statblock
        self._effect = effect
    
    def __getitem__(self, key):
        return getattr(self, key)
        
    def __getattr__(self, name):
        return getattr(self._statblock, name)
    
    def add_effect(self, subeffect_name, duration):
        subeffect = SubEffect(subeffect_name, self._effect._script, self._effect._globals)
        return self._statblock.add_effect(subeffect, duration)
    