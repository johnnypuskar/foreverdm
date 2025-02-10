from enum import Enum
from src.stats.handlers.ability_score_handler import AbilityScoreHandler
from src.util.modifier_values import ModifierRolls

class SkillHandler(AbilityScoreHandler):
    class SKILLS(Enum):
        ACROBATICS = "acrobatics"
        ANIMAL_HANDLING = "animal_handling"
        ARCANA = "arcana"
        ATHLETICS = "athletics"
        DECEPTION = "deception"
        HISTORY = "history"
        INSIGHT = "insight"
        INTIMIDATION = "intimidation"
        INVESTIGATION = "investigation"
        MEDICINE = "medicine"
        NATURE = "nature"
        PERCEPTION = "perception"
        PERFORMANCE = "performance"
        PERSUASION = "persuasion"
        RELIGION = "religion"
        SLEIGHT_OF_HAND = "sleight_of_hand"
        STEALTH = "stealth"
        SURVIVAL = "survival"

    SKILL_ABILITIES = {
        SKILLS.ACROBATICS.value: AbilityScoreHandler.ABILITIES.DEXTERITY.value,
        SKILLS.ANIMAL_HANDLING.value: AbilityScoreHandler.ABILITIES.WISDOM.value,
        SKILLS.ARCANA.value: AbilityScoreHandler.ABILITIES.INTELLIGENCE.value,
        SKILLS.ATHLETICS.value: AbilityScoreHandler.ABILITIES.STRENGTH.value,
        SKILLS.DECEPTION.value: AbilityScoreHandler.ABILITIES.CHARISMA.value,
        SKILLS.HISTORY.value: AbilityScoreHandler.ABILITIES.INTELLIGENCE.value,
        SKILLS.INSIGHT.value: AbilityScoreHandler.ABILITIES.WISDOM.value,
        SKILLS.INTIMIDATION.value: AbilityScoreHandler.ABILITIES.CHARISMA.value,
        SKILLS.INVESTIGATION.value: AbilityScoreHandler.ABILITIES.INTELLIGENCE.value,
        SKILLS.MEDICINE.value: AbilityScoreHandler.ABILITIES.WISDOM.value,
        SKILLS.NATURE.value: AbilityScoreHandler.ABILITIES.INTELLIGENCE.value,
        SKILLS.PERCEPTION.value: AbilityScoreHandler.ABILITIES.WISDOM.value,
        SKILLS.PERFORMANCE.value: AbilityScoreHandler.ABILITIES.CHARISMA.value,
        SKILLS.PERSUASION.value: AbilityScoreHandler.ABILITIES.CHARISMA.value,
        SKILLS.RELIGION.value: AbilityScoreHandler.ABILITIES.INTELLIGENCE.value,
        SKILLS.SLEIGHT_OF_HAND.value: AbilityScoreHandler.ABILITIES.DEXTERITY.value,
        SKILLS.STEALTH.value: AbilityScoreHandler.ABILITIES.DEXTERITY.value,
        SKILLS.SURVIVAL.value: AbilityScoreHandler.ABILITIES.WISDOM.value
    }

    def __init__(self, statblock):
        super().__init__(statblock)
    
    @staticmethod
    def is_valid_skill(skill_name):
        """Returns true if the given skill name is valid, false otherwise"""
        return skill_name in [skill.value for skill in SkillHandler.SKILLS]

    def has_proficiency(self, proficiency_name):
        """Returns true if the Statblock has proficiency in the given proficiency, false otherwise"""
        proficiencies = set([proficiency for result in self._statblock._effects.get_function_results("get_proficiencies", self._statblock) for proficiency in result])
        return proficiency_name in proficiencies

    def get_passive_skill_score(self, skill_name):
        """
        Returns the passive skill score for the given skill

        param skill_name: str - the name of the skill to get the passive score for

        return: int - the passive skill score
        """
        # If the skill_name is not valid, raise a ValueError
        if not self.is_valid_skill(skill_name):
            raise ValueError(f"Invalid skill ({skill_name})")

        # Get the modifiers that would apply to the skill check
        ability_name = self.SKILL_ABILITIES[skill_name]

        # Get the modifiers and bonus for the skill check
        modifiers = self._prepare_check(ability_name, None, [("make_skill_check", skill_name, "recieve_skill_check")])

        # Get the modifiers for passive checks and merge them with the skill check modifiers
        passive_modifiers = ModifierRolls(self._statblock._effects.get_function_results("modify_passive_skill", self._statblock, skill_name))
        modifiers.merge(passive_modifiers)

        # Add or subtract 5 from the roll bonus based on advantage and disadvantage
        modifiers.bonus += 5 if modifiers.advantage else 0
        modifiers.bonus -= 5 if modifiers.disadvantage else 0

        return 10 + modifiers.bonus

    def _prepare_bonus(self, parameter):
        """
        Returns the bonus added based on the given parameter's proficiency.
        Overrides parent function used in AbilityScoreHandler._prepare_check.
        """
        proficiency_type = parameter[3] if len(parameter) > 3 else parameter[1]
        if self.has_proficiency(proficiency_type):
            return self._statblock.get_proficiency_bonus()
        return 0