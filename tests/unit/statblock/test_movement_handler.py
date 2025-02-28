import unittest
from unittest.mock import patch
from src.stats.handlers.movement_handler import MovementHandler

class TestMovementHandler(unittest.TestCase):
    STATBLOCK = None

    @patch("src.stats.statblock.Statblock")
    def setUp(self, statblock):
        self.STATBLOCK = statblock

    def test_modify_speed(self):
        statblock = self.STATBLOCK

        def verify_movement(starting, movement, expected):
            self.STATBLOCK._speed.walk = starting[0]
            self.STATBLOCK._speed.fly = starting[1]
            self.STATBLOCK._speed.swim = starting[2]
            self.STATBLOCK._speed.climb = starting[3]
            self.STATBLOCK._speed.burrow = starting[4]

            statblock._speed.move.reset_mock()
            MovementHandler(statblock).modify_speed(movement)

            movement_cost = statblock._speed.move.call_args[0][0]
            self.assertAlmostEqual(movement_cost.walk, expected[0], 4, f"Expected walk cost to be {expected[0]} but was {movement_cost.walk}")
            self.assertAlmostEqual(movement_cost.fly, expected[1] if expected[1] is not None else expected[0], 4, f"Expected fly cost to be {expected[1] if expected[1] is not None else expected[0]} but was {movement_cost.fly}")
            self.assertAlmostEqual(movement_cost.swim, expected[2], 4, f"Expected swim cost to be {expected[2]} but was {movement_cost.swim}")
            self.assertAlmostEqual(movement_cost.climb, expected[3], 4, f"Expected climb cost to be {expected[3]} but was {movement_cost.climb}")
            self.assertAlmostEqual(movement_cost.burrow, expected[4], 4, f"Expected burrow cost to be {expected[4]} but was {movement_cost.burrow}")

        def verify_type(movement_type):
            movement_types = ["walk", "fly", "swim", "climb", "burrow"]
            movement_id = movement_types.index(movement_type)

            # Test add operation
            for i in range(60, -5, -5):
                base_movement = [0, 0, 0, 0, 0]
                base_movement[movement_id] = 60
                
                result = [None, None, None, None, None]
                result[movement_id] = 60 - i

                verify_movement(
                    base_movement,
                    {movement_type: {"value": 60 - i, "operation": "add"}},
                    result
                )
            
            # Test multiply operation
            for i in range(200, -5, -5):
                base_movement = [0, 0, 0, 0, 0]
                base_movement[movement_id] = 100
                
                result = [None, None, None, None, None]
                result[movement_id] = 100 - 100 * (i / 100.0)

                verify_movement(
                    base_movement,
                    {movement_type: {"value": i / 100.0, "operation": "multiply"}},
                    result
                )
            
            # Test set operation
            for i in range(60, -5, -5):
                base_movement = [0, 0, 0, 0, 0]
                base_movement[movement_id] = 60
                
                result = [None, None, None, None, None]
                result[movement_id] = 60 - i

                verify_movement(
                    base_movement,
                    {movement_type: {"value": i, "operation": "set"}},
                    result
                )
        
        verify_type("walk")
        verify_type("fly")
        verify_type("swim")
        verify_type("climb")
        verify_type("burrow")
                


