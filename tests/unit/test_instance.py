import unittest, sys, os
from src.combat.map.instance import Instance, PositionOccupiedError
from src.combat.map.battlemap import Map
from src.combat.map.token import Token
from src.stats.statblock import Statblock

class TestInstance(unittest.TestCase):
    def setUp(self) -> None:
        sys.stdout.reconfigure(encoding='utf-8')

        test_dir = os.path.dirname(os.path.abspath(__file__))

        self.TEST_LEVEL_SIZE = os.path.join(test_dir, "levels\\size_test_level.fdm")
        self.TEST_LEVEL_TERRAIN = os.path.join(test_dir, "levels\\terrain_test_level.fdm")
        self.TEST_LEVEL_WATER = os.path.join(test_dir, "levels\\water_test_small.fdm")

        return super().setUp()
    
    def test_adding_token(self):
        instance = Instance(Map(5, 5))
        token = Token()

        # Token is added to instance and position is updated
        self.assertEqual(token.position, (-1, -1))
        instance.add_token(token, (1, 2))
        self.assertEqual(token.position, (1, 2))

        # Error is thrown when token already exists in the instance
        self.assertRaises(ValueError, instance.add_token, token, (3, 3))

        # Error is thrown when position is already occupied
        other_token = Token()
        self.assertRaises(PositionOccupiedError, instance.add_token, other_token, (1, 2))

    def test_removing_token(self):
        instance = Instance(Map(5, 5))
        token = Token()
        instance.add_token(token, (1, 2))

        # Token is removed from instance
        instance.remove_token(token)
        self.assertNotIn(token, instance.tokens)

        # Error is thrown when token does not exist in the instance
        self.assertRaises(ValueError, instance.remove_token, token)

    def test_moving_token(self):
        instance = Instance(Map(10, 4))
        instance.map.calculate_navgraph()
        token = Token(Statblock("Fighter"))

        instance.add_token(token, (1, 1))

        # Cannot move to a space too far away
        self.assertFalse(instance.move_token(token, (8, 1)))

        # Can move to a space within reach and position updates correctly
        self.assertTrue(instance.move_token(token, (6, 1)))
        self.assertEqual(token.position, (6, 1))

        # Can now move to space originally too far away and position updates correctly
        self.assertTrue(instance.move_token(token, (8, 1)))
        self.assertEqual(token.position, (8, 1))

        # Cannot move onto already occupied space
        other_token = Token(Statblock("Wizard"))
        instance.add_token(other_token, (8, 3))
        self.assertRaises(PositionOccupiedError, instance.move_token, token, (8, 3))

        # Can move onto previously occupied space if token is moved
        instance.move_token(other_token, (9, 3))
        self.assertTrue(instance.move_token(token, (8, 3)))
