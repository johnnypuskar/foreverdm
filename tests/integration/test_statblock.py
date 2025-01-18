import unittest
from unittest.mock import patch
from src.stats.abilities import Ability
from src.control.controller import Controller
from src.stats.statblock import Statblock
from src.stats.positioned_statblock import PositionedStatblock
from src.events.event_manager import EventManager

class IntegrationTestStatblock(unittest.TestCase):
    @patch('src.util.dice.DiceRoller.roll_d20', return_value = 15)
    def test_reaction_events(self, roll_d20):
        event_manager = EventManager()

        primary_controller = Controller()
        primary = Statblock("Primary")
        primary._ability_scores["str"].value = 20
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
    
    def test_positional_abilities(self):
        event_manager = EventManager()

        primary_controller = Controller()
        primary = PositionedStatblock("Primary")
        primary.set_position(10, 0)
        primary._controller = primary_controller

        secondary_controller = Controller()
        secondary = PositionedStatblock("Secondary")
        secondary.set_position(-5, 0)
        secondary._controller = secondary_controller

        test_ability = Ability("test_ability", '''
            use_time = UseTime("action")
            
            function run(target)
                x, y = statblock.get_position()
                target.push_from(x, y, 15)
                return target.get_position()
            end
        ''')
        primary.add_ability(test_ability)

        print(primary.use_ability("test_ability", secondary))


