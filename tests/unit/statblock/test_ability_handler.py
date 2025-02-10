import unittest
from unittest.mock import MagicMock, patch
from src.stats.handlers.ability_handler import AbilityHandler

class TestAbilityHandler(unittest.TestCase):
    STATBLOCK = None

    ABILITY_INDEX = {}

    ALLOW_ACTIONS = []
    ALLOW_REACTIONS = []


    @patch('src.stats.statblock.Statblock')
    def setUp(self, statblock):
        self.STATBLOCK = statblock

        self.STATBLOCK._abilities.add.side_effect = lambda ability: self.ABILITY_INDEX.update({ability.name: ability})
        self.STATBLOCK._abilities.remove.side_effect = lambda ability_name: self.ABILITY_INDEX.pop(ability_name)
        self.STATBLOCK._abilities.get_ability.side_effect = lambda ability_name: self.ABILITY_INDEX.get(ability_name)
        self.STATBLOCK._abilities.run_ability.side_effect = lambda ability_name, _, *args, modifier_calls: (
            self.ABILITY_INDEX.get(ability_name).mocked_return_value,
            f"Used {self.ABILITY_INDEX.get(ability_name).name}"
        )

        self.STATBLOCK._effects.get_function_results.side_effect = lambda function_name, *args: (
            self.ALLOW_ACTIONS if function_name == "allow_actions" else
            self.ALLOW_REACTIONS if function_name == "allow_reactions" else
            []
        )
        
        self.STATBLOCK._turn_resources.make_copy.return_value = MagicMock(
            use_from_use_time = MagicMock(return_value = True)
        )
    
    def AbilityMock(self, name, use_time, return_value, modifier = False):
        ability = MagicMock()
        
        ability.name = name
        ability.mocked_use_time_string = use_time
        ability.is_modifier = modifier

        ability._use_time = MagicMock()
        ability._use_time.__str__.return_value = ability.mocked_use_time_string
        ability._use_time.is_action.side_effect = lambda: ability.mocked_use_time_string == "action"
        ability._use_time.is_bonus_action.side_effect = lambda: ability.mocked_use_time_string == "bonus_action"
        ability._use_time.is_reaction.side_effect = lambda: ability.mocked_use_time_string == "reaction"
        ability._use_time.is_special = True

        ability.mocked_return_value = return_value

        return ability

    def test_add_ability(self):
        statblock = self.STATBLOCK
        ability = self.AbilityMock("test_ability", "action", True)

        AbilityHandler(statblock).add_ability(ability)
        statblock._abilities.add.assert_called_with(ability)
    
    def test_remove_ability(self):
        statblock = self.STATBLOCK
        self.ABILITY_INDEX["test_ability"] = self.AbilityMock("test_ability", "action", True)

        AbilityHandler(statblock).remove_ability("test_ability")
        statblock._abilities.remove.assert_called_with("test_ability")
    
    def test_use_ability(self):
        statblock = self.STATBLOCK
        action_ability = self.AbilityMock("test_ability", "action", True)
        bonus_action_ability = self.AbilityMock("test_ability_bonus", "bonus_action", True)
        reaction_ability = self.AbilityMock("test_ability_reaction", "reaction", True)

        handler = AbilityHandler(statblock)
        handler.add_ability(action_ability)
        handler.add_ability(bonus_action_ability)
        handler.add_ability(reaction_ability)

        result = handler.use_ability("test_ability")
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Used test_ability")

        result = handler.use_ability("test_ability_bonus")
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Used test_ability_bonus")

        result = handler.use_ability("test_ability_reaction")
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Used test_ability_reaction")
    
    def test_action_preventing_effects(self):
        statblock = self.STATBLOCK
        action_ability = self.AbilityMock("test_ability", "action", True)
        bonus_action_ability = self.AbilityMock("test_ability_bonus", "bonus_action", True)
        reaction_ability = self.AbilityMock("test_ability_reaction", "reaction", True)

        handler = AbilityHandler(statblock)
        handler.add_ability(action_ability)
        handler.add_ability(bonus_action_ability)
        handler.add_ability(reaction_ability)

        self.ALLOW_ACTIONS = [True]
        self.ALLOW_REACTIONS = [True]
        self.assertTrue(handler.use_ability("test_ability").success)
        self.assertTrue(handler.use_ability("test_ability_bonus").success)
        self.assertTrue(handler.use_ability("test_ability_reaction").success)

        self.ALLOW_ACTIONS = [True, True, False]
        self.assertFalse(handler.use_ability("test_ability").success)
        self.assertEqual(handler.use_ability("test_ability").message, "Unable to take action")
        self.assertFalse(handler.use_ability("test_ability_bonus").success)
        self.assertEqual(handler.use_ability("test_ability_bonus").message, "Unable to take bonus_action")
        self.assertTrue(handler.use_ability("test_ability_reaction").success)

        self.ALLOW_REACTIONS = [False, True]
        self.assertFalse(handler.use_ability("test_ability").success)
        self.assertFalse(handler.use_ability("test_ability_bonus").success)
        self.assertFalse(handler.use_ability("test_ability_reaction").success)
        self.assertEqual(handler.use_ability("test_ability_reaction").message, "Unable to take reaction")
    
    def test_modifier_abilities(self):
        statblock = self.STATBLOCK
        ability = self.AbilityMock("test_ability", "action", True)
        modifier_1 = self.AbilityMock("modifier_1", "action", True, True)
        modifier_2 = self.AbilityMock("modifier_2", "action", True, True)

        handler = AbilityHandler(statblock)
        handler.add_ability(ability)
        handler.add_ability(modifier_1)
        handler.add_ability(modifier_2)

        result = handler.use_ability("modifier_1", "parameter")
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Prepared use of modifier_1.")

        result = handler.use_ability("modifier_2", 40, "argument")
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Prepared use of modifier_2.")

        statblock._abilities.run_ability.reset_mock()
        result = handler.use_ability("test_ability", "value")
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Used test_ability")

        statblock._abilities.run_ability.assert_called_with("test_ability", statblock, "value", modifier_calls = [
            tuple(["modifier_1", "parameter"]),
            tuple(["modifier_2", 40, "argument"])
        ])
    
    def test_modifier_abilities_no_resources(self):
        statblock = self.STATBLOCK
        ability = self.AbilityMock("test_ability", "action", True)
        modifier_1 = self.AbilityMock("modifier_1", "bonus_action", True, True)
        modifier_2 = self.AbilityMock("modifier_2", "action", True, True)
        modifier_3 = self.AbilityMock("modifier_3", "bonus_action", True, True)

        handler = AbilityHandler(statblock)
        handler.add_ability(ability)
        handler.add_ability(modifier_1)
        handler.add_ability(modifier_2)
        handler.add_ability(modifier_3)

        self.TURN_RESOURCES = {"action": True, "bonus_action": True}
        self.STATBLOCK._turn_resources.make_copy.return_value = MagicMock(
            use_from_use_time = MagicMock(
                side_effect = lambda use_time: self.TURN_RESOURCES.pop(str(use_time), False)
            )
        )

        result = handler.use_ability("modifier_1")
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Prepared use of modifier_1.")

        result = handler.use_ability("modifier_2")
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Prepared use of modifier_2.")

        result = handler.use_ability("test_ability")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "No action remaining to use test_ability after modifiers.")

        self.TURN_RESOURCES = {"action": True, "bonus_action": True}

        result = handler.use_ability("modifier_1")
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Prepared use of modifier_1.")

        result = handler.use_ability("modifier_2")
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Prepared use of modifier_2.")

        result = handler.use_ability("modifier_3")
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Prepared use of modifier_3.")

        result = handler.use_ability("test_ability")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "No bonus_action remaining to use modifier_3.")

