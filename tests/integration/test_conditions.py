import unittest
from unittest.mock import patch

from src.control.controller import Controller
from src.stats.statblock import Statblock
from src.stats.conditions import Blinded, Charmed

class TestConditions(unittest.TestCase):
    
    @patch('src.util.dice.DiceRoller.roll_d20', return_value = 10)
    def test_blinded(self, Mock_roll_d20):
        # Create primary statblock
        test_controller = Controller()
        statblock = Statblock("Source")
        statblock._controller = test_controller

        # Create secondary statblock
        target_controller = Controller()
        target = Statblock("Target")
        target._controller = target_controller

        # Create blinded effect
        blinded_effect = Blinded()

        # Verify that all types of attack are rolled with no advantage or disadvantage
        Mock_roll_d20.reset_mock()
        statblock.melee_attack_roll(target, "1d4")
        Mock_roll_d20.assert_called_with(False, False)

        Mock_roll_d20.reset_mock()
        statblock.ranged_attack_roll(target, "1d4")
        Mock_roll_d20.assert_called_with(False, False)

        Mock_roll_d20.reset_mock()
        statblock.ability_attack_roll(target, "int", "1d4")
        Mock_roll_d20.assert_called_with(False, False)

        # Verify that all types of incoming attack are rolled with no advantage or disadvantage
        Mock_roll_d20.reset_mock()
        target.melee_attack_roll(statblock, "1d4")
        Mock_roll_d20.assert_called_with(False, False)

        Mock_roll_d20.reset_mock()
        target.ranged_attack_roll(statblock, "1d4")
        Mock_roll_d20.assert_called_with(False, False)

        Mock_roll_d20.reset_mock()
        target.ability_attack_roll(statblock, "int", "1d4")
        Mock_roll_d20.assert_called_with(False, False)

        # Add blinded effect to statblock and verify it is applied
        statblock.add_effect(blinded_effect, 3)
        self.assertIn(blinded_effect, statblock._effects._effects.values())
        
        # Verify that all types of attack are rolled with disadvantage
        Mock_roll_d20.reset_mock()
        statblock.melee_attack_roll(target, "1d4")
        Mock_roll_d20.assert_called_with(False, True)

        Mock_roll_d20.reset_mock()
        statblock.ranged_attack_roll(target, "1d4")
        Mock_roll_d20.assert_called_with(False, True)

        Mock_roll_d20.reset_mock()
        statblock.ability_attack_roll(target, "int", "1d4")
        Mock_roll_d20.assert_called_with(False, True)

        # Verify that all types of incoming attack are rolled with advantage
        Mock_roll_d20.reset_mock()
        target.melee_attack_roll(statblock, "1d4")
        Mock_roll_d20.assert_called_with(True, False)

        Mock_roll_d20.reset_mock()
        target.ranged_attack_roll(statblock, "1d4")
        Mock_roll_d20.assert_called_with(True, False)

        Mock_roll_d20.reset_mock()
        target.ability_attack_roll(statblock, "int", "1d4")
        Mock_roll_d20.assert_called_with(True, False)
    
    @patch('src.util.dice.DiceRoller.roll_d20', return_value = 20)
    def test_charmed(self, Mock_roll_d20):
        # Create primary statblock
        test_controller = Controller()
        statblock = Statblock("Source")
        statblock._controller = test_controller

        # Create secondary statblock
        target_controller = Controller()
        target = Statblock("Target")
        target._controller = target_controller

        # Create charmed effect
        charmed_effect = Charmed(target)

        # Verify that all types of attack are rolled with no advantage or disadvantage
        Mock_roll_d20.reset_mock()
        statblock.melee_attack_roll(target, "1d4")
        Mock_roll_d20.assert_called_with(False, False)

        Mock_roll_d20.reset_mock()
        statblock.ranged_attack_roll(target, "1d4")
        Mock_roll_d20.assert_called_with(False, False)

        Mock_roll_d20.reset_mock()
        statblock.ability_attack_roll(target, "int", "1d4")
        Mock_roll_d20.assert_called_with(False, False)

        # Verify that no ability checks are rolled with advantage
        Mock_roll_d20.reset_mock()
        result = target.ability_check(10, "str", statblock)
        Mock_roll_d20.assert_called_with(False, False)

        Mock_roll_d20.reset_mock()
        result = target.ability_check(10, "dex", statblock)
        Mock_roll_d20.assert_called_with(False, False)

        Mock_roll_d20.reset_mock()
        result = target.ability_check(10, "con", statblock)
        Mock_roll_d20.assert_called_with(False, False)

        Mock_roll_d20.reset_mock()
        result = target.ability_check(10, "int", statblock)
        Mock_roll_d20.assert_called_with(False, False)

        Mock_roll_d20.reset_mock()
        result = target.ability_check(10, "wis", statblock)
        Mock_roll_d20.assert_called_with(False, False)

        Mock_roll_d20.reset_mock()
        result = target.ability_check(10, "cha", statblock)
        Mock_roll_d20.assert_called_with(False, False)

        # Add charmed effect to target and verify it is applied
        statblock.add_effect(charmed_effect, 3)
        self.assertIn(charmed_effect, statblock._effects._effects.values())

        # Verify that all types of attack fail without rolling
        Mock_roll_d20.reset_mock()
        result = statblock.melee_attack_roll(target, "1d4")
        self.assertFalse(result)
        Mock_roll_d20.assert_not_called()

        Mock_roll_d20.reset_mock()
        result = statblock.ranged_attack_roll(target, "1d4")
        self.assertFalse(result)
        Mock_roll_d20.assert_not_called()

        Mock_roll_d20.reset_mock()
        result = statblock.ability_attack_roll(target, "int", "1d4")
        self.assertFalse(result)
        Mock_roll_d20.assert_not_called()

        # Verify that only charisma ability checks are rolled with advantage
        Mock_roll_d20.reset_mock()
        result = target.ability_check(10, "str", statblock)
        Mock_roll_d20.assert_called_with(False, False)

        Mock_roll_d20.reset_mock()
        result = target.ability_check(10, "dex", statblock)
        Mock_roll_d20.assert_called_with(False, False)

        Mock_roll_d20.reset_mock()
        result = target.ability_check(10, "con", statblock)
        Mock_roll_d20.assert_called_with(False, False)

        Mock_roll_d20.reset_mock()
        result = target.ability_check(10, "int", statblock)
        Mock_roll_d20.assert_called_with(False, False)

        Mock_roll_d20.reset_mock()
        result = target.ability_check(10, "wis", statblock)
        Mock_roll_d20.assert_called_with(False, False)

        Mock_roll_d20.reset_mock()
        result = target.ability_check(10, "cha", statblock)
        Mock_roll_d20.assert_called_with(True, False)



