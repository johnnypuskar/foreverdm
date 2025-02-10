from src.util.return_status import ReturnStatus

class AbilityHandler:
    def __init__(self, statblock):
        self._statblock = statblock
        # List of queued modifier abilities, formatted as [name, use_time, *args]
        self._modifier_ability_calls = []
    
    def add_ability(self, ability):
        """Adds an ability to the Statblock's abilities."""
        self._statblock._abilities.add(ability)
    
    def remove_ability(self, ability_name):
        """Removes an ability from the Statblock's abilities by name."""
        self._statblock._abilities.remove(ability_name)
    
    def use_ability(self, ability_name, *args):
        """
        Uses the ability with the given name, passing any additional arguments to the ability's script.
        Modifier abilities will be stored by the handlers, and passed alongside the next non-modifier ability call.

        param ability_name: str - the name of the ability to use
        param *args: any - any additional arguments to pass to the ability's script

        return: ReturnStatus
        """
        ability = self._statblock._abilities.get_ability(ability_name)

        # Check if any effects prevent the ability from being used through preventing action types.
        if ability._use_time.is_action() or ability._use_time.is_bonus_action():
            if not all(self._statblock._effects.get_function_results("allow_actions", self, ability)):
                return ReturnStatus(False, f"Unable to take {str(ability._use_time)}")
        elif ability._use_time.is_reaction():
            if not all(self._statblock._effects.get_function_results("allow_reactions", self, ability)):
                return ReturnStatus(False, f"Unable to take {str(ability._use_time)}")
        
        # If the ability is a modifier, add it to the list of modifier abilities to call when the next run ability is used.
        if ability.is_modifier:
            self._modifier_ability_calls.append(
                (ability_name, ability._use_time, *args)
            )
            return ReturnStatus(True, f"Prepared use of {ability_name}.")
        
        # Create copy of turn resources to check if the ability and all modifiers together can be used before removing any resources.
        turn_resources = self._statblock._turn_resources.make_copy()
        for modifier_name, use_time, *_ in self._modifier_ability_calls:
            if not turn_resources.use_from_use_time(use_time):
                self._modifier_ability_calls.clear()
                if not use_time.is_special:
                    return ReturnStatus(False, f"No action remaining to use {modifier_name}.")
                else:
                    return ReturnStatus(False, f"No {str(use_time)} remaining to use {modifier_name}.")
        
        if not turn_resources.use_from_use_time(ability._use_time):
            message_end = "." if len(self._modifier_ability_calls) == 0 and turn_resources != self._statblock._turn_resources else " after modifiers."
            self._modifier_ability_calls.clear()
            if not ability._use_time.is_special:
                return ReturnStatus(False, f"No action remaining to use {ability_name}{message_end}")
            else:
                return ReturnStatus(False, f"No {str(ability._use_time)} remaining to use {ability_name}{message_end}")

        # Turn resources has enough actions to use the ability and all modifiers, so run the ability and remove the turn resources.
        self._statblock._turn_resources.use_from_use_time(ability._use_time)
        for _, modifier_use_time, *_ in self._modifier_ability_calls:
            self._statblock._turn_resources.use_from_use_time(modifier_use_time)
            
        succeeded, message = self._statblock._abilities.run_ability(ability_name, self._statblock, *args, modifier_calls = [tuple([mod[0]]) + mod[2:] for mod in self._modifier_ability_calls])
        self._modifier_ability_calls.clear()
        return ReturnStatus(succeeded, message)

        
