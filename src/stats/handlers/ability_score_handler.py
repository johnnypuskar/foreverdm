from enum import Enum
from src.util.modifier_values import ModifierValues, ModifierRolls
from foreverdm.src.stats.statblock import Statblock

class AbilityScoreHandler:
    class ABILITIES(Enum):
        STRENGTH = "strength"
        DEXTERITY = "dexterity"
        CONSTITUTION = "constitution"
        INTELLIGENCE = "intelligence"
        WISDOM = "wisdom"
        CHARISMA = "charisma"

    def __init__(self, statblock):
        self._statblock = statblock
    
    @staticmethod
    def is_valid_ability(ability_name):
        """Returns true if the given ability name is valid, false otherwise"""
        return ability_name in [ability.value for ability in AbilityScoreHandler.ABILITIES]

    def get_ability_score(self, ability_name):
        """
        Returns the value of the given ability score after applying any applicable modifiers

        param ability_name: str - the name of the ability score

        return: int - the value of the ability score
        """
        # Check that the ability is valid
        if not self.is_valid_ability(ability_name):
            raise ValueError(f"Invalid ability ({ability_name})")
        
        # Get the modifiers that would apply to the base ability score
        ability_score_modifiers = ModifierValues(self._statblock._effects.get_function_results("modify_stat", self._statblock, ability_name))

        # Apply the modifiers to the base ability score from the Statblock, in order of multiply, add, set
        base_ability_score = self._statblock._ability_scores.get_ability(ability_name).value
        base_ability_score = ability_score_modifiers.process_mult(base_ability_score)
        base_ability_score = ability_score_modifiers.process_add(base_ability_score)
        base_ability_score = ability_score_modifiers.process_set_max(base_ability_score)

        return base_ability_score
    
    def get_ability_modifier(self, ability_name):
        """Returns the modifier for the given ability score"""
        return self.get_ability_score(ability_name) // 2 - 5
    
    def _prepare_check(self, ability_name, target = None, additional_modifier_parameters = []):
        """
        Returns the modifiers and bonus for a check based on the given ability score and additional parameters for special types of rolls

        param ability_name: str - the name of the ability score to use for the check
        param target (optional): Targettable - the target of the check
        param additional_modifier_parameters (optional): list[tuple] - additional parameters to pass to the _prepare_bonus method
            [0]: str - the name of the effect function to call on the self Statblock
            [1]: str - the argument to pass to the effect function
            [2]: str - the name of the effect function to call on the target Statblock
            [3]: str (optional) - the proficiency type to check for proficiency, defaults to using the effect function argument
        
        return: ModifierRolls, int - the modifiers and bonus for the check
        """
        # Check that the ability is valid
        if not self.is_valid_ability(ability_name):
            raise ValueError(f"Invalid ability ({ability_name})")

        modifier_parameters = [["make_ability_check", ability_name, "receive_ability_check"]] + additional_modifier_parameters

        # Get the modifiers and bonus for the ability check to starter values
        modifiers = ModifierRolls()
        modifiers.bonus = self.get_ability_modifier(ability_name)

        # Merge and add the modifiers and bonuses from the additional parameters
        for parameter in modifier_parameters:
            # Define parameters as variables for readability
            self_effect_function = parameter[0]
            argument = parameter[1]
            other_effect_function = parameter[2]
            
            # Get the modifiers that would apply to the check
            additional_modifiers = ModifierRolls(self._statblock._effects.get_function_results(self_effect_function, self._statblock, argument, target))
            
            # If target is not None, try applying the target's modifiers to the check
            if target is not None:
                try:
                    target_modifiers = ModifierRolls(target._effects.get_function_results(other_effect_function, target, argument, self._statblock))
                    additional_modifiers.merge(target_modifiers)
                except:
                    pass
            
            # Add the bonus from the additional parameter to the total bonus
            additional_modifiers.bonus += self._prepare_bonus(parameter)

            # Merge the additional modifiers with the existing modifiers
            modifiers.merge(additional_modifiers)
        
        return modifiers

    def _prepare_bonus(self, _):
        """Returns the bonus added based on the given parameter, overwritten in subclasses"""
        return 0