from abc import ABC, abstractmethod
from src.util.lua_manager import LuaManager
from src.events.observer import Observer
from server.backend.database.util.data_storer import DataStorer

class MapObject(Observer, ABC, DataStorer):
    def __init__(self, name, script = None):
        DataStorer.__init__(self)
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
        
        self.map_data_property("_name", "name")
        self.map_data_property("_script", "script", export_falsy = False)
        self.map_data_property("_script_functions", "script_functions", export_falsy = False)
        self.map_data_property("_applied_objects", "applied_objects", export_falsy = False)

    def __getattr__(self, name):
        if name in self._script_functions:
            return self._get_object_function(name)
        return super().__getattr__(name)
    
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