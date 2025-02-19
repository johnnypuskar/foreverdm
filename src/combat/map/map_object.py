from abc import ABC, abstractmethod
from src.util.lua_manager import LuaManager
from src.events.observer import Observer
from src.util.constants import ScriptData

class MapObject(Observer, ABC):
    def __init__(self, name, script = None):
        self._name = name
        self._script = script
        self._script_functions = []
        self._applied_objects = []

        if script is not None:
            lua = LuaManager()
            lua.execute(self._script)
            self._script_functions = lua.get_defined_functions()
            self._globals = {key: lua.get(key) for key in lua.get_defined_variables()}
        else:
            self._script_functions = []
            self._globals = {}

    def __getattribute__(self, name):
        if name in ['_name', '_script', '_globals', '_script_functions', '_applied_objects', '_get_object_function', 'signal', '_has_object_function', 'apply', 'unapply']:
            return super().__getattribute__(name)
        elif name in self._script_functions:
            return self._get_object_function(name)
        return super().__getattribute__(name)
    
    def _has_object_function(self, function_name):
        return function_name in self._script_functions

    def _get_object_function(self, function_name):
        lua = LuaManager()
        script = self._script
        for obj in self._applied_objects:
            if function_name in obj._script_functions:
                script = obj._script
                break
        lua.execute(script)
        lua.merge_globals(self._globals)
        lua.merge_globals({"object": self})
        lua.connect(self)
        return lua._get_function(function_name)

    def apply(self, other):
        if any(func in self._script_functions for func in other._script_functions):
            if not any([obj._name == other._name for obj in self._applied_objects]):
                self._applied_objects.append(other)
                return True
        return False
    
    def unapply(self, other_name):
        for obj in self._applied_objects:
            if obj._name == other_name:
                self._applied_objects.remove(obj)
                return True
        return False

    def signal(self, event: str, *data):
        if event == 'set_reference_variable':
            key, value = data
            self._globals[key] = value