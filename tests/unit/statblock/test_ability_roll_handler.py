import unittest
from unittest.mock import MagicMock, patch, create_autospec
from src.stats.handlers.ability_roll_handler import AbilityRollHandler

class TestAbilityRollHandler(unittest.TestCase):
    STATBLOCK = None
    TARGET = None

    STR = 10
    DEX = 10
    CON = 10
    INT = 10
    WIS = 10
    CHA = 10

    PROFICIENCIES = []

    SELF_ABILITY = []
    SELF_SKILL = []
    SELF_SAVING = []

    TARGET_ABILITY = []
    TARGET_SKILL = []
    TARGET_SAVING = []

    @patch("src.stats.statblock.Statblock")
    @patch("src.stats.statblock.Statblock")
    def setUp(self, statblock, target):
        self.STATBLOCK = statblock
        self.TARGET = target
        
        self.STATBLOCK.get_proficiency_bonus.return_value = 2
        self.STATBLOCK._effects.get_function_results.side_effect = lambda function_name, *args: (
            self.SELF_ABILITY if function_name == "make_ability_check" else
            self.SELF_SKILL if function_name == "make_skill_check" else
            self.SELF_SAVING if function_name == "make_saving_throw" else
            self.PROFICIENCIES if function_name == "get_proficiencies" else 
            []
        )
        self.STATBLOCK._ability_scores.get_ability.side_effect = lambda ability_name: (
            MagicMock(value = self.STR) if ability_name == "strength" else
            MagicMock(value = self.DEX) if ability_name == "dexterity" else
            MagicMock(value = self.CON) if ability_name == "constitution" else
            MagicMock(value = self.INT) if ability_name == "intelligence" else
            MagicMock(value = self.WIS) if ability_name == "wisdom" else
            MagicMock(value = self.CHA) if ability_name == "charisma" else
            MagicMock(value = 0)
        )
        self.TARGET._effects.get_function_results.side_effect = lambda function_name, *args: (
            self.TARGET_ABILITY if function_name == "receive_ability_check" else
            self.TARGET_SKILL if function_name == "receive_skill_check" else
            self.TARGET_SAVING if function_name == "force_saving_throw" else
            []
        )
    
    @patch("src.util.dice.DiceRoller.roll_d20", return_value = 10)
    def test_ability_check(self, roller):
        statblock = self.STATBLOCK

        def validate_checks(highest_success, ability_name):
            """
            Performs a series of ability checks with increasing DCs from 1 to 30 for the given ability.
            Asserts that ability checks succeed for DC less than or equal to the given value.
            Asserts that ability checks fail for DC greater than the given value.
            """
            for i in range(1, 31):
                result = AbilityRollHandler(statblock).ability_check(i, ability_name)
                self.assertEqual(i <= highest_success, result.success, f"DC {i} {ability_name.title()} check was {result.success}, should be {i <= highest_success}")

        validate_checks(10, "strength")
        with self.assertRaises(ValueError):
            AbilityRollHandler(statblock).ability_check(10, "honor")

        self.STR = 12
        validate_checks(11, "strength")

        self.INT = 17
        validate_checks(11, "strength")
        validate_checks(13, "intelligence")

        self.CON = 6
        validate_checks(8, "constitution")

        roller.reset_mock()
        self.SELF_ABILITY = [{"advantage": True}]
        self.assertTrue(AbilityRollHandler(statblock).ability_check(10, "strength").success)
        self.assertTrue(roller.call_args[0][0])
        self.assertFalse(roller.call_args[0][1])

        roller.reset_mock()
        self.SELF_ABILITY = [{"disadvantage": True}]
        self.assertTrue(AbilityRollHandler(statblock).ability_check(10, "strength").success)
        self.assertFalse(roller.call_args[0][0])
        self.assertTrue(roller.call_args[0][1])

        roller.reset_mock()
        self.SELF_ABILITY = [{"advantage": True}, {"disadvantage": True}]
        self.assertTrue(AbilityRollHandler(statblock).ability_check(10, "strength").success)
        self.assertTrue(roller.call_args[0][0])
        self.assertTrue(roller.call_args[0][1])

        roller.reset_mock()
        self.SELF_ABILITY = [{"bonus": 4}]
        validate_checks(14, "charisma")
        self.SELF_ABILITY = [{"bonus": -3}]
        validate_checks(7, "charisma")

        roller.reset_mock()
        self.SELF_ABILITY = [{"bonus": 100}, {"auto_fail": True}]
        validate_checks(0, "charisma")

        roller.reset_mock()
        self.SELF_ABILITY = [{"bonus": -100}, {"auto_succeed": True}]
        validate_checks(30, "charisma")

        roller.reset_mock()
        self.SELF_ABILITY = [{"auto_succeed": True}, {"auto_fail": True}]
        validate_checks(0, "charisma")
    
    @patch("src.util.dice.DiceRoller.roll_d20", return_value = 10)
    def test_ability_check_targeted(self, roller):
        statblock = self.STATBLOCK
        target = self.TARGET

        def validate_checks(highest_success, ability_name):
            """
            Performs a series of ability checks with increasing DCs from 1 to 30 for the given ability.
            Asserts that ability checks succeed for DC less than or equal to the given value.
            Asserts that ability checks fail for DC greater than the given value.
            """
            for i in range(1, 31):
                result = AbilityRollHandler(statblock).ability_check(i, ability_name, target)
                self.assertEqual(i <= highest_success, result.success, f"DC {i} {ability_name.title()} check was {result.success}, should be {i <= highest_success}")

        validate_checks(10, "strength")
        with self.assertRaises(ValueError):
            AbilityRollHandler(statblock).ability_check(10, "honor", target)

        roller.reset_mock()
        self.TARGET_ABILITY = [{"advantage": True}]
        self.assertTrue(AbilityRollHandler(statblock).ability_check(10, "strength", target).success)
        self.assertTrue(roller.call_args[0][0])
        self.assertFalse(roller.call_args[0][1])

        roller.reset_mock()
        self.TARGET_ABILITY = [{"disadvantage": True}]
        self.assertTrue(AbilityRollHandler(statblock).ability_check(10, "strength", target).success)
        self.assertFalse(roller.call_args[0][0])
        self.assertTrue(roller.call_args[0][1])

        roller.reset_mock()
        self.TARGET_ABILITY = [{"advantage": True}, {"disadvantage": True}]
        self.assertTrue(AbilityRollHandler(statblock).ability_check(10, "strength", target).success)
        self.assertTrue(roller.call_args[0][0])
        self.assertTrue(roller.call_args[0][1])

        roller.reset_mock()
        self.TARGET_ABILITY = [{"bonus": 4}]
        validate_checks(14, "strength")
        self.TARGET_ABILITY = [{"bonus": -3}]
        validate_checks(7, "strength")

        roller.reset_mock()
        self.TARGET_ABILITY = [{"bonus": 100}, {"auto_fail": True}]
        validate_checks(0, "strength")

        roller.reset_mock()
        self.TARGET_ABILITY = [{"bonus": -100}, {"auto_succeed": True}]
        validate_checks(30, "strength")

        roller.reset_mock()
        self.TARGET_ABILITY = [{"auto_succeed": True}, {"auto_fail": True}]
        validate_checks(0, "strength")

    @patch("src.util.dice.DiceRoller.roll_d20", return_value = 10)
    def test_skill_check(self, roller):
        statblock = self.STATBLOCK

        def validate_checks(highest_success, skill_name, ability_name = None):
            """
            Performs a series of ability checks with increasing DCs from 1 to 30 for the given ability.
            Asserts that ability checks succeed for DC less than or equal to the given value.
            Asserts that ability checks fail for DC greater than the given value.
            """
            for i in range(1, 31):
                result = AbilityRollHandler(statblock).skill_check(i, skill_name, ability_name = ability_name)
                ability_tag = "" if ability_name is None else f" ({ability_name.title()})"
                self.assertEqual(i <= highest_success, result.success, f"DC {i} {skill_name.title()}{ability_tag} check was {result.success}, should be {i <= highest_success}")
        
        validate_checks(10, "insight")
        with self.assertRaises(ValueError):
            AbilityRollHandler(statblock).skill_check(10, "resourcefulness")
        with self.assertRaises(ValueError):
            AbilityRollHandler(statblock).skill_check(10, "insight", None, "honor")

        self.WIS = 15

        validate_checks(12, "insight")
        validate_checks(10, "insight", "intelligence")
        validate_checks(12, "sleight_of_hand", "wisdom")
        validate_checks(10, "sleight_of_hand")

        self.DEX = 6

        validate_checks(8, "sleight_of_hand")

        roller.reset_mock()
        self.SELF_SKILL = [{"advantage": True}]
        self.assertTrue(AbilityRollHandler(statblock).skill_check(10, "history").success)
        self.assertTrue(roller.call_args[0][0])
        self.assertFalse(roller.call_args[0][1])

        roller.reset_mock()
        self.SELF_SKILL = [{"disadvantage": True}]
        self.assertTrue(AbilityRollHandler(statblock).skill_check(10, "history").success)
        self.assertFalse(roller.call_args[0][0])
        self.assertTrue(roller.call_args[0][1])

        roller.reset_mock()
        self.SELF_SKILL = [{"advantage": True}, {"disadvantage": True}]
        self.assertTrue(AbilityRollHandler(statblock).skill_check(10, "history").success)
        self.assertTrue(roller.call_args[0][0])
        self.assertTrue(roller.call_args[0][1])

        roller.reset_mock()
        self.SELF_SKILL = [{"bonus": 4}]
        validate_checks(14, "history")
        self.SELF_SKILL = [{"bonus": -3}]
        validate_checks(7, "history")

        roller.reset_mock()
        self.SELF_SKILL = [{"bonus": 100}, {"auto_fail": True}]
        validate_checks(0, "history")
        
        roller.reset_mock()
        self.SELF_SKILL = [{"bonus": -100}, {"auto_succeed": True}]
        validate_checks(30, "history")

        roller.reset_mock()
        self.SELF_SKILL = [{"auto_succeed": True}, {"auto_fail": True}]
        validate_checks(0, "history")

        self.SELF_SKILL = []
        validate_checks(10, "persuasion")
        self.PROFICIENCIES = [["persuasion"]]
        validate_checks(12, "persuasion")
        validate_checks(14, "persuasion", "wisdom")
    
    @patch("src.util.dice.DiceRoller.roll_d20", return_value = 10)
    def test_skill_check_targeted(self, roller):
        statblock = self.STATBLOCK
        target = self.TARGET

        def validate_checks(highest_success, skill_name, ability_name = None):
            """
            Performs a series of skill checks with increasing DCs from 1 to 30 for the given ability.
            Asserts that skill checks succeed for DC less than or equal to the given value.
            Asserts that skill checks fail for DC greater than the given value.
            """
            for i in range(1, 31):
                result = AbilityRollHandler(statblock).skill_check(i, skill_name, target, ability_name)
                ability_tag = "" if ability_name is None else f" ({ability_name.title()})"
                self.assertEqual(i <= highest_success, result.success, f"DC {i} {skill_name.title()}{ability_tag} check was {result.success}, should be {i <= highest_success}")
        
        validate_checks(10, "insight")
        with self.assertRaises(ValueError):
            AbilityRollHandler(statblock).skill_check(10, "resourcefulness", target)
        with self.assertRaises(ValueError):
            AbilityRollHandler(statblock).skill_check(10, "insight", target, "honor")
        
        roller.reset_mock()
        self.TARGET_SKILL = [{"advantage": True}]
        self.assertTrue(AbilityRollHandler(statblock).skill_check(10, "history", target).success)
        self.assertTrue(roller.call_args[0][0])
        self.assertFalse(roller.call_args[0][1])

        roller.reset_mock()
        self.TARGET_SKILL = [{"disadvantage": True}]
        self.assertTrue(AbilityRollHandler(statblock).skill_check(10, "history", target).success)
        self.assertFalse(roller.call_args[0][0])
        self.assertTrue(roller.call_args[0][1])

        roller.reset_mock()
        self.TARGET_SKILL = [{"advantage": True}, {"disadvantage": True}]
        self.assertTrue(AbilityRollHandler(statblock).skill_check(10, "history", target).success)
        self.assertTrue(roller.call_args[0][0])
        self.assertTrue(roller.call_args[0][1])

        roller.reset_mock()
        self.TARGET_SKILL = [{"bonus": 4}]
        validate_checks(14, "history")
        self.TARGET_SKILL = [{"bonus": -3}]
        validate_checks(7, "history")

        roller.reset_mock()
        self.TARGET_SKILL = [{"bonus": 100}, {"auto_fail": True}]
        validate_checks(0, "history")

        roller.reset_mock()
        self.TARGET_SKILL = [{"bonus": -100}, {"auto_succeed": True}]
        validate_checks(30, "history")

        roller.reset_mock()
        self.TARGET_SKILL = [{"auto_succeed": True}, {"auto_fail": True}]
        validate_checks(0, "history")
    
    @patch("src.util.dice.DiceRoller.roll_d20", return_value = 10)
    def test_saving_throw(self, roller):
        statblock = self.STATBLOCK

        def validate_checks(highest_success, ability_name):
            """
            Performs a series of saving throws with increasing DCs from 1 to 30 for the given ability.
            Asserts that saving throws succeed for DC less than or equal to the given value.
            Asserts that saving throws fail for DC greater than the given value.
            """
            for i in range(1, 31):
                result = AbilityRollHandler(statblock).saving_throw(i, ability_name)
                self.assertEqual(i <= highest_success, result.success, f"DC {i} {ability_name.title()} saving throw was {result.success}, should be {i <= highest_success}")
        
        validate_checks(10, "strength")
        with self.assertRaises(ValueError):
            AbilityRollHandler(statblock).saving_throw(10, "honor")
        
        self.INT = 15
        validate_checks(12, "intelligence")

        self.CON = 6
        validate_checks(8, "constitution")

        roller.reset_mock()
        self.SELF_SAVING = [{"advantage": True}]
        self.assertTrue(AbilityRollHandler(statblock).saving_throw(10, "strength").success)
        self.assertTrue(roller.call_args[0][0])
        self.assertFalse(roller.call_args[0][1])

        roller.reset_mock()
        self.SELF_SAVING = [{"disadvantage": True}]
        self.assertTrue(AbilityRollHandler(statblock).saving_throw(10, "strength").success)
        self.assertFalse(roller.call_args[0][0])
        self.assertTrue(roller.call_args[0][1])

        roller.reset_mock()
        self.SELF_SAVING = [{"advantage": True}, {"disadvantage": True}]
        self.assertTrue(AbilityRollHandler(statblock).saving_throw(10, "strength").success)
        self.assertTrue(roller.call_args[0][0])
        self.assertTrue(roller.call_args[0][1])

        roller.reset_mock()
        self.SELF_SAVING = [{"bonus": 4}]
        validate_checks(14, "strength")
        self.SELF_SAVING = [{"bonus": -3}]
        validate_checks(7, "strength")

        roller.reset_mock()
        self.SELF_SAVING = [{"bonus": 100}, {"auto_fail": True}]
        validate_checks(0, "strength")

        roller.reset_mock()
        self.SELF_SAVING = [{"bonus": -100}, {"auto_succeed": True}]
        validate_checks(30, "strength")

        roller.reset_mock()
        self.SELF_SAVING = [{"auto_succeed": True}, {"auto_fail": True}]
        validate_checks(0, "strength")

        self.SELF_SAVING = []
        validate_checks(10, "dexterity")
        self.PROFICIENCIES = [["dexterity_saving_throws"]]
        validate_checks(12, "dexterity")

    @patch("src.util.dice.DiceRoller.roll_d20", return_value = 10)
    def test_saving_throw_targeted(self, roller):
        statblock = self.STATBLOCK
        target = self.TARGET

        def validate_checks(highest_success, ability_name):
            """
            Performs a series of saving throws with increasing DCs from 1 to 30 for the given ability.
            Asserts that saving throws succeed for DC less than or equal to the given value.
            Asserts that saving throws fail for DC greater than the given value.
            """
            for i in range(1, 31):
                result = AbilityRollHandler(statblock).saving_throw(i, ability_name, target)
                self.assertEqual(i <= highest_success, result.success, f"DC {i} {ability_name.title()} saving throw was {result.success}, should be {i <= highest_success}")
        
        validate_checks(10, "strength")
        with self.assertRaises(ValueError):
            AbilityRollHandler(statblock).saving_throw(10, "honor", target)
        
        roller.reset_mock()
        self.TARGET_SAVING = [{"advantage": True}]
        self.assertTrue(AbilityRollHandler(statblock).saving_throw(10, "strength", target).success)
        self.assertTrue(roller.call_args[0][0])
        self.assertFalse(roller.call_args[0][1])

        roller.reset_mock()
        self.TARGET_SAVING = [{"disadvantage": True}]
        self.assertTrue(AbilityRollHandler(statblock).saving_throw(10, "strength", target).success)
        self.assertFalse(roller.call_args[0][0])
        self.assertTrue(roller.call_args[0][1])

        roller.reset_mock()
        self.TARGET_SAVING = [{"advantage": True}, {"disadvantage": True}]
        self.assertTrue(AbilityRollHandler(statblock).saving_throw(10, "strength", target).success)
        self.assertTrue(roller.call_args[0][0])
        self.assertTrue(roller.call_args[0][1])

        roller.reset_mock()
        self.TARGET_SAVING = [{"bonus": 4}]
        validate_checks(14, "strength")
        self.TARGET_SAVING = [{"bonus": -3}]
        validate_checks(7, "strength")

        roller.reset_mock()
        self.TARGET_SAVING = [{"bonus": 100}, {"auto_fail": True}]
        validate_checks(0, "strength")

        roller.reset_mock()
        self.TARGET_SAVING = [{"bonus": -100}, {"auto_succeed": True}]
        validate_checks(30, "strength")

        roller.reset_mock()
        self.TARGET_SAVING = [{"auto_succeed": True}, {"auto_fail": True}]
        validate_checks(0, "strength")