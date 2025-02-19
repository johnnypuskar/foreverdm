import unittest
from unittest.mock import patch
from src.stats.size import Size
from src.stats.movement.speed import Speed
from src.stats.statblock import Statblock

class TestStatblock(unittest.TestCase):

    # Base Statistics
    def test_get_name(self):
        statblock = Statblock("Tester")

        self.assertEqual("Tester", statblock.get_name())
    
    @patch("src.stats.effect_index.EffectIndex.get_function_results")
    def test_get_size(self, effect_results):
        tiny_statblock = Statblock("Tiny", Size.TINY)
        small_statblock = Statblock("Small", Size.SMALL)
        medium_statblock = Statblock("Medium", Size.MEDIUM)
        large_statblock = Statblock("Large", Size.LARGE)
        huge_statblock = Statblock("Huge", Size.HUGE)
        gargantuan_statblock = Statblock("Gargantuan", Size.GARGANTUAN)

        self.assertEqual(0, tiny_statblock.get_size().size_class)
        self.assertEqual(1, small_statblock.get_size().size_class)
        self.assertEqual(2, medium_statblock.get_size().size_class)
        self.assertEqual(3, large_statblock.get_size().size_class)
        self.assertEqual(4, huge_statblock.get_size().size_class)
        self.assertEqual(5, gargantuan_statblock.get_size().size_class)

        # Getting size with size-modifying effects
        effect_results.return_value = [{"operation": "set", "value": 4}]

        self.assertEqual(4, tiny_statblock.get_size().size_class)
        self.assertEqual(4, small_statblock.get_size().size_class)
        self.assertEqual(4, medium_statblock.get_size().size_class)
        self.assertEqual(4, large_statblock.get_size().size_class)
        self.assertEqual(4, huge_statblock.get_size().size_class)
        self.assertEqual(4, gargantuan_statblock.get_size().size_class)

        
        effect_results.return_value = [{"operation": "add", "value": 1}]

        self.assertEqual(1, tiny_statblock.get_size().size_class)
        self.assertEqual(2, small_statblock.get_size().size_class)
        self.assertEqual(3, medium_statblock.get_size().size_class)
        self.assertEqual(4, large_statblock.get_size().size_class)
        self.assertEqual(5, huge_statblock.get_size().size_class)
        self.assertEqual(5, gargantuan_statblock.get_size().size_class)

        effect_results.return_value = [{"operation": "add", "value": -1}]

        self.assertEqual(0, tiny_statblock.get_size().size_class)
        self.assertEqual(0, small_statblock.get_size().size_class)
        self.assertEqual(1, medium_statblock.get_size().size_class)
        self.assertEqual(2, large_statblock.get_size().size_class)
        self.assertEqual(3, huge_statblock.get_size().size_class)
        self.assertEqual(4, gargantuan_statblock.get_size().size_class)

    def test_get_speed(self):
        statblock = Statblock("Tester", speed = Speed(10, 20, 30, 40, 50, True))
        statblock._speed.distance_moved = 15

        self.assertEqual(Speed(10, 20, 30, 40, 50, True), statblock.get_speed())
        self.assertEqual(15, statblock.get_speed().distance_moved)

    @patch("src.stats.effect_index.EffectIndex.get_function_results")
    def test_get_initiative_modifier(self, effect_results):
        statblock = Statblock("Tester")

        initiative = statblock.get_initiative_modifier()
        self.assertFalse(initiative.advantage)
        self.assertFalse(initiative.disadvantage)
        self.assertFalse(initiative.auto_succeed)
        self.assertFalse(initiative.auto_fail)
        self.assertEqual(0, initiative.bonus)

        effect_results.return_value = [{"advantage": True}]

        initiative = statblock.get_initiative_modifier()
        self.assertTrue(initiative.advantage)
        self.assertFalse(initiative.disadvantage)
        self.assertFalse(initiative.auto_succeed)
        self.assertFalse(initiative.auto_fail)
        self.assertEqual(0, initiative.bonus)

        effect_results.return_value = [{"disadvantage": True}, {"bonus": 2}, {"bonus": 3}]

        initiative = statblock.get_initiative_modifier()
        self.assertFalse(initiative.advantage)
        self.assertTrue(initiative.disadvantage)
        self.assertFalse(initiative.auto_succeed)
        self.assertFalse(initiative.auto_fail)
        self.assertEqual(5, initiative.bonus)

        effect_results.return_value = [{"auto_succeed": True, "bonus": 3}, {"auto_fail": True, "bonus": -2}]

        initiative = statblock.get_initiative_modifier()
        self.assertFalse(initiative.advantage)
        self.assertFalse(initiative.disadvantage)
        self.assertTrue(initiative.auto_succeed)
        self.assertTrue(initiative.auto_fail)
        self.assertEqual(1, initiative.bonus)

    @patch("src.stats.effect_index.EffectIndex.get_function_results")
    def test_get_armor_class(self, effect_results):
        statblock = Statblock("Tester")

        self.assertEqual(10, statblock.get_armor_class())

        effect_results.return_value = [{"operation": "multiply", "value": 1.5}]
        self.assertEqual(15, statblock.get_armor_class())

        effect_results.return_value = [{"operation": "add", "value": 7}]
        self.assertEqual(17, statblock.get_armor_class())

        effect_results.return_value = [{"operation": "set", "value": 20}]
        self.assertEqual(20, statblock.get_armor_class())

        effect_results.return_value = [{"operation": "add", "value": -5}, {"operation": "multiply", "value": 1.2}]
        self.assertEqual(7, statblock.get_armor_class())

        effect_results.return_value = [{"operation": "set", "value": 5}, {"operation": "add", "value": 10}, {"operation": "set", "value": 6}]
        self.assertEqual(6, statblock.get_armor_class())

        effect_results.return_value = [{"operation": "set", "value": 5}, {"operation": "multiply", "value": 2}]
        self.assertEqual(5, statblock.get_armor_class())

    def test_get_proficiency_bonus(self):
        statblock = Statblock("Tester")

        statblock._level.add_level("fighter")

        self.assertEqual(2, statblock.get_proficiency_bonus())

        statblock._level.add_level("fighter", 3)
        self.assertEqual(2, statblock.get_proficiency_bonus())

        statblock._level.add_level("fighter", 1)
        self.assertEqual(3, statblock.get_proficiency_bonus())

        statblock._level.add_level("fighter", 3)
        self.assertEqual(3, statblock.get_proficiency_bonus())

        statblock._level.add_level("fighter", 1)
        self.assertEqual(4, statblock.get_proficiency_bonus())

        statblock._level.add_level("fighter", 3)
        self.assertEqual(4, statblock.get_proficiency_bonus())

        statblock._level.add_level("fighter", 1)
        self.assertEqual(5, statblock.get_proficiency_bonus())

        statblock._level.add_level("fighter", 3)
        self.assertEqual(5, statblock.get_proficiency_bonus())

        statblock._level.add_level("fighter", 1)
        self.assertEqual(6, statblock.get_proficiency_bonus())

        statblock._level.add_level("fighter", 3)
        self.assertEqual(6, statblock.get_proficiency_bonus())
        self.assertEqual(20, statblock._level.get_level())