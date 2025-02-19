from src.stats.abilities.ability import Ability
from src.util.lua_manager import LuaManager
from src.util.time import UseTime

class SubAbility(Ability):
    def __init__(self, name, script):
        script += f"if {name}.validate == nil then {name}.validate = function() return true, nil end end\n"
        super().__init__(name, script)
        if self._globals.get(name, None) is None or type(self._globals[name]) != dict:
            raise ValueError(f"SubAbility table {name} not defined in script.")
        
        self._modifier_values = self._globals[name].get("can_modify", [])
        self._use_time = UseTime.from_table(self._globals[name].get("use_time", {'unit': 'undefined', 'value': -1}))
        self._concentration = self._globals[name].get("spell_concentration", False)
        self._duration = self._globals[name].get("spell_duration", {'unit': 'round', 'value': 1})

        self._function_name = None
        for key in list(self._globals[name].keys()):
            value = self._globals[name][key]
            if LuaManager.is_type(value, 'function'):
                if key in ['run', 'modify']:
                    if self._function_name is None:
                        self._function_name = f"{self._name}.{key}"
                    elif key != self._function_name:
                        raise ValueError("Cannot define run() and modify() functions in the same SubAbility table.")
                self._globals[name].pop(key)
        
        self._globals = self._globals[name]

        self._globals = {**self._globals, 
            "can_modify": self._modifier_values,
            "use_time": self._use_time,
            "spell_concentration": self._concentration,
            "spell_duration": self._duration
        }

    def validate(self, *args):
        if self._lua is None:
            raise RuntimeError("LuaManager not initialized.")
        validated, validation_message = self._lua.run_nested(f"{self._name}.validate", *args)
        if not validated:
            return (False, validation_message)
        return (True, None)

    def run(self, *args):
        if self._lua is None:
            raise RuntimeError("LuaManager not initialized.")
        validated, validation_message = self.validate(*args)
        if not validated:
            return (False, validation_message)
        return self._lua.run_nested(f"{self._name}.{self._function_name}", *args)