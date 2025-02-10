import unittest
from unittest.mock import MagicMock, patch
from src.stats.handlers.skill_handler import SkillHandler

class TestSkillHandler(unittest.TestCase):
    
    def test_is_valid_skill(self):
        valid_skills = ["acrobatics", 
                        "animal_handling", 
                        "arcana", 
                        "athletics", 
                        "deception", 
                        "history", 
                        "insight", 
                        "intimidation", 
                        "investigation", 
                        "medicine", 
                        "nature", 
                        "perception", 
                        "performance", 
                        "persuasion", 
                        "religion", 
                        "sleight_of_hand", 
                        "stealth", 
                        "survival"]
        
        for skill in valid_skills:
            self.assertTrue(SkillHandler.is_valid_skill(skill))
        
        self.assertFalse(SkillHandler.is_valid_skill("invalid_skill"))
    
    @patch("src.stats.statblock.Statblock")
    def test_has_proficiency(self, statblock):
        statblock._effects.get_function_results.return_value = []
        
        self.assertFalse(SkillHandler(statblock).has_proficiency("acrobatics"))
        self.assertFalse(SkillHandler(statblock).has_proficiency("athletics"))
        self.assertFalse(SkillHandler(statblock).has_proficiency("deception"))
        self.assertFalse(SkillHandler(statblock).has_proficiency("sleight_of_hand"))
        self.assertFalse(SkillHandler(statblock).has_proficiency("history"))        

        statblock._effects.get_function_results.return_value = [["acrobatics", "athletics"], ["deception"], ["athletics", "sleight_of_hand"]]

        self.assertTrue(SkillHandler(statblock).has_proficiency("acrobatics"))
        self.assertTrue(SkillHandler(statblock).has_proficiency("athletics"))
        self.assertTrue(SkillHandler(statblock).has_proficiency("deception"))
        self.assertTrue(SkillHandler(statblock).has_proficiency("sleight_of_hand"))
        self.assertFalse(SkillHandler(statblock).has_proficiency("history"))

    @patch("src.stats.statblock.Statblock")
    def test_get_passive_skill_score(self, statblock):
        # Set up default statblock mock with no passive skill boosting effects.
        statblock._ability_scores.get_ability.return_value = MagicMock(value = 10)
        statblock._effects.get_function_results.side_effect = lambda function_name, *args: (
            [] if function_name == "modify_passive_skill" else []
        )
        self.assertEqual(10, SkillHandler(statblock).get_passive_skill_score("perception"))

        # Verify statblock ability score modifiers are added to passive skill score.
        statblock._ability_scores.get_ability.return_value = MagicMock(value = 14)
        self.assertEqual(12, SkillHandler(statblock).get_passive_skill_score("perception"))

        # Verify advantage and bonus modifiers are applied to passive skill score.
        statblock._ability_scores.get_ability.return_value = MagicMock(value = 10)
        statblock._effects.get_function_results.side_effect = lambda function_name, *args: (
            [{"advantage": True, "bonus": -2}] if function_name == "modify_passive_skill" else []
        )
        self.assertEqual(13, SkillHandler(statblock).get_passive_skill_score("perception"))

        # Verify disadvantage and bonus modifiers are applied to passive skill score.
        statblock._effects.get_function_results.side_effect = lambda function_name, *args: (
            [{"disadvantage": True, "bonus": 3}] if function_name == "modify_passive_skill" else []
        )
        self.assertEqual(8, SkillHandler(statblock).get_passive_skill_score("perception"))

