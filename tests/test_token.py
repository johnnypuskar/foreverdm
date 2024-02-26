import unittest
from src.stats.statistics import Stat, StatModifier

class TestTokens(unittest.TestCase):
    def test_token(self):
        pass

class TestStats(unittest.TestCase):
    def test_stat_modifiers(self):
        stat = Stat("strength", 14)

        # Value calculated properly
        self.assertEqual(stat.value, 14)

        # Datastring for stat with no modifiers
        CORRECT_EMPTY_DATASTRING = "strength: 14"
        self.assertEqual(stat.datastring, CORRECT_EMPTY_DATASTRING)

        # Positive modifier
        plus_mod = StatModifier(2, "test buff")
        stat.add_modifier(plus_mod)
        self.assertEqual(stat.value, 16)

        # Removing modifiers
        stat.remove_modifier(0)
        self.assertEqual(stat.value, 14)

        # Negative modifier
        minus_mod = StatModifier(-3, "test debuff")
        stat.add_modifier(minus_mod)
        self.assertEqual(stat.value, 11)

        # Multiple modifiers
        second_plus_mod = StatModifier(4, "other test buff")
        stat.add_modifier(second_plus_mod)
        self.assertEqual(stat.value, 15)

        # Zero modifier does not update value
        zero_mod = StatModifier(0, "kinda useless")
        stat.add_modifier(zero_mod)
        self.assertEqual(stat.value, 15)

        # Stat datastring correctly formatted
        CORRECT_FULL_DATASTRING = "strength: 15 (14 (base) with modifiers [-3 (from test debuff), +4 (from other test buff), +0 (from kinda useless)]"
        self.assertEqual(stat.datastring, CORRECT_FULL_DATASTRING)
