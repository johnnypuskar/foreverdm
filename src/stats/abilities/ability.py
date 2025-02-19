import uuid
from src.util.time import UseTime, Timer
from src.util.lua_manager import LuaManager
from src.util.constants import ScriptData
from src.events.observer import Observer

class Ability(Observer):
    def __init__(self, name, script):
        # Only allow alphanumerics and underscores in ability names
        if not all(c.isalnum() or c in ["_"] for c in name):
            raise ValueError("Ability name can only include alphanumerics and underscores.")
        super().__init__()

        self._name = name
        self._function_name = None
        self._globals = {}
        self._lua = None
        self._uuid = None
        self.regenerate_uuid()

        SCRIPT_HEADERS = ScriptData.USE_TIME + ScriptData.DURATION + ScriptData.SPEED + ScriptData.ABILITY_VALIDATE
        
        lua = LuaManager()
        lua.execute(SCRIPT_HEADERS)
        lua.connect(self)
        lua.execute(script)

        self._script = SCRIPT_HEADERS + script

        use_time = self._globals.get("use_time", {'unit': 'undefined', 'value': -1})
        if not isinstance(self, ReactionAbility) and use_time['unit'] == 'reaction':
            self.__class__ = ReactionAbility
            self.__init__(name, script)
            return

        self._modifier_values = self._globals.get("can_modify", [])
        self._use_time = UseTime.from_table(use_time)

        self._concentration = self._globals.get("spell_concentration", False)
        self._duration = Timer.from_table(self._globals.get("spell_duration", {'unit': 'round', 'value': 1}))

        self.reset_use_delay()

    def signal(self, event, *data):
        if event == "set_reference":
            key, value = data
            if LuaManager.is_type(value, 'function'):
                if key in ['run', 'modify']:
                    if self._function_name is None:
                        self._function_name = key
                    elif key != self._function_name:
                        raise ValueError("Cannot define run() and modify() functions in the same Ability script.")
            else:
                value = LuaManager.to_python_type(value, strip_functions = False)
                self._globals[key] = value

    @property
    def header(self):
        lua = LuaManager()
        lua.execute(self._script)
        return (self._name, lua.get_function_header(self._function_name)[1])

    @property
    def is_modifier(self):
        return len(self._modifier_values) > 0 and self._function_name == "modify"

    def regenerate_uuid(self):
        self._uuid = str(uuid.uuid4().hex)

    def can_modify(self, ability_name):
        if not self.is_modifier:
            return False
        if "." in ability_name:
            ability_names = set(ability_name.split(".", 1) + ability_name.rsplit(".", 1))
            for name in ability_names:
                if self.can_modify(name):
                    return True
        return ability_name in self._modifier_values

    @property
    def is_attacking(self):
        lua = LuaManager()
        return lua.analyze_for_call(self._script, "target", "take_damage")

    def reset_use_delay(self):
        if self._use_time.is_special:
            self._use_delay = 0
        else:
            self._use_delay = self._use_time.minutes * 10

    def ready_check(self):
        if self._use_delay > 1:
            self._use_delay -= 1
            return False
        self._use_delay = 0
        return True

    def set_lua(self, lua):
        self._lua = lua
        self._lua.execute(self._script)

    def set_function_name(self, function_name):
        self._function_name = function_name

    def initialize(self, globals):
        self._lua = LuaManager()
        self._lua.execute(self._script)
        self._lua.merge_globals(self._globals)
        self._lua.merge_globals(globals)
        return self._lua

    def validate(self, *args):
        if self._lua is None:
            raise RuntimeError("LuaManager not initialized.")
        validated, validation_message = self._lua.run("validate", *args)
        if not validated:
            return (False, validation_message)
        return (True, None)

    def run(self, *args):
        if self._lua is None:
            raise RuntimeError("LuaManager not initialized.")
        return self._lua.run(self._function_name, *args)

class ReactionAbility(Ability):
    def __init__(self, name, script):
        super().__init__(name, script)
        
        lua = LuaManager()
        lua.execute(self._script)
        if "reaction_trigger" not in lua.get_defined_variables():
            raise ValueError("Reaction ability must define a reaction_trigger variable.")
        self._reaction_trigger = lua.get("reaction_trigger")