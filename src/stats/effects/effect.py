from src.events.observer import Observer
from src.util.constants import ScriptData
from src.util.lua_manager import LuaManager

class Effect(Observer):
    def __init__(self, name, script, duration = -1):
        super().__init__()

        self._name = name
        self._globals = {}
        self._effect_functions = []
        self._lua = None
        self.duration = duration

        SCRIPT_HEADERS = ScriptData.REMOVE_EFFECT + ScriptData.ROLL_RESULT + ScriptData.ADD_VALUE + ScriptData.SET_VALUE + ScriptData.MULTIPLY_VALUE + ScriptData.DURATION + ScriptData.SPEED

        lua = LuaManager()
        lua.execute(SCRIPT_HEADERS)
        lua.connect(self)
        lua.execute(script)

        self._script = SCRIPT_HEADERS + script

        self._conditions = self._globals.get("conditions", [])

    def signal(self, event, *data):
        if event == "set_reference_variable":
            key, value = data
            value = LuaManager.to_python_type(value, strip_functions = False)
            self._globals[key] = value
        elif event == "set_reference_function":
            key, value = data
            self._effect_functions.append(key)

    def initialize(self, globals = {}):
        self._lua = LuaManager()
        self._lua.execute(self._script)
        self._lua.merge_globals(self._globals)
        self._lua.merge_globals(globals)
        return self._lua

    def has_function(self, function_name):
        return function_name in self._effect_functions

    def run(self, function_name, *args):
        if self._lua is None:
            raise RuntimeError("LuaManager not initialized.")
        return self._lua.run(function_name, *args)

    def tick_timer(self):
        if self.duration > 0:
            self.duration -= 1