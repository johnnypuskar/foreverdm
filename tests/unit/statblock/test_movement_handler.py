import unittest
from unittest.mock import patch
from src.stats.handlers.movement_handler import MovementHandler

class TestMovementHandler(unittest.TestCase):
    STATBLOCK = None

    @patch("src.stats.statblock.Statblock")
    def setUp(self, statblock):
        self.STATBLOCK = statblock

    def test_expend_speed(self):
        statblock = self.STATBLOCK

        def verify_movement(starting, movement, expected):
            self.STATBLOCK._speed.walk = starting[0]
            self.STATBLOCK._speed.fly = starting[1]
            self.STATBLOCK._speed.swim = starting[2]
            self.STATBLOCK._speed.climb = starting[3]
            self.STATBLOCK._speed.burrow = starting[4]

            statblock._speed.move.reset_mock()
            MovementHandler(statblock).expend_speed(movement)

            movement_cost = statblock._speed.move.call_args[0][0]
            self.assertEqual(movement_cost.walking, expected[0], f"Expected walk cost to be {expected[0]} but was {movement_cost.walking}")
            self.assertEqual(movement_cost.flying, expected[1] if expected[1] is not None else expected[0], f"Expected fly cost to be {expected[1] if expected[1] is not None else expected[0]} but was {movement_cost.flying}")
            self.assertEqual(movement_cost.swimming, expected[2], f"Expected swim cost to be {expected[2]} but was {movement_cost.swimming}")
            self.assertEqual(movement_cost.climbing, expected[3], f"Expected climb cost to be {expected[3]} but was {movement_cost.climbing}")
            self.assertEqual(movement_cost.burrowing, expected[4], f"Expected burrow cost to be {expected[4]} but was {movement_cost.burrowing}")

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
            for i in range(100, -5, -5):
                base_movement = [0, 0, 0, 0, 0]
                base_movement[movement_id] = 100
                
                result = [None, None, None, None, None]
                result[movement_id] = 100 - int(100 * (i / 100.0))

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
                


