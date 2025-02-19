import lupa, re
from lupa import LuaRuntime, lua_type

from src.events.observer import Emitter
from src.util.constants import ScriptData

class LuaManager(Emitter):
    def __init__(self, globals = {}):
        super().__init__()
        self._lua = LuaRuntime(unpack_returned_tuples=True)

        self._defined_variables = {}
        self._defined_functions = {}

        setup_metatable = '''
        local proxy = {}
        local mt = {
            __index = proxy,
            __newindex = function(t, k, v)
                rawset(proxy, k, v)
                SetGlobalReference(k, v)
            end,
            __pairs = function(t)
                return next, proxy, nil
            end
        }
        setmetatable(_ENV, mt)
        _G = {}
        '''
        self._lua.globals()["SetGlobalReference"] = self.set_reference
        self._lua.execute(setup_metatable)
        self._initial_globals = list(self._lua.globals().keys())
        
        for key, value in globals.items():
            self.set_global(key, value)

    def get(self, key):
        return self._lua.globals()[key]

    def set_global(self, key, value):
        self._lua.globals()[key] = value

    def set_reference(self, key, value):
        if lua_type(value) == 'function':
            self._defined_functions[key] = value
            self.emit('set_reference_function', key, value)
        else:
            self._defined_variables[key] = value
            self.emit('set_reference_variable', key, value)
        self.emit('set_reference', key, value)

    @staticmethod
    def is_type(value, *types):
        for type in types:
            if lua_type(value) == type:
                return True
        return False

    @staticmethod
    def to_python_type(value, strip_functions = False):
        if lua_type(value) == 'table':
            value = LuaManager._recursive_table_convert(value, strip_functions)
        return value

    def get_function_script(self, function):
        info = self._lua.eval("debug.getinfo")(function)
        if info is None or 'source' not in info:
            raise ValueError("Could not retrieve function script.")
        return info['namewhat']

    def execute(self, script):
        return self._lua.execute(script)

    def run(self, function_name, *args):
        function = self._get_function(function_name)
        if function is None:
            raise ValueError("Function not found.")
        args = list(args)
        for i in range(len(args)):
            arg = args[i]
            if type(arg) == list or type(arg) == tuple or type(arg) == dict:
                args[i] = self._lua.table_from(arg)
        result = function(*args)
        if lua_type(result) == 'table':
            return self._recursive_table_convert(result)
        return result

    def run_nested(self, function_pos, *args):
        function = self._lua.eval(function_pos)
        if function is None:
            raise ValueError("Function not found.")
        result = function(*args)
        if lua_type(result) == 'table':
            return self._recursive_table_convert(result)
        return result

    def get_function_header(self, function_name):
        function = self._get_function(function_name)
        if function is None:
            raise ValueError("Function not found.")
        params = []
        while True:
            arg = self._lua.eval("debug.getlocal")(function, len(params) + 1)
            if arg is None:
                break
            params.append(arg)
        return (function_name, tuple(params))

    def _get_function(self, name):
        func = self.get(name)
        if lua_type(func) == 'function':
            return func
        return None
    
    def merge_globals(self, globals):
        # Inserts all global values into the Lua environment, overwriting any existing values
        for key, value in globals.items():
            self.set_global(key, value)

    def append_globals(self, globals):
        # Inserts all global values into the Lua environment, skipping any existing values
        for key, value in globals.items():
            if key not in self._lua.globals():
                self.set_global(key, value)
    
    def get_defined_functions(self):
        return list(self._defined_functions.keys())

    def get_defined_variables(self):
        return list(self._defined_variables.keys())

    def get_full_value(self, variable):
        value = self._lua.eval(variable)
        if lua_type(value) == 'function':
            raise ValueError("Cannot retrieve function value.")
        if lua_type(value) != 'table':
            return value
        else:
            return self._recursive_table_convert(value)

    @staticmethod
    def _recursive_table_convert(table, strip_functions = False):
        converted = {}
        for key, value in dict(table).items():
            if lua_type(value) == 'table':
                converted[key] = LuaManager._recursive_table_convert(value)
            else:
                converted[key] = LuaManager.to_python_type(value)
                if strip_functions and lua_type(value) == 'function':
                    converted.pop(key)
        if list(converted.keys()) == list(range(1, len(converted.keys()) + 1)):
            converted = list(converted.values())
        return converted


    def analyze_for_call(self, script, param_name, property_name):
        return bool(re.compile(f"(\s*|^){param_name}(\.|:){property_name}(\([^\n]*\))?\s*$", re.MULTILINE).search(script))
