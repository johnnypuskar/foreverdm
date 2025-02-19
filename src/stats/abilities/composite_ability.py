from src.stats.abilities.ability import Ability
from src.util.lua_manager import LuaManager

class CompositeAbility(Ability):
    def __init__(self, name, script):
        super().__init__(name, script)
        self._sub_abilities = {}
    
    @property
    def header(self):
        sub_ability_headers = []
        for sub_ability in self._sub_abilities.values():
            header = list(sub_ability.header)
            header[0] = f"{self._name}.{header[0]}"
            sub_ability_headers.append(tuple(header))
        return tuple(sub_ability_headers)
            
    def add(self, sub_ability: Ability):
        if sub_ability._name in self._sub_abilities:
            raise ValueError(f"Subability {sub_ability._name} already exists in index.")
        for key, value in self._globals.items():
            if key not in sub_ability._globals:
                sub_ability._globals[key] = value
        self._sub_abilities[sub_ability._name] = sub_ability
    
    def remove(self, name):
        if name not in self._sub_abilities:
            raise ValueError(f"Subability {name} does not exist in index.")
        del self._sub_abilities[name]
    
    def get_all_keys(self):
        keys = []
        for key in self._sub_abilities.keys():
            if type(self._sub_abilities[key]) is CompositeAbility:
                keys.extend([f"{key}.{sub_key}" for sub_key in self._sub_abilities[key].get_all_keys()])
            else:
                keys.append(key)
        return keys

    def get_sub_ability(self, name):
        name_split = name.split(".")
        if len(name_split) == 1:
            if name not in self._sub_abilities:
                raise ValueError(f"Subability {name} does not exist in index.")
            return self._sub_abilities[name]
        else:
            if name_split[0] not in self._sub_abilities:
                raise ValueError(f"Subability {name_split[0]} not found in index.")
            if type(self._sub_abilities[name_split[0]]) is not CompositeAbility:
                raise ValueError(f"Subability {name_split[0]} is not a composite ability.")
            
            return self._sub_abilities[name_split[0]].get_sub_ability(".".join(name_split[1:]))

    @property
    def header(self):
        sub_ability_headers = []
        for sub_ability in self._sub_abilities.values():
            header = list(sub_ability.header)
            header[0] = f"{self._name}.{header[0]}"
            sub_ability_headers.append(tuple(header))
        return tuple(sub_ability_headers)
    
    def initialize(self, sub_ability_name, globals):
        self._lua = LuaManager(self._globals)
        self._lua.merge_globals(globals)
        self._sub_abilities[sub_ability_name].set_lua(self._lua)

        return self._lua

    def run(self, sub_ability_name, *args):
        if self._lua is None:
            raise RuntimeError("LuaManager not initialized.")
        return self._sub_abilities[sub_ability_name].run(*args)