import unittest
from src.control.controller import Controller
from src.stats.statblock import Statblock
from src.events.event_manager import EventManager

class IntegrationTestStatblock(unittest.TestCase):
    def test_reaction_events(self):
        event_manager = EventManager()

        primary_controller = Controller()
        primary = Statblock("Primary")
        primary_controller.statblock = primary

        secondary_controller = Controller()
        secondary = Statblock("Secondary")
        secondary_controller.statblock = secondary

        primary_controller.event_manager = event_manager
        secondary_controller.event_manager = event_manager

        print(f"\n{primary.name} attacks {secondary.name}\n : {secondary.name} HP: {secondary._hp}")
        print(primary.melee_attack_roll(secondary, "1d4 slashing, 1d4 lightning"))
        print(f" : {secondary.name} HP: {secondary._hp}")

        primary.ability_check(15, "str")

        primary.skill_check(15, "athletics")

        primary.saving_throw(10, "con")

