import unittest
from unittest.mock import MagicMock, patch
from src.stats.handlers.hit_point_handler import HitPointHandler
from src.util.constants import EventType

class TestHitPointHandler(unittest.TestCase):

    @patch("src.stats.statblock.Statblock")
    def test_get_max_hp(self, statblock):
        statblock._effects.get_function_results.return_value = []
        statblock._hit_points = MagicMock(_max_hp = 20)

        self.assertEqual(20, HitPointHandler(statblock).get_max_hp())

        statblock._effects.get_function_results.return_value = [{"operation": "add", "value": 5}]
        self.assertEqual(25, HitPointHandler(statblock).get_max_hp())

        statblock._effects.get_function_results.return_value = [{"operation": "multiply", "value": 2}]
        self.assertEqual(40, HitPointHandler(statblock).get_max_hp())

        statblock._effects.get_function_results.return_value = [{"operation": "set", "value": 30}, {"operation": "set", "value": 10}]
        self.assertEqual(30, HitPointHandler(statblock).get_max_hp())

        statblock._effects.get_function_results.return_value = [{"operation": "set", "value": 10}]
        self.assertEqual(10, HitPointHandler(statblock).get_max_hp())

        statblock._effects.get_function_results.return_value = [{"operation": "add", "value": -5}, {"operation": "multiply", "value": 1.5}]
        self.assertEqual(25, HitPointHandler(statblock).get_max_hp())

        statblock._effects.get_function_results.return_value = [{"operation": "add", "value": 40}, {"operation": "multiply", "value": 3}, {"operation": "set", "value": 15}]
        self.assertEqual(15, HitPointHandler(statblock).get_max_hp())
    
    @patch("src.stats.statblock.Statblock")
    def test_restore_hp(self, statblock):
        statblock._effects.get_function_results.return_value = []
        statblock._hit_points = MagicMock(_hp = 10, _max_hp = 30)

        self.assertEqual(10, statblock._hit_points._hp)

        self.assertTrue(HitPointHandler(statblock).restore_hp(5).success)
        self.assertEqual(15, statblock._hit_points._hp)

        self.assertTrue(HitPointHandler(statblock).restore_hp(25).success)
        self.assertEqual(30, statblock._hit_points._hp)

        self.assertFalse(HitPointHandler(statblock).restore_hp(5).success)
        self.assertEqual(30, statblock._hit_points._hp)

class TestHitPointHandlerTakeDamage(unittest.TestCase):
    IMMUNITIES = []
    RESISTANCES = []
    VULNERABILITIES = []
    STATBLOCK = None

    @patch("src.stats.statblock.Statblock")
    def setUp(self, statblock):
        self.IMMUNITIES = []
        self.RESISTANCES = []
        self.VULNERABILITIES = []
        self.STATBLOCK = statblock
        self.STATBLOCK._effects.get_function_results.side_effect = lambda function_name, *args: (
            self.IMMUNITIES if function_name == "get_immunities" else
            self.RESISTANCES if function_name == "get_resistances" else
            self.VULNERABILITIES if function_name == "get_vulnerabilities" else
            []
        )
        self.STATBLOCK._hit_points = MagicMock(_hp = 100, _max_hp = 100)
        self.STATBLOCK._hit_points.get_hp.side_effect = lambda: statblock._hit_points._hp
        self.STATBLOCK._hit_points.reduce_hp.side_effect = lambda amount: setattr(statblock._hit_points, "_hp", statblock._hit_points._hp - amount)
        self.assertEqual(100, statblock._hit_points._hp)
    
    def test_take_damage_static(self):
        statblock = self.STATBLOCK

        HitPointHandler(statblock).take_damage("10 slashing")
        self.assertEqual(90, statblock._hit_points._hp)

        HitPointHandler(statblock).take_damage("5 piercing")
        self.assertEqual(85, statblock._hit_points._hp)

        HitPointHandler(statblock).take_damage("15 fire")
        self.assertEqual(70, statblock._hit_points._hp)

        HitPointHandler(statblock).take_damage("10 cold, 5 thunder")
        self.assertEqual(55, statblock._hit_points._hp)
    
    @patch("src.util.dice.DiceRoller.roll_custom")
    def test_take_damage_rolled(self, roller):
        statblock = self.STATBLOCK

        # Testing maximum damage rolls
        roller.side_effect = lambda amount, sides: amount * sides

        HitPointHandler(statblock).take_damage("2d6 slashing")
        self.assertEqual(88, statblock._hit_points._hp)

        HitPointHandler(statblock).take_damage("1d4 piercing")
        self.assertEqual(84, statblock._hit_points._hp)

        HitPointHandler(statblock).take_damage("3d8 fire, 1d4 force")
        self.assertEqual(56, statblock._hit_points._hp)

        HitPointHandler(statblock).take_damage("2d10+2 cold")
        self.assertEqual(34, statblock._hit_points._hp)

        HitPointHandler(statblock).take_damage("2d12+1d4 acid")
        self.assertEqual(6, statblock._hit_points._hp)

        # Testing minimum damage rolls
        statblock._hit_points._hp = 100
        roller.side_effect = lambda amount, sides: amount

        HitPointHandler(statblock).take_damage("2d6 slashing")
        self.assertEqual(98, statblock._hit_points._hp)

        HitPointHandler(statblock).take_damage("1d4 piercing")
        self.assertEqual(97, statblock._hit_points._hp)

        HitPointHandler(statblock).take_damage("3d8 fire, 1d4+1 force")
        self.assertEqual(92, statblock._hit_points._hp)

        HitPointHandler(statblock).take_damage("2d10+2+4 cold")
        self.assertEqual(84, statblock._hit_points._hp)
    
    def test_damage_immunities(self):
        statblock = self.STATBLOCK
        
        HitPointHandler(statblock).take_damage("10 slashing")
        self.assertEqual(90, statblock._hit_points._hp)

        self.IMMUNITIES = [["slashing"]]
        HitPointHandler(statblock).take_damage("10 slashing")
        self.assertEqual(90, statblock._hit_points._hp)

        
        HitPointHandler(statblock).take_damage("5 piercing")
        self.assertEqual(85, statblock._hit_points._hp)

        self.IMMUNITIES = [["piercing"]]
        HitPointHandler(statblock).take_damage("5 piercing")
        self.assertEqual(85, statblock._hit_points._hp)

        HitPointHandler(statblock).take_damage("15 fire")
        self.assertEqual(70, statblock._hit_points._hp)

        self.IMMUNITIES = [["fire"], ["force", "fire"]]
        HitPointHandler(statblock).take_damage("15 fire")
        self.assertEqual(70, statblock._hit_points._hp)
    
    def test_damage_resistances(self):
        statblock = self.STATBLOCK
        
        HitPointHandler(statblock).take_damage("10 slashing")
        self.assertEqual(90, statblock._hit_points._hp)

        self.RESISTANCES = [["slashing"]]
        HitPointHandler(statblock).take_damage("10 slashing")
        self.assertEqual(85, statblock._hit_points._hp)

        HitPointHandler(statblock).take_damage("5 piercing")
        self.assertEqual(80, statblock._hit_points._hp)

        self.RESISTANCES = [["piercing"]]
        HitPointHandler(statblock).take_damage("5 piercing")
        self.assertEqual(78, statblock._hit_points._hp)

        HitPointHandler(statblock).take_damage("18 fire")
        self.assertEqual(60, statblock._hit_points._hp)

        self.RESISTANCES = [["fire"], ["force", "fire"]]
        HitPointHandler(statblock).take_damage("13 fire")
        self.assertEqual(54, statblock._hit_points._hp)

        self.IMMUNITIES = [["force"]]
        self.RESISTANCES = [["force"]]
        HitPointHandler(statblock).take_damage("10 force")
        self.assertEqual(54, statblock._hit_points._hp)
    
    def test_damage_vulnerabilities(self):
        statblock = self.STATBLOCK

        HitPointHandler(statblock).take_damage("10 slashing")
        self.assertEqual(90, statblock._hit_points._hp)

        self.VULNERABILITIES = [["slashing"]]
        HitPointHandler(statblock).take_damage("10 slashing")
        self.assertEqual(70, statblock._hit_points._hp)

        HitPointHandler(statblock).take_damage("5 piercing")
        self.assertEqual(65, statblock._hit_points._hp)

        self.VULNERABILITIES = [["piercing"]]
        HitPointHandler(statblock).take_damage("5 piercing")
        self.assertEqual(55, statblock._hit_points._hp)

        self.VULNERABILITIES = [["fire"], ["force", "fire"]]
        HitPointHandler(statblock).take_damage("10 fire")
        self.assertEqual(35, statblock._hit_points._hp)

        self.RESISTANCES = [["psychic"]]
        self.VULNERABILITIES = [["psychic"]]
        HitPointHandler(statblock).take_damage("10 psychic")
        self.assertEqual(25, statblock._hit_points._hp)

        self.IMMUNITIES = [["radiant"]]
        self.VULNERABILITIES = [["radiant"]]
        self.RESISTANCES = []
        HitPointHandler(statblock).take_damage("10 radiant")
        self.assertEqual(25, statblock._hit_points._hp)
    
    def test_zero_hp(self):
        statblock = self.STATBLOCK

        statblock._hit_points._hp = 5
        HitPointHandler(statblock).take_damage("10 slashing")
        self.assertEqual(statblock._controller.trigger_event.call_args[0][0], EventType.TRIGGER_ZERO_HP)
        self.assertEqual(statblock._hit_points._hp, 0)

        HitPointHandler(statblock).take_damage("25 slashing")
        self.assertEqual(statblock._controller.trigger_event.call_args[0][0], EventType.TRIGGER_ZERO_HP)
        self.assertEqual(statblock._hit_points._hp, 0)

        HitPointHandler(statblock).take_damage("100 slashing")
        self.assertEqual(statblock._controller.trigger_event.call_args[0][0], EventType.TRIGGER_DEATH)
        self.assertEqual(statblock._hit_points._hp, -100)

    @patch("src.stats.handlers.ability_roll_handler.AbilityRollHandler.saving_throw")
    def test_concentration_save(self, saving_throw):
        statblock = self.STATBLOCK
        statblock._hit_points._hp = 200
        statblock._hit_points._max_hp = 200
        saving_throw.return_value = MagicMock(success = True)
        statblock._abilities._concentration_tracker.concentrating = True

        HitPointHandler(statblock).take_damage("1 slashing")
        self.assertEqual(saving_throw.call_args[0][0], 10)

        HitPointHandler(statblock).take_damage("10 slashing")
        self.assertEqual(saving_throw.call_args[0][0], 10)

        HitPointHandler(statblock).take_damage("20 slashing")
        self.assertEqual(saving_throw.call_args[0][0], 10)

        HitPointHandler(statblock).take_damage("21 slashing")
        self.assertEqual(saving_throw.call_args[0][0], 10)

        HitPointHandler(statblock).take_damage("22 slashing")
        self.assertEqual(saving_throw.call_args[0][0], 11)

        HitPointHandler(statblock).take_damage("30 slashing")
        self.assertEqual(saving_throw.call_args[0][0], 15)

        saving_throw.return_value = MagicMock(success = False)
        self.assertFalse(statblock._abilities._concentration_tracker.end_concentration.called)
        HitPointHandler(statblock).take_damage("1 slashing")
        self.assertTrue(statblock._abilities._concentration_tracker.end_concentration.called)