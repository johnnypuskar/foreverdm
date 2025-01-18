import unittest
from unittest.mock import patch, MagicMock
from src.stats.statblock import Statblock
from src.stats.positioned_statblock import PositionedStatblock

class TestPositionedStatblock(unittest.TestCase):
    def test_conversion(self):
        # Create a statblock and set some arbitrary values
        statblock = Statblock("Test", size = 10)
        statblock._hp._initial = 20
        statblock._hp._value = 14
        statblock._ability_scores['con'].value = 18

        # Convert the statblock to a PositionedStatblock and verify the values are preserved
        positioned = PositionedStatblock.from_statblock(statblock)
        self.assertEqual(positioned._name, "Test")
        self.assertEqual(positioned._size, 10)
        self.assertEqual(positioned._hp._initial, 20)
        self.assertEqual(positioned._hp._value, 14)
        self.assertEqual(positioned._ability_scores['con'].value, 18)

        # Update some values in the PositionedStatblock
        positioned._hp._value = 10
        positioned._ability_scores['con'].value = 14
        positioned._ability_scores['int'].value = 8
               
        # Convert the PositionedStatblock back to a Statblock and verify the values are preserved
        reverted_statblock = positioned.to_statblock()
        self.assertEqual(reverted_statblock._name, "Test")
        self.assertEqual(reverted_statblock._size, 10)
        self.assertEqual(reverted_statblock._hp._initial, 20)
        self.assertEqual(reverted_statblock._hp._value, 10)
        self.assertEqual(reverted_statblock._ability_scores['con'].value, 14)
        self.assertEqual(reverted_statblock._ability_scores['int'].value, 8)
    
    def test_in_melee(self):
        # Create positioned statblocks
        anchor_statblock = PositionedStatblock("Anchor")
        anchor_statblock._position = (4, 4)

        adjacent_statblock = PositionedStatblock("Adjacent")

        # Test all squares in a 10x10 grid.
        successful = []
        for x in range(10):
            for y in range(10):
                if (x, y) == anchor_statblock._position:
                    continue
                adjacent_statblock._position = (x, y)
                if anchor_statblock.in_melee(adjacent_statblock):
                    successful.append((x, y))

        # Check that the only successful squares are the 8 adjacent to the anchor
        expected = [(3, 3), (3, 4), (3, 5), (4, 3), (4, 5), (5, 3), (5, 4), (5, 5)]
        self.assertListEqual(successful, expected)

    def test_pull_towards(self):
        # Create positioned statblock
        statblock = PositionedStatblock("Test")
        statblock._position = (0, 0)

        # Test pushing aligned to axes
        statblock.pull_towards(5, 0, 2)
        self.assertEqual(statblock._position, (2, 0))

        statblock.pull_towards(2, 5, 3)
        self.assertEqual(statblock._position, (2, 3))

        # Reset and push at diagonals, using pythagorean triplets for easy integer coordinates
        statblock.set_position(0, 0)
        statblock.pull_towards(3, 4, 10)
        self.assertEqual(statblock._position, (6, 8))

        statblock.pull_towards(16, -16, 13)
        self.assertEqual(statblock._position, (11, -4))

        # Reset and push at imprecise angles to verify rounding
        statblock.set_position(0, 0)
        statblock.pull_towards(1, 1, 1)
        self.assertEqual(statblock._position, (1, 1))

        statblock.set_position(0, 0)
        statblock.pull_towards(5, 6, 8)
        self.assertEqual(statblock._position, (5, 6))

        statblock.set_position(0, 0)
        statblock.pull_towards(5, 6, 7)
        self.assertEqual(statblock._position, (4, 5))

        # Reset and verify pushing with zero distance
        statblock.set_position(0, 0)
        statblock.pull_towards(40, -25, 0)
        self.assertEqual(statblock._position, (0, 0))
    
    def test_push_from(self):
        # Create positioned statblock
        statblock = PositionedStatblock("Test")
        statblock._position = (0, 0)

        # Test pushing aligned to axes
        statblock.push_from(5, 0, 2)
        self.assertEqual(statblock._position, (-2, 0))

        statblock.push_from(-2, 5, 3)
        self.assertEqual(statblock._position, (-2, -3))

        # Reset and push at diagonals, using pythagorean triplets for easy integer coordinates
        statblock.set_position(0, 0)
        statblock.push_from(3, 4, 10)
        self.assertEqual(statblock._position, (-6, -8))

        statblock.push_from(18, -18, 26)
        self.assertEqual(statblock._position, (-30, 2))

        # Reset and push at imprecise angles to verify rounding
        statblock.set_position(0, 0)
        statblock.push_from(1, 1, 1)
        self.assertEqual(statblock._position, (-1, -1))

        statblock.set_position(0, 0)
        statblock.push_from(5, 6, 8)
        self.assertEqual(statblock._position, (-5, -6))

        statblock.set_position(0, 0)
        statblock.push_from(5, 6, 7)
        self.assertEqual(statblock._position, (-4, -5))

        # Reset and verify pushing with zero distance
        statblock.set_position(0, 0)
        statblock.push_from(40, -25, 0)
        self.assertEqual(statblock._position, (0, 0))