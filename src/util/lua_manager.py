import lupa, re
from lupa import LuaRuntime, lua_type

class LuaManager:
    def __init__(self, globals = {}):
        self._lua = LuaRuntime(unpack_returned_tuples=True)
        self._initial_globals = list(self._lua.globals().keys())
        for key, value in globals.items():
            self._lua.globals()[key] = value

    @property
    def globals(self):
        return dict(self._lua.globals())

    @staticmethod
    def is_type(value, type):
        return lua_type(value) == type

    def get_function_script(self, function):
        info = self._lua.eval("debug.getinfo")(function)
        if info is None or 'source' not in info:
            raise ValueError("Could not retrieve function script.")
        print(list(info.keys()))
        return info['namewhat']

    def execute(self, script):
        self._lua.execute(script)

    def run(self, function_name, *args):
        function = self._get_function(function_name)
        if function is None:
            raise ValueError("Function not found.")
        result = function(*args)
        if lua_type(result) == 'table':
            return dict(result)
        return result

    def run_nested(self, function_pos, *args):
        function = self._lua.eval(function_pos)
        if function is None:
            raise ValueError("Function not found.")
        result = function(*args)
        if lua_type(result) == 'table':
            return dict(result)
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
        for key, value in self._lua.globals().items():
            if lua_type(value) == 'function' and key == name:
                return value
        return None
    
    def merge_globals(self, globals):
        # Inserts all global values into the Lua environment, overwriting any existing values
        for key, value in globals.items():
            self._lua.globals()[key] = value

    def append_globals(self, globals):
        # Inserts all global values into the Lua environment, skipping any existing values
        for key, value in globals.items():
            if key not in self._lua.globals():
                self._lua.globals()[key] = value
    
    def get_defined_functions(self):
        function_names = []
        for key, value in self._lua.globals().items():
            if key not in self._initial_globals and lua_type(value) == 'function':
                function_names.append(key)
        return function_names
    
    def get_defined_globals(self):
        global_names = []
        for key in self._lua.globals().keys():
            if key in self._initial_globals:
                continue
            global_names.append(key)
        return global_names

    def get_defined_variables(self):
        return [item for item in self.get_defined_globals() if item not in self.get_defined_functions()]
    
    def analyze_for_call(self, script, param_name, property_name):
        return bool(re.compile(f"(\s*|^){param_name}(\.|:){property_name}(\([^\n]*\))?\s*$", re.MULTILINE).search(script))
