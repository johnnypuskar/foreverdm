import unittest
from src.stats.statblock import Statblock
from src.events.event_manager import EventManager

class IntegrationTestStatblock(unittest.TestCase):
    def test_reaction_events(self):
        event_manager = EventManager()

        primary = Statblock("Primary")
        secondary = Statblock("Secondary")

        primary.assign_event_manager(event_manager)
        secondary.assign_event_manager(event_manager)

        print(primary.ability_check(1, "str"))

