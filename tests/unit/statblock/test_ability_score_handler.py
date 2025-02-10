import unittest
from unittest.mock import patch, MagicMock
from src.stats.handlers.ability_score_handler import AbilityScoreHandler

class TestAbilityScoreHandler(unittest.TestCase):
    @patch("src.stats.statblock.Statblock")
    def test_get_base_ability_scores(self, statblock):
        statblock._ability_scores.get_ability.return_value = MagicMock(value = 10)
        statblock._effects.get_function_results.return_value = []

        self.assertEqual(10, AbilityScoreHandler(statblock).get_ability_score("strength"))
        self.assertEqual(0, AbilityScoreHandler(statblock).get_ability_modifier("strength"))

        self.assertEqual(10, AbilityScoreHandler(statblock).get_ability_score("dexterity"))
        self.assertEqual(0, AbilityScoreHandler(statblock).get_ability_modifier("dexterity"))

        self.assertEqual(10, AbilityScoreHandler(statblock).get_ability_score("constitution"))
        self.assertEqual(0, AbilityScoreHandler(statblock).get_ability_modifier("constitution"))

        self.assertEqual(10, AbilityScoreHandler(statblock).get_ability_score("intelligence"))
        self.assertEqual(0, AbilityScoreHandler(statblock).get_ability_modifier("intelligence"))

        self.assertEqual(10, AbilityScoreHandler(statblock).get_ability_score("wisdom"))
        self.assertEqual(0, AbilityScoreHandler(statblock).get_ability_modifier("wisdom"))

        self.assertEqual(10, AbilityScoreHandler(statblock).get_ability_score("charisma"))
        self.assertEqual(0, AbilityScoreHandler(statblock).get_ability_modifier("charisma"))

        statblock._ability_scores.get_ability.return_value = MagicMock(value = 16)

        self.assertEqual(16, AbilityScoreHandler(statblock).get_ability_score("charisma"))
        self.assertEqual(3, AbilityScoreHandler(statblock).get_ability_modifier("charisma"))

        statblock._ability_scores.get_ability.return_value = MagicMock(value = 7)

        self.assertEqual(7, AbilityScoreHandler(statblock).get_ability_score("constitution"))
        self.assertEqual(-2, AbilityScoreHandler(statblock).get_ability_modifier("constitution"))
    
    @patch("src.stats.statblock.Statblock")
    def test_get_modified_ability_scores(self, statblock):
        statblock._ability_scores.get_ability.return_value = MagicMock(value = 13)

        self.assertEqual(13, AbilityScoreHandler(statblock).get_ability_score("strength"))
        self.assertEqual(1, AbilityScoreHandler(statblock).get_ability_modifier("strength"))

        statblock._effects.get_function_results.return_value = [{"operation": "add", "value": 3}]

        self.assertEqual(16, AbilityScoreHandler(statblock).get_ability_score("strength"))
        self.assertEqual(3, AbilityScoreHandler(statblock).get_ability_modifier("strength"))

        statblock._effects.get_function_results.return_value = [{"operation": "multiply", "value": 2}]

        self.assertEqual(26, AbilityScoreHandler(statblock).get_ability_score("strength"))
        self.assertEqual(8, AbilityScoreHandler(statblock).get_ability_modifier("strength"))

        statblock._effects.get_function_results.return_value = [{"operation": "set", "value": 10}]

        self.assertEqual(10, AbilityScoreHandler(statblock).get_ability_score("strength"))
        self.assertEqual(0, AbilityScoreHandler(statblock).get_ability_modifier("strength"))

        # Multiplication should be applied before addition
        statblock._effects.get_function_results.return_value = [{"operation": "add", "value": -6}, {"operation": "multiply", "value": 2}]

        self.assertEqual(20, AbilityScoreHandler(statblock).get_ability_score("strength"))
        self.assertEqual(5, AbilityScoreHandler(statblock).get_ability_modifier("strength"))

        # Set is applied last, and sets to the largest set value
        statblock._effects.get_function_results.return_value = [{"operation": "set", "value": 12}, {"operation": "add", "value": 5}, {"operation": "set", "value": 14}, {"operation": "multiply", "value": 2}]

        self.assertEqual(14, AbilityScoreHandler(statblock).get_ability_score("strength"))
        self.assertEqual(2, AbilityScoreHandler(statblock).get_ability_modifier("strength"))