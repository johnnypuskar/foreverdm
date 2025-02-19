from src.stats.effects.effect import Effect
from src.util.constants import ScriptData
from src.util.lua_manager import LuaManager

class SubEffect(Effect):
    def __init__(self, name, script, ability_uuid = None):
        # UseTime function appended to script to avoid error from unknown function when creating a SubEffect from an ability script.
        super().__init__(name, ScriptData.USE_TIME + script)

        self._ability_uuid = ability_uuid
        self._conditions = self._globals[name].get("conditions", [])

        self._effect_functions = []
        for key in list(self._globals[name].keys()):
            value = self._globals[name][key]
            if LuaManager.is_type(value, 'function'):
                self._effect_functions.append(key)
                self._globals[name].pop(key)
        
        self._globals = {**self._globals[name],
            "conditions": self._conditions
        }
    
    def run(self, function_name, *args):
        if self._lua is None:
            raise RuntimeError("LuaManager not initialized.")
        return self._lua.run_nested(f'{self._name}.{function_name}', *args)