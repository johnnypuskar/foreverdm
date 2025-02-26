from src.stats.handlers.skill_handler import SkillHandler
from src.stats.proficiencies import Proficiencies
from src.util.constants import EventType
from src.events.event_context import RollEventContext, RollResultEventContext
from src.util.return_status import ReturnStatus

class AbilityRollHandler(SkillHandler):
    def __init__(self, statblock, dice_roller = None):
        super().__init__(statblock)
        self._dice_roller = statblock._dice_roller if dice_roller is None else dice_roller
    
    def ability_check(self, dc, ability_name, target = None):
        """
        Makes an ability check roll against the given DC and target

        param dc: int - the difficulty class of the check
        param ability_name: str - the name of the ability to check
        param target (optional): Targettable - the target of the check

        return: ReturnStatus - the result of the ability check
        """
        # Get the modifiers for the ability check and the base bonus to add to the d20 roll
        modifiers = self._prepare_check(ability_name, target)

        # Call the handle_d20_roll method to handle the roll and return the result
        return self._handle_d20_roll(
            modifiers, dc, 
            [EventType.TRIGGER_ABILITY_CHECK_ROLL],
            [EventType.TRIGGER_ABILITY_CHECK_SUCCEED],
            [EventType.TRIGGER_ABILITY_CHECK_FAIL],
            f"{ability_name} check"
        )
    
    def skill_check(self, dc, skill_name, target = None, ability_name: str = None):
        """
        Makes a skill check roll against the given DC and target

        param dc: int - the difficulty class of the check
        param skill_name: str - the name of the skill to check
        param target (optional): Targettable - the target of the check
        param ability_name (optional): str - the ability score to base the skill check off of

        return: ReturnStatus - the result of the skill check
        """
        # If the skill_name is not valid, raise a ValueError
        if not self.is_valid_skill(skill_name):
            raise ValueError(f"Invalid skill ({skill_name})")
        
        # If ability_name is not provided, use the default ability for the skill
        if ability_name is None:
            ability_name = self.SKILL_ABILITIES[skill_name]
        
        # Get the modifiers for the skill check
        skill_modifiers = self._prepare_check(ability_name, target, [("make_skill_check", skill_name, "receive_skill_check")])
        
        # Call the handle_d20_roll method to handle the roll and return the result
        return self._handle_d20_roll(
            skill_modifiers, dc, 
            [EventType.TRIGGER_SKILL_CHECK_ROLL],
            [EventType.TRIGGER_SKILL_CHECK_SUCCEED],
            [EventType.TRIGGER_SKILL_CHECK_FAIL],
            f"{skill_name} check"
        )    
    
    def saving_throw(self, dc, ability_name, trigger = None, additional_roll_events = [], additional_success_events = [], additional_fail_events = []):
        """
        Makes a saving throw against the given DC with the given ability score

        param dc: int - the difficulty class of the saving throw
        param ability_name: str - the ability score to use for the saving throw
        param trigger (optional): Targettable - the trigger of the saving throw
        roll_events (optional): list - the events to trigger when the roll is made
        success_events (optional): list - the events to trigger when the saving throw is successful
        fail_events (optional): list - the events to trigger when the saving throw fails

        return: ReturnStatus - the result of the saving throw
        """
        # If the ability_name is not valid, raise a ValueError
        if not self.is_valid_ability(ability_name):
            raise ValueError(f"Invalid ability ({ability_name})")

        # Define a helper dictionary to map ability scores to their saving throw proficiencies
        saving_throw_proficiencies = {
            self.ABILITIES.STRENGTH.value: Proficiencies.SAVING_THROW_STRENGTH,
            self.ABILITIES.DEXTERITY.value: Proficiencies.SAVING_THROW_DEXTERITY,
            self.ABILITIES.CONSTITUTION.value: Proficiencies.SAVING_THROW_CONSTITUTION,
            self.ABILITIES.INTELLIGENCE.value: Proficiencies.SAVING_THROW_INTELLIGENCE,
            self.ABILITIES.WISDOM.value: Proficiencies.SAVING_THROW_WISDOM,
            self.ABILITIES.CHARISMA.value: Proficiencies.SAVING_THROW_CHARISMA
        }

        # Add any potential additional events to the roll, success, and fail events
        roll_events = [EventType.TRIGGER_SAVING_THROW_ROLL] + additional_roll_events
        success_events = [EventType.TRIGGER_SAVING_THROW_SUCCEED] + additional_success_events
        fail_events = [EventType.TRIGGER_SAVING_THROW_FAIL] + additional_fail_events

        # Get the modifiers for the saving throw
        modifiers = self._prepare_check(ability_name, trigger, [("make_saving_throw", ability_name, "force_saving_throw", saving_throw_proficiencies[ability_name])])

        # Call the handle_d20_roll method to handle the roll and return the result
        return self._handle_d20_roll(
            modifiers, dc, roll_events, success_events, fail_events, f"{ability_name} saving throw"
        )

    def _handle_d20_roll(self, roll_modifiers, dc, roll_events, success_events, fail_events, roll_tag: str = "roll"):
        """
        Handles a d20 roll by applying the given modifiers, comparing the result to the DC, and triggering events based on the result

        param roll_modifiers: ModifierRolls - the modifiers to apply to the roll
        param dc: int - the difficulty class of the roll
        param roll_bonus: int - the base bonus to add to the d20 roll
        param roll_events: list - the events to trigger when the roll is made
        param success_events: list - the events to trigger when the roll is successful
        param fail_events: list - the events to trigger when the roll fails

        return: ReturnStatus - the result of the roll
        """
        # Roll the die and trigger the roll events for the roll with the context
        die_result = self._dice_roller.roll_d20(roll_modifiers.advantage, roll_modifiers.disadvantage)
        roll_context = RollEventContext(self._statblock, roll_modifiers.advantage, roll_modifiers.disadvantage, roll_modifiers.auto_succeed, roll_modifiers.auto_fail, roll_modifiers.bonus)
        self._statblock._controller.trigger_reactions([(event, roll_context) for event in roll_events])

        # if the roll is an auto fail or the roll should not proceed, return false
        if roll_context.auto_fail or not roll_context.proceed:
            return ReturnStatus(False, f"Failed {roll_tag}: automatically failed.")
        
        # Calculate the final roll result and create the result context
        roll_result = die_result + roll_context.bonus
        result_context = RollResultEventContext(self._statblock, roll_result, roll_result >= dc, False)

        # If the roll is a failure, trigger the fail events, otherwise trigger the success events, then return the result status
        if not (roll_context.auto_succeed or result_context.success):
            self._statblock._controller.trigger_reactions([(fail_event, result_context) for fail_event in fail_events])
        if roll_context.auto_succeed or result_context.success:
            # If the roll is a success, trigger the success events and return a success message if result context remains successful
            self._statblock._controller.trigger_reactions([(success_event, result_context) for success_event in success_events])
            if roll_context.auto_succeed or result_context.success:
                roll_message = "Automatically succeeded." if roll_context.auto_succeed else f"Success, rolled {roll_result} against DC {dc}."
                return ReturnStatus(True, roll_message)
        return ReturnStatus(False, f"Failed {roll_tag}: rolled {roll_result} against DC {dc}.")