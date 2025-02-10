import unittest
from unittest.mock import MagicMock, patch
from src.stats.handlers.world_sense_handler import WorldSenseHandler

class TestWorldSenseHandler(unittest.TestCase):
    STATBLOCK = None
    TARGET = None

    SELF_VISIBILITY = []
    TARGET_VISIBILITY = []
    TARGET_NOTICED = []

    @patch('src.stats.statblock.Statblock')
    @patch('src.stats.statblock.Statblock')
    def setUp(self, statblock, target):
        self.STATBLOCK = statblock
        self.TARGET = target
        
        self.STATBLOCK._effects.get_function_results.side_effect = lambda function_name, *_: (
            self.SELF_VISIBILITY if function_name == "modify_visibility" else
            []
        )

        self.TARGET._effects.get_function_results.side_effect = lambda function_name, *_: (
            self.TARGET_VISIBILITY if function_name == "modify_visibility" else
            self.TARGET_NOTICED if function_name == "is_noticed" else
            []
        )

    def test_visibility(self):
        statblock = self.STATBLOCK

        self.assertEqual(WorldSenseHandler(statblock).visibility(), 2)

        self.SELF_VISIBILITY = [{"operation": "add", "value": 1}]
        self.assertEqual(WorldSenseHandler(statblock).visibility(), 2)

        self.SELF_VISIBILITY = [{"operation": "add", "value": -1}]
        self.assertEqual(WorldSenseHandler(statblock).visibility(), 1)

        self.SELF_VISIBILITY = [{"operation": "add", "value": -2}]
        self.assertEqual(WorldSenseHandler(statblock).visibility(), 0)

        self.SELF_VISIBILITY = [{"operation": "add", "value": -3}]
        self.assertEqual(WorldSenseHandler(statblock).visibility(), 0)

        self.SELF_VISIBILITY = [{"operation": "multiply", "value": 0.5}]
        self.assertEqual(WorldSenseHandler(statblock).visibility(), 2)

        self.SELF_VISIBILITY = [{"operation": "multiply", "value": 0.0}]
        self.assertEqual(WorldSenseHandler(statblock).visibility(), 2)

        self.SELF_VISIBILITY = [{"operation": "set", "value": 0}, {"operation": "set", "value": 1}]
        self.assertEqual(WorldSenseHandler(statblock).visibility(), 0)

        self.SELF_VISIBILITY = [{"operation": "set", "value": 1}, {"operation": "add", "value": 1}]
        self.assertEqual(WorldSenseHandler(statblock).visibility(), 1)
    
    @patch('src.stats.handlers.world_sense_handler.SkillHandler.get_passive_skill_score')
    def test_sight_to(self, passive_skill):
        statblock = self.STATBLOCK
        target = self.TARGET

        self.assertEqual(WorldSenseHandler(statblock).sight_to(target, 10), 2)

        self.TARGET_NOTICED = [True]
        self.assertEqual(WorldSenseHandler(statblock).sight_to(target, 10), 2)

        self.TARGET_NOTICED = [False]
        self.assertEqual(WorldSenseHandler(statblock).sight_to(target, 10), 0)

        self.TARGET_NOTICED = [True, False]
        self.assertEqual(WorldSenseHandler(statblock).sight_to(target, 10), 2)

        self.TARGET_NOTICED = [False, False]
        self.assertEqual(WorldSenseHandler(statblock).sight_to(target, 10), 0)

        self.TARGET_VISIBILITY = [{"operation": "add", "value": -1}]
        self.TARGET_NOTICED = []
        self.assertEqual(WorldSenseHandler(statblock).sight_to(target, 10), 1)

        self.TARGET_VISIBILITY = [{"operation": "add", "value": 1}]
        self.assertEqual(WorldSenseHandler(statblock).sight_to(target, 10), 2)

        target._effects.get_function_results.reset_mock()
        WorldSenseHandler(statblock).sight_to(target, 12)
        self.assertEqual(target._effects.get_function_results.call_args_list[0][0][2], 12)
        
        target._effects.get_function_results.reset_mock()
        passive_skill.return_value = 15
        WorldSenseHandler(statblock).sight_to(target)
        self.assertEqual(target._effects.get_function_results.call_args_list[0][0][2], 15)