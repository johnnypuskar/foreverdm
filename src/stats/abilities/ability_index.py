from src.util.return_status import ReturnStatus
from src.util.constants import EventType, AbilityHeaderControlFlag
from src.stats.abilities.sub_ability import SubAbility
from src.stats.abilities.composite_ability import CompositeAbility
from src.stats.abilities.concentration_tracker import ConcentrationTracker
from src.stats.abilities.ability import Ability
from src.events.observer import Observer, Emitter
from src.stats.wrappers.statblock_ability_wrapper import StatblockAbilityWrapper
from server.backend.database.util.data_storer import DataStorer

class AbilityIndex(Observer, Emitter, DataStorer):
    def __init__(self):
        Observer.__init__(self)
        Emitter.__init__(self)
        DataStorer.__init__(self)
        
        self._abilities = {}
        self._concentration_tracker = ConcentrationTracker()
        self._concentration_tracker.connect(self)
        self._active_use_ability = None
        self._active_use_modifiers = []

        self.map_data_property("_abilities", "abilities")
        self.map_data_property("_concentration_tracker", "concentration_tracker")
        self.map_data_property("_active_use_ability", "active_use_ability")
        self.map_data_property("_active_use_modifiers", "active_use_modifiers")

    def signal(self, event: str, *data):
        if event == EventType.EFFECT_GRANTED_ABILITY:
            # [data] = [ability_name, script]
            effect_ability = SubAbility(data[0], data[1])
            self.add(effect_ability)
        elif event == EventType.EFFECT_REMOVED_ABILITY:
            # [data] = [ability_name]
            self.remove(data[0])
        elif event == EventType.ABILITY_CONCENTRATION_ENDED:
            # [data] = [ability_uuid]
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

    def get_headers(self, valid_use_times = ["action", "bonus_action", "reaction", "free_action"]):
        headers = []
        _SPECIAL_ACTION_KEY = {-1: "action", -2: "bonus_action", -3: "reaction", -4: "free_action"}
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
        return self.get_headers(["action", "bonus_action", "free_action"])
    
    def get_headers_reactions(self):
        return self.get_headers(["reaction", "free_action"])

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

    def _wrap_args(self, *args):
        args = [arg.wrap(StatblockAbilityWrapper) if hasattr(arg, "wrap") else arg for arg in args]
        return args
    
    def run_ability(self, name, statblock, *args, modifier_abilities = []):
        ability_name, control_flags = self._separate_header_control_flags(name)

        # Verify that the ability, as well as any modifier abilities, all exist in the index
        for checked_name in [ability_name] + [modifier[0] for modifier in modifier_abilities]:
            if not self.has_ability(checked_name):
                raise ValueError(f"Ability {checked_name} does not exist in index.")
        if self._active_use_ability is ability_name and len(control_flags) == 0:
            raise ValueError(f"Ability {name} is active use ability, must use control flag to determine continue use or new_use.")
        if len(control_flags) > 0:
            if self._active_use_ability is None:
                raise ValueError(f"No currently active use ability to continue or reset with {control_flags} flag(s).")
            elif AbilityHeaderControlFlag.CONTINUE in control_flags and len(modifier_abilities) > 0:
                raise ValueError(f"Invalid use of modifiers on continued use of ability {ability_name}, modifiers can only be applied at initial or new use.")

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
            return ReturnStatus(False, f"Invalid {name} use. {validation_message}" + ("." if validation_message[-1] != "." else ""))

        # For each modifier ability, check for validation and that it is a valid modifer ability
        for modifier in modifier_abilities:
            modifier_ability = self.get_ability(modifier[0])
            if not modifier_ability.is_modifier:
                return ReturnStatus(False, f"Ability {modifier[0]} is not a modifier ability and cannot be used as a modifier.")
            if not modifier_ability.can_modify(name):
                raise ValueError(f"Ability {modifier[0]} cannot be used to modify {name}.")
            modifier_ability.set_lua(env)
            validated, validation_message = modifier_ability.validate(*modifier[1:])
            if not validated:
                return ReturnStatus(False, f"Invalid {modifier[0]} use. {validation_message}" + ("." if validation_message[-1] != "." else ""))

        # If ability is a new ability, or a new use of the active ability, set it as the active ability and reset it's usage delay.
        if self._active_use_ability != ability_name or (self._active_use_ability == ability_name and AbilityHeaderControlFlag.NEW_USE in control_flags):
            self._active_use_ability = ability_name
            self._active_use_modifiers = modifier_abilities
            self.get_ability(self._active_use_ability).reset_use_delay()
        
        ability.regenerate_uuid()
        if ability._concentration:
            self._concentration_tracker.set_concentration(ability._uuid, ability._duration.timestamp)
        
        if not ability.ready_check():
            return ReturnStatus(False, f"Preparing to use {ability_name}, {ability._use_delay} turns remaining.")
        if self._active_use_ability == ability_name:
            modifier_abilities = self._active_use_modifiers
        self._active_use_ability = None
        self._active_use_modifiers = []

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
            env.connect(ability)
            modifier_success, modifier_message = modifier_ability.run(*self._wrap_args(*modifier[1:]))
            env.disconnect(ability)

            if not modifier_success:
                return ReturnStatus(False, modifier_message)
            # Add result return string to list of return strings.
            use_result_messages.append(modifier_message)
        
        env.connect(ability)
        main_return = env.run("__ability_sequence_main_function__", *self._wrap_args(*args))
        env.disconnect(ability)
        use_result_messages.append(main_return[1])
        return ReturnStatus(main_return[0], " ".join(use_result_messages))

    def __repr__(self):
        return str(list(self._abilities.values()))