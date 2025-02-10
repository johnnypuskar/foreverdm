from enum import Enum
import uuid
from src.util.time import UseTime, Timer
from src.util.lua_manager import LuaManager
from src.util.constants import EventType, ScriptData, AbilityHeaderControlFlag
from src.events.observer import Observer, Emitter

class Ability(Observer):
    def __init__(self, name, script, function_name = "run", globals = {}):
        if not all(c.isalnum() or c in ["_"] for c in name):
            raise ValueError("Ability name can only include alphanumerics and underscores.")
        super().__init__()
        self._name = name
        self._function_name = function_name
        self._globals = {key: StatblockAbilityWrapper.create_wrapper(value, self) for key, value in globals.items()}
        self._lua = None
        self._uuid = None
        self.regenerate_uuid()

        self._script = ScriptData.USE_TIME + ScriptData.DURATION + ScriptData.SPEED + ScriptData.ABILITY_VALIDATE + script

        lua = LuaManager()
        lua.execute("use_time = {unit = 'undefined', value = -1}")
        lua.execute("can_modify = {}")
        lua.execute("spell_concentration = false")
        lua.execute("spell_duration = {unit = 'round', value = 1}")
        lua.execute(self._script)

        use_time = dict(lua.globals['use_time'])
        if not isinstance(self, ReactionAbility) and use_time['unit'] == 'reaction':
            self.__class__ = ReactionAbility
            self.__init__(name, script, function_name, globals)
            return

        self._is_modifier = len(list(lua.globals['can_modify'])) > 0
        self._use_time = UseTime.from_table(use_time)

        self._concentration = lua.globals['spell_concentration']
        self._duration = Timer.from_table(dict(lua.globals['spell_duration']))

        self.reset_use_delay()

    def signal(self, event, *data):
        if event == "set_reference":
            key, value = data
            self._globals[key] = StatblockAbilityWrapper.create_wrapper(value, self)

    @property
    def header(self):
        lua = LuaManager()
        lua.execute(self._script)
        return (self._name, lua.get_function_header(self._function_name)[1])

    @property
    def is_modifier(self):
        return self._is_modifier

    def regenerate_uuid(self):
        self._uuid = str(uuid.uuid4().hex)

    def can_modify(self, ability_name):
        if not self._is_modifier:
            return False
        if "." in ability_name:
            ability_names = ability_name.split(".")
            for name in ability_names:
                if self.can_modify(name):
                    return True
            return False
        lua = LuaManager()
        lua.execute(self._script)
        return ability_name in dict(lua.globals['can_modify']).values()

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
        self._lua = LuaManager(self._globals)
        self._lua.connect(self)
        self._lua.merge_globals(globals)
        self._lua.execute(self._script)
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
        validated, validation_message = self.validate(*args)
        if not validated:
            return (False, validation_message)
        return self._lua.run(self._function_name, *args)

    def __repr__(self):
        return str(self.header)

class ReactionAbility(Ability):
    def __init__(self, name, script, function_name = "run", globals = {}):
        super().__init__(name, script, function_name, globals)
        
        lua = LuaManager()
        lua.execute(self._script)
        if "reaction_trigger" not in lua.get_defined_variables():
            raise ValueError("Reaction ability must define a reaction_trigger variable.")
        self._reaction_trigger = lua.globals["reaction_trigger"]

class CompositeAbility(Ability):
    def __init__(self, name, script, function_name = "run", globals = {}):
        super().__init__(name, script, function_name, globals)
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

class SubAbility(Ability):
    def __init__(self, name, script, function_name = "run", globals = {}):
        self._name = name
        self._function_name = function_name
        self._globals = {key: StatblockAbilityWrapper.create_wrapper(value, self) for key, value in globals.items()}
        self._lua = None
        self._uuid = None
        self.regenerate_uuid()

        self._script = ScriptData.USE_TIME + ScriptData.SPEED + script
        self._script += f'''
        if {self._name}.validate == nil then
            {self._name}.validate = function(p) return true, nil end
        end
        '''

        lua = LuaManager()
        lua.execute(self._script)
        
        ability_dict = dict(lua.globals[name])
        self._concentration = "spell_concentration" in ability_dict.keys() and ability_dict['spell_concentration']
        self._duration = "spell_duration" in ability_dict.keys() and Timer.from_table(dict(ability_dict['spell_duration']))
        self._is_modifier = "can_modify" in ability_dict.keys() and len(list(ability_dict['can_modify'])) > 0
        self._use_time = UseTime.from_table(dict(ability_dict['use_time']))

        self.reset_use_delay()

        for key, value in lua.get_full_value(f"{name}").items():
            if key not in self._globals and value is not None:
                self._globals[key] = value

    def initialize(self, globals):
        super().initialize(globals)
        self._lua.merge_globals(dict(self._lua.globals[self._name]))

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

class AbilityIndex(Observer, Emitter):
    def __init__(self):
        super().__init__()
        self._abilities = {}
        self._concentration_tracker = ConcentrationTracker()
        self._concentration_tracker.connect(self)
        self._active_use_ability = None

    def signal(self, event: str, *data):
        if event == EventType.EFFECT_GRANTED_ABILITY:
            # [data] = [ability_name, script, function_name = "run"]
            effect_ability = SubAbility(data[0], data[1], data[2])
            self.add(effect_ability)
        elif event == EventType.EFFECT_REMOVED_ABILITY:
            # [data] = [ability_name]
            self.remove(data[0])
        elif event == EventType.ABILITY_CONCENTRATION_ENDED:
            # [data] = [ability_use_hash]
            self.emit(EventType.ABILITY_CONCENTRATION_ENDED, *data)

    def add(self, ability: Ability):
        if ability._name in self._abilities:
            raise ValueError("Ability already exists in index.")
        self._abilities[ability._name] = ability
    
    def remove(self, name):
        if name not in self._abilities:
            raise ValueError("Ability does not exist in index.")
        del self._abilities[name]
    
    def _separate_header_control_flags(self, name):
        control_flags = []
        ability_name = []
        name_split = name.split(".")
        for name_segment in name_split:
            if name_segment[0] == "^":
                if name_segment == "^continue":
                    control_flags.append(AbilityHeaderControlFlag.CONTINUE)
                elif name_segment == "^new_use":
                    control_flags.append(AbilityHeaderControlFlag.NEW_USE)
            else:
                ability_name.append(name_segment)
        return (".".join(ability_name), control_flags)

    def get_headers(self, valid_use_times = ["action", "bonus_action", "reaction"]):
        headers = []
        _SPECIAL_ACTION_KEY = {-1: "action", -2: "bonus_action", -3: "reaction"}
        for ability in self._abilities.values():
            if type(ability) is CompositeAbility:
                for new_header in ability.header:
                    sub_ability = ability.get_sub_ability(".".join(new_header[0].split(".")[1:]))
                    if not ((not sub_ability._use_time.is_special and "action" in valid_use_times) or (sub_ability._use_time.is_special and _SPECIAL_ACTION_KEY[sub_ability._use_time.minutes] in valid_use_times)):
                        continue
                    if new_header[0] == self._active_use_ability:
                        headers.append((f"^continue.{new_header[0]}", new_header[1]))
                        headers.append((f"^new_use.{new_header[0]}", new_header[1]))
                    else:
                        headers.append(new_header)
            else:
                if not ((not ability._use_time.is_special and "action" in valid_use_times) or (ability._use_time.is_special and _SPECIAL_ACTION_KEY[ability._use_time.minutes] in valid_use_times)):
                    continue
                if ability.header[0] == self._active_use_ability:
                    headers.append((f"^continue.{ability.header[0]}", ability.header[1]))
                    headers.append((f"^new_use.{ability.header[0]}", ability.header[1]))
                else:
                    headers.append(ability.header)
        return headers

    def get_headers_turn_actions(self):
        return self.get_headers(["action", "bonus_action"])
    
    def get_headers_reactions(self):
        return self.get_headers(["reaction"])

    def get_headers_reactions_to_event(self, event):
        headers = []
        for header in self.get_headers_reactions():
            ability = self.get_ability(header[0])
            if ability._reaction_trigger == event:
                headers.append(header)
        return headers

    def get_all_keys(self):
        keys = []
        for key in self._abilities.keys():
            if type(self._abilities[key]) is CompositeAbility:
                keys.extend([f"{key}.{sub_key}" for sub_key in self._abilities[key].get_all_keys()])
            else:
                keys.append(key)
        return keys
    
    def get_ability(self, name):
        name, _ = self._separate_header_control_flags(name)
        name_split = name.split(".")
        if len(name_split) == 1:
            if name not in self._abilities:
                raise ValueError(f"Ablity {name} does not exist in index.")
            return self._abilities[name]
        else:
            if name_split[0] not in self._abilities:
                raise ValueError(f"Ablity {name} does not exist in index ({name_split[0]} not found).")
            if type(self._abilities[name_split[0]]) is not CompositeAbility:
                raise ValueError(f"Ability {name_split[0]} is not a composite ability.")
            
            return self._abilities[name_split[0]].get_sub_ability(".".join(name_split[1:]))

    def has_ability(self, name):
        return name in self.get_all_keys()

    def tick_timers(self):
        self._concentration_tracker.tick_timer()

    def break_concentration(self):
        self._concentration_tracker.end_concentration()

    def run_ability(self, name, statblock, *args, modifier_abilities = []):
        ability_name, control_flags = self._separate_header_control_flags(name)

        # Verify that the ability, as well as any modifier abilities, all exist in the index
        for name in [ability_name] + [modifier[0] for modifier in modifier_abilities]:
            if not self.has_ability(name):
                raise ValueError(f"Ability {name} does not exist in index.")
        if self._active_use_ability is ability_name and len(control_flags) == 0:
            raise ValueError(f"Ability {name} is active use ability, must use control flag to determine continue use or new_use.")

        # TODO: Verify that you want to override the active use ability

        # TODO: Verify that you want to break existing concentration

        ability = self.get_ability(ability_name)

        if ability.is_modifier:
            raise ValueError(f"Ability {ability_name} is a modifier ability and cannot be run directly.")
        
        # Create the runtime environment for the ability
        env = ability.initialize({"statblock": StatblockAbilityWrapper(statblock, ability)})

        # Check for ability use validation, and if invalid, return false with the validation error message.
        validated, validation_message = ability.validate(*args)
        if not validated:
            return (False, f"Invalid {name} use. {validation_message}" + ("." if validation_message[-1] != "." else ""))

        # For each modifier ability, check for validation and that it is a valid modifer ability
        for modifier in modifier_abilities:
            modifier_ability = self.get_ability(modifier[0])
            if not modifier_ability.is_modifier:
                return (False, f"Ability {modifier[0]} is not a modifier ability and cannot be used as a modifier.")
            if not modifier.can_modify(name):
                raise ValueError(f"Ability {modifier[0]} cannot be used to modify {name}.")
            modifier_ability.set_lua(env)
            validated, validation_message = modifier_ability.validate(*modifier[1:])
            if not validated:
                return (False, f"Invalid {modifier[0]} use. {validation_message}" + ("." if validation_message[-1] != "." else ""))

        # If ability is a new ability, or a new use of the active ability, set it as the active ability and reset it's usage delay.
        if self._active_use_ability != ability_name or (self._active_use_ability == ability_name and AbilityHeaderControlFlag.NEW_USE in control_flags):
            self._active_use_ability = ability_name
            self.get_ability(self._active_use_ability).reset_use_delay()
        
        ability.regenerate_uuid()
        if ability._concentration:
            self._concentration_tracker.set_concentration(ability, ability._duration.timestamp)
        
        if not ability.ready_check():
            return (False, f"Preparing to use {ability_name}, {ability._use_delay} turns remaining.")
        self._active_use_ability = None

        use_result_messages = []

        # Store ability function in a variable for later reference to avoid overwriting the main ability function with a modifider that has the same name
        override_protection_script = f'''
            __ability_sequence_main_function__ = {ability._function_name}
        '''
        env.execute(override_protection_script)

        for modifier in modifier_abilities:
            modifier_ability = self.get_ability(modifier[0])
            modifier_ability.set_lua(env)
            
            # Fix: Call run() on the ability object, not the tuple
            modifier_result = modifier_ability.run(*modifier[1:])

            if not modifier_result[0]:
                return modifier_result
            # Add result return string to list of return strings.
            use_result_messages.append(modifier_result[1])
        
        main_return = env.run("__ability_sequence_main_function__", *args)
        use_result_messages.append(main_return[1])
        return (main_return[0], " ".join(use_result_messages))
            

    def run(self, name, statblock, *args):
        ability_name, control_flags = self._separate_header_control_flags(name)

        if not self.has_ability(ability_name):
            raise ValueError(f"Ability {ability_name} does not exist in index.")
        if self._active_use_ability is ability_name and len(control_flags) == 0:
            raise ValueError(f"Ability {name} is active use ability, must use control flag to determine continue use or new_use.")

        # TODO: Verify that you want to override the active use ability

        # TODO: Verify that you want to break existing concentration
        
        ability = self.get_ability(ability_name)

        if ability.is_modifier:
            raise ValueError(f"Ability {ability_name} is a modifier ability and cannot be run as a main ability")

        if self._active_use_ability != ability_name or (self._active_use_ability == ability_name and AbilityHeaderControlFlag.NEW_USE in control_flags):
            self._active_use_ability = ability_name
            self.get_ability(self._active_use_ability).reset_use_delay()
        
        ability.initialize({"statblock": StatblockAbilityWrapper(statblock, ability)})
        
        validated, validation_message = ability.validate(*args)
        if not validated:
            self._active_use_ability = None
            ability.reset_use_delay()
            return (False, validation_message)

        if not ability.ready_check():
            return (False, f"Preparing to use {ability_name}, {ability._use_delay} turns remaining.")
        self._active_use_ability = None

        ability.regenerate_uuid()
        if ability._concentration:
            self._concentration_tracker.set_concentration(ability, ability._duration.timestamp)

        return ability.run(*args)

    def run_sequence(self, name, statblock, modifiers, *args):
        # Check if main run ability exists in index
        ability_name, control_flags = self._separate_header_control_flags(name)

        if not self.has_ability(ability_name):
            raise ValueError(f"Ability {ability_name} does not exist in index.")
        if self._active_use_ability is ability_name and len(control_flags) == 0:
            raise ValueError(f"Ability {ability_name} is active use ability, must use control flag to determine continue use or new_use.")

        # TODO: Verify that you want to override the active use ability

        # Initialize the main run ability
        ability = self.get_ability(ability_name)

        # Check if main ability is a modifier ability, and throw an error if so
        if ability.is_modifier:
            raise ValueError(f"Ability {ability_name} is a modifier ability and cannot be run as a main ability.")

        # TODO: Verify that you want to override the active use ability
        
        # TODO: Verify that you want to break existing concentration

        if self._active_use_ability != ability_name or (self._active_use_ability == ability_name and AbilityHeaderControlFlag.NEW_USE in control_flags):
            self._active_use_ability = ability_name
            self.get_ability(self._active_use_ability).reset_use_delay()
        
        env = ability.initialize({"statblock": StatblockAbilityWrapper(statblock, ability)})
        
        validated, validation_message = ability.validate(*args)
        if not validated:
            self._active_use_ability = None
            ability.reset_use_delay()
            return (False, validation_message)

        ability.regenerate_uuid()
        if ability._concentration:
            self._concentration_tracker.set_concentration(ability, ability._duration.timestamp)

        if not ability.ready_check():
            return (False, f"Preparing to use {ability_name}, {ability._use_delay} turns remaining.")
        self._active_use_ability = None
        
        # Store ability function in a variable for later reference to avoid overwriting the main ability function with a modifider that has the same name
        override_protection_script = f'''
            _sequence_ability_function = {ability._function_name}
        '''
        env.execute(override_protection_script)

        return_strings = []

        # Run each modifier ability on the main ability runtime
        for modifier_params in modifiers:
            key = modifier_params[0]
            # Check it exists and is a modify ability before running
            if key not in self.get_all_keys():
                raise ValueError(f"Ability {key} does not exist in index.")
            
            # Initialize the modifier ability with the main ability runtime
            modifier = self.get_ability(key)

            # Check if the modifier ability is a modifier ability
            if not modifier.is_modifier:
                raise ValueError(f"Ability {key} is not a modifier ability and cannot be run as a modifier.")
            
            # Check if the modifier ability can modify the provided main ability
            if not modifier.can_modify(name):
                raise ValueError(f"Ability {key} cannot be used to modify {name}.")

            modifier.set_lua(env)

            # Run the modifier ability using its defined parameters from the modifiers dict
            result = modifier.run(*modifier_params[1:])

            # If modifier returns false, quit out of the sequence
            if not result[0]:
                return result

            # Add result return string to list of return strings.
            return_strings.append(result[1])
        
        # Run the main ability with the modified runtime
        main_return = env.run("_sequence_ability_function", *args)
        return_strings.append(main_return[1])
        return (main_return[0], " ".join(return_strings))

    def __repr__(self):
        return str(list(self._abilities.values()))

class ConcentrationTracker(Emitter):
    def __init__(self):
        super().__init__()
        self._ability = None
        self._remaining_ticks = 0
    
    @property
    def concentrating(self):
        return self._ability_use_uuid is not None

    def set_concentration(self, ability, duration):
        if self._ability is not None:
            self.end_concentration()
        self._ability = ability
        self._remaining_ticks = duration
    
    def end_concentration(self):
        if self._ability is not None:
            self.emit(EventType.ABILITY_CONCENTRATION_ENDED, self._ability._uuid)
            self._ability = None
            self._remaining_ticks = 0

    def tick_timer(self):
        if self._remaining_ticks > 0:
            self._remaining_ticks -= 1
            if self._remaining_ticks <= 0:
                self.end_concentration()


class StatblockAbilityWrapper:
    def __init__(self, statblock, ability):
        self._statblock = statblock
        self._ability = ability
    
    @staticmethod
    def create_wrapper(obj, effect):
        if isinstance(obj, (int, float, str, bool, type(None), dict)):
            return obj
        return StatblockAbilityWrapper(obj, effect)

    def __getitem__(self, key):
        return getattr(self, key)
        
    def __getattr__(self, name):
        return getattr(self._statblock, name)

    def add_effect(self, effect_name, duration, globals = {}):
        self._statblock._abilities.emit(EventType.ABILITY_APPLIED_EFFECT, effect_name, self._ability._script, duration, globals, self._ability._uuid)
    
    def remove_effect(self, effect_name):
        self._statblock._abilities.emit(EventType.ABILITY_REMOVED_EFFECT, effect_name)

    def spell_attack_roll(self, target, damage_string):
        if "spellcasting_ability" not in self._ability._lua.get_defined_variables():
            raise ValueError(f"Spellcasting ability not defined in Ability {self._ability._name}.")
        return self._statblock.ability_attack_roll(target, self._ability._lua.globals["spellcasting_ability"], damage_string)