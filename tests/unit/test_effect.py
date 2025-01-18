import unittest
from unittest.mock import patch
from src.util.constants import EventType
from src.stats.effects import Effect, SubEffect
from src.stats.effect_index import EffectIndex

class TestEffect(unittest.TestCase):
    def test_add_effect(self):
        index = EffectIndex()
        effect = Effect("effect_a", "")

        index.add(effect, 1)

        self.assertTrue(effect in index._effects.values())

    def test_function_run(self):
        index = EffectIndex()
        effect_a = Effect("effect_a", '''
            function make_attack_roll(target)
                return RollModifier({bonus = 5})
            end
        ''')
        effect_b = Effect("effect_b", '''
            function make_attack_roll(target)
                return RollModifier({bonus = -2})
            end
        ''')   
        effect_c = Effect("effect_c", '''
            function receive_attack_roll(attacker)
                return RollModifier({auto_fail = true})
            end
        ''')
        index.add(effect_a, 1)
        index.add(effect_b, 1)
        index.add(effect_c, 1)

        self.assertTrue(effect_a in index._effects.values())
        self.assertTrue(effect_b in index._effects.values())
        self.assertTrue(effect_c in index._effects.values())

        results = index.get_function_results("make_attack_roll", None, None)
        expected = [
            {'disadvantage': False, 'advantage': False, 'auto_succeed': False, 'auto_fail': False, 'bonus': 5},
            {'disadvantage': False, 'advantage': False, 'auto_succeed': False, 'auto_fail': False, 'bonus': -2}
        ]

        self.assertEqual(results, expected)

        results = index.get_function_results("receive_attack_roll", None, None)
        expected = [
            {'disadvantage': False, 'advantage': False, 'auto_succeed': False, 'auto_fail': True, 'bonus': 0}
        ]

        self.assertEqual(results, expected)

    @patch('src.stats.statblock.Statblock')
    def test_subeffect(self, StatblockMock):
        statblock = StatblockMock.return_value

        # Create test index and effect
        index = EffectIndex()
        effect = Effect("test_effect", '''
            test_subeffect = {
                receive_attack_roll = function(attacker)
                    return RollModifier({auto_fail = true})
                end
            }

            function make_attack_roll(target)
                return RollModifier({bonus = 5})
            end
                        
            function end_turn()
                statblock:add_effect("test_subeffect", 1)
            end
        ''')

        # Add initial effect and verify it was added
        index.add(effect, 1)
        self.assertEqual(1, len(index._effects))

        # Verify effect is returning typical function results correctly
        results = index.get_function_results("make_attack_roll", None, None)
        expected = [
            {'disadvantage': False, 'advantage': False, 'auto_succeed': False, 'auto_fail': False, 'bonus': 5}
        ]
        self.assertEqual(results, expected)

        # Verify effect does not have any results for the function defined in the subeffect
        results = index.get_function_results("receive_attack_roll", None, None)
        expected = []
        self.assertEqual(results, expected)

        # Run the function to attempt to apply the subeffect
        index.get_function_results("end_turn", statblock, None)

        # Verify the subeffect was applied correctly to the statblock mock, and insert it into the test index manually
        statblock.add_effect.assert_called_once()
        subeffect = statblock.add_effect.call_args[0][0]
        statblock.add_effect.assert_called_with(subeffect, 1)
        index.add(subeffect, 1)
        
        # Verify that the effect index now has two effects
        self.assertEqual(2, len(index._effects))

        # Verify that the original typical function results are still returned correctly
        results = index.get_function_results("make_attack_roll", None, None)
        expected = [
            {'disadvantage': False, 'advantage': False, 'auto_succeed': False, 'auto_fail': False, 'bonus': 5}
        ]
        self.assertEqual(results, expected)

        # Verify that the subeffect now has results for the function defined in the subeffect
        results = index.get_function_results("receive_attack_roll", None, None)
        expected = [
            {'disadvantage': False, 'advantage': False, 'auto_succeed': False, 'auto_fail': True, 'bonus': 0}
        ]
        self.assertEqual(results, expected)
    
    def test_granted_subeffect(self):
        effect_index = EffectIndex()
        ability_script = '''
            ability_effect = {
                make_attack_roll = function(target)
                    return RollModifier({bonus = 5})
                end
            }
        '''

        # Verify test effect is not in the effect index
        self.assertNotIn("ability_effect", effect_index.effect_names)

        # Verify there is no effect on the function results
        expected = []
        results = effect_index.get_function_results("make_attack_roll", None, None)
        self.assertEqual(results, expected)

        # Emit the signal containing the effect data
        effect_index.signal(EventType.ABILITY_APPLIED_EFFECT, "ability_effect", ability_script, 1, {}, "")

        # Verify test effect was added to the index
        self.assertIn("ability_effect", effect_index.effect_names)

        # Verify that the effect has the expected function results
        expected = [
            {'disadvantage': False, 'advantage': False, 'auto_succeed': False, 'auto_fail': False, 'bonus': 5}
        ]
        results = effect_index.get_function_results("make_attack_roll", None, None)
        self.assertEqual(results, expected)

        # Emit the signal to remove the effect
        effect_index.signal(EventType.ABILITY_REMOVED_EFFECT, "ability_effect", 1, {})

        # Verify the effect was removed from the index
        self.assertNotIn("ability_effect", effect_index.effect_names)

    def test_granted_multiple_subeffects(self):
        effect_index = EffectIndex()
        ability_script = '''
            first_effect = {
                make_attack_roll = function(target)
                    return RollModifier({bonus = 5})
                end
            }
            second_effect = {
                make_attack_roll = function(target)
                    return RollModifier({bonus = -2})
                end
            }
        '''

        # Verify test effects are not in the effect index
        self.assertNotIn("first_effect", effect_index.effect_names)
        self.assertNotIn("second_effect", effect_index.effect_names)

        # Verify there is no effect on the function results
        expected = []
        results = effect_index.get_function_results("make_attack_roll", None, None)

        # Emit the signal containing the effect data
        effect_index.signal(EventType.ABILITY_APPLIED_EFFECT, "first_effect", ability_script, 1, {}, "")
        effect_index.signal(EventType.ABILITY_APPLIED_EFFECT, "second_effect", ability_script, 1, {}, "")

        # Verify test effects were added to the index
        self.assertIn("first_effect", effect_index.effect_names)
        self.assertIn("second_effect", effect_index.effect_names)

        # Verify that the effects have the expected function results
        expected = [
            {'disadvantage': False, 'advantage': False, 'auto_succeed': False, 'auto_fail': False, 'bonus': 5},
            {'disadvantage': False, 'advantage': False, 'auto_succeed': False, 'auto_fail': False, 'bonus': -2}
        ]
        results = effect_index.get_function_results("make_attack_roll", None, None)
        self.assertEqual(results, expected)

        # Emit the signal to remove the first effect
        effect_index.signal(EventType.ABILITY_REMOVED_EFFECT, "first_effect")

        # Verify only the first effect was removed from the index
        self.assertNotIn("first_effect", effect_index.effect_names)
        self.assertIn("second_effect", effect_index.effect_names)

    def test_concentration_breaking_effects(self):
        # Create test index and ability_script
        index = EffectIndex()
        ability_script = '''
            use_time = UseTime("action", 1)
            spell_duration = Duration("round", 3)
            spell_concentration = true
            
            test_effect = {
                make_attack_roll = function(target) return RollModifier({bonus = 5}) end
            }
            alt_effect ={
                make_ability_check = function(target) return RollModifier({bonus = 1}) end
            }
        '''
        effect = Effect("static_effect", '''
            function make_attack_roll(target) return RollModifier({bonus = -3}) end
        ''')

        # Add the static effect to the index
        index.add(effect, 10)

        # Verify test effect is not in the effect index
        self.assertNotIn("test_effect", index.effect_names)

        # Emit the signal containing the effect data
        TEST_UUID = "test_uuid"
        index.signal(EventType.ABILITY_APPLIED_EFFECT, "test_effect", ability_script, 3, {}, TEST_UUID)
        index.signal(EventType.ABILITY_APPLIED_EFFECT, "alt_effect", ability_script, 3, {}, TEST_UUID)

        # Verify test effect was added to the index
        self.assertIn("test_effect", index.effect_names)
        self.assertIn("alt_effect", index.effect_names)

        # Verify that the effect has the expected function results
        expected = [
            {'disadvantage': False, 'advantage': False, 'auto_succeed': False, 'auto_fail': False, 'bonus': -3},
            {'disadvantage': False, 'advantage': False, 'auto_succeed': False, 'auto_fail': False, 'bonus': 5}
        ]
        results = index.get_function_results("make_attack_roll", None, None)
        self.assertEqual(results, expected)

        expected = [
            {'disadvantage': False, 'advantage': False, 'auto_succeed': False, 'auto_fail': False, 'bonus': 1}
        ]
        results = index.get_function_results("make_ability_check", None, None)
        self.assertEqual(results, expected)

        # Emit the broken concentration signal and verify the concentration effect was removed
        index.signal(EventType.ABILITY_CONCENTRATION_ENDED, TEST_UUID)

        self.assertNotIn("test_effect", index.effect_names)
        self.assertNotIn("alt_effect", index.effect_names)

        expected = [
            {'disadvantage': False, 'advantage': False, 'auto_succeed': False, 'auto_fail': False, 'bonus': -3}
        ]
        results = index.get_function_results("make_attack_roll", None, None)
        self.assertEqual(results, expected)

        expected = []
        results = index.get_function_results("make_ability_check", None, None)
        self.assertEqual(results, expected)
            

    @patch('src.stats.statblock.Statblock')
    def test_statblock_wrapper(self, StatblockMock):
        statblock = StatblockMock.return_value

        # Create test index and effect and add effect into index
        index = EffectIndex()
        effect = Effect("test_effect", '''
            subeffects = {
                test_subeffect = {
                    receive_attack_roll = function(attacker)
                        return RollModifier({auto_fail = true})
                    end
                }
            }

            function make_attack_roll(target)
                statblock:restore_hp(10)
            end
                        
            function multiple_parameters(foo, bar)
                statblock:multi_param(foo, bar)
            end
                        
            function receive_attack_roll(attacker)
                statblock:add_effect("test_subeffect", 1)
            end
        ''')
        index.add(effect, 1)

        # Verify that a typical function call passes the arguments through normally
         # Note: Due to the wrapper, the call parameters on the mock are indexed up by 1
        index.get_function_results("make_attack_roll", statblock, None)
        statblock.restore_hp.assert_called_once()
        self.assertEqual(statblock.restore_hp.call_args[0][1], 10)

        # Verify that multiple parameters are passed through correctly
         # Note: Due to the wrapper, the call parameters on the mock are indexed up by 1
        index.get_function_results("multiple_parameters", statblock, 15, -20)
        statblock.multi_param.assert_called_once()
        self.assertEqual(statblock.multi_param.call_args[0][1], 15)
        self.assertEqual(statblock.multi_param.call_args[0][2], -20)

        # Verify that the wrapper add_effect call correctly passes a SubEffect object into the Statblock add_effect arguments
        index.get_function_results("receive_attack_roll", statblock, None)
        statblock.add_effect.assert_called_once()
        self.assertEqual(type(statblock.add_effect.call_args[0][0]), SubEffect)

    @patch('src.stats.statblock.Statblock')
    @patch('src.stats.statblock.Statblock')
    def test_statblock_reference(self, StatblockMock2, StatblockMock1):
        index = EffectIndex()

        # Create two reference statblocks with different behaviors
        reference_statblock = StatblockMock1.return_value
        new_reference_statblock = StatblockMock2.return_value

        effect = Effect("test_effect", '''
            function start_turn()
                reference:restore_hp(10)
            end
                        
            function change_reference(target)
                SetGlobal("reference", target)
            end
        ''', {"reference": reference_statblock})

        # Add effect to index and verify it was added
        index.add(effect, 1)
        self.assertIn("test_effect", index.effect_names)
        self.assertEqual(effect._globals["reference"]._statblock, reference_statblock)

        # Verify that the reference statblock was called correctly
        index.get_function_results("start_turn", None, None)
        reference_statblock.restore_hp.assert_called_once()
        new_reference_statblock.restore_hp.assert_not_called()

        # Verify that the reference was changed
        index.get_function_results("change_reference", None, new_reference_statblock)
        self.assertEqual(effect._globals["reference"]._statblock, new_reference_statblock)

        # Reset the first mock's call count to verify it's not called again
        reference_statblock.restore_hp.reset_mock()

        # Verify that the new reference statblock was called correctly
        index.get_function_results("start_turn", None, None)
        new_reference_statblock.restore_hp.assert_called_once()
        reference_statblock.restore_hp.assert_not_called()

    def test_effect_duration(self):
        effect = Effect("test_effect", "")

        # Tick the effect and check duration
        effect.tick_timer()
        self.assertEqual(effect.duration, -1)

        # Add effect to index and tick
        index = EffectIndex()
        index.add(effect, 5)
        self.assertEqual(effect.duration, 5)
        index.tick_timers(None)
        self.assertEqual(effect.duration, 4)

        # Add a second effect and tick the index
        effect2 = Effect("test_effect_2", "")
        index.add(effect2, 10)
        index.tick_timers(None)

        self.assertEqual(effect.duration, 3)
        self.assertEqual(effect2.duration, 9)

    @patch('src.stats.statblock.Statblock')
    def test_effect_on_apply(self, StatblockMock):
        index = EffectIndex()
        effect = Effect("test_effect", '''
            function on_apply()
                statblock:restore_hp(10)
            end
        ''')

        # Add effect to index and verify it was added
        statblock = StatblockMock.return_value
        index.add(effect, 1, statblock)
        self.assertIn("test_effect", index.effect_names)

        # Verify on_apply function was called
        statblock.restore_hp.assert_called_once()
    
    @patch('src.stats.statblock.Statblock')
    def test_effect_expiry(self, StatblockMock):
        index = EffectIndex()
        effect = Effect("test_effect", "")

        # Add effect to index and verify it was added
        index.add(effect, 1)
        self.assertIn("test_effect", index.effect_names)
        
        # Tick the index and verify the effect was removed
        self.assertEqual(effect.duration, 1)
        index.tick_timers(None)
        self.assertNotIn("test_effect", index.effect_names)


        # Create effect with on_expire function and add to index
        effect_expires = Effect("test_effect", '''
            function on_expire()
                statblock:restore_hp(10)
            end
        ''')
        statblock = StatblockMock.return_value
        index.add(effect_expires, 2)

        # Tick the index and verify the effect was removed and the on_expire function was called when duration reaches 0
        self.assertIn("test_effect", index.effect_names)
        statblock.restore_hp.assert_not_called()

        # Tick once to reduce duration to 1 and verify on_expire was not called
        index.tick_timers(statblock)
        statblock.restore_hp.assert_not_called()

        # Tick again to remove the effect and verify on_expire was called
        index.tick_timers(statblock)
        self.assertNotIn("test_effect", index.effect_names)
        statblock.restore_hp.assert_called_once()
        self.assertEqual(statblock.restore_hp.call_args[0][1], 10)
    
    @patch('src.stats.statblock.Statblock')
    def test_effect_add_condition(self, StatblockMock):
        index = EffectIndex()
        statblock = StatblockMock.return_value
        effect = Effect("test_effect", '''
            function make_attack_roll(target)
                statblock.add_condition("poisoned", 3)
            end
        ''')

        index.add(effect, 1)

        index.get_function_results("make_attack_roll", statblock, None)

        statblock._effects._condition_manager.new_condition.assert_called_once()
        condition_name, parent_effect_name, duration = statblock._effects._condition_manager.new_condition.call_args[0]
        self.assertEqual(condition_name, "poisoned")
        self.assertEqual(parent_effect_name, None)
        self.assertEqual(duration, 3)

    def test_effect_derived_conditions(self):
        index = EffectIndex()

        effect = Effect("test_effect", '''
            conditions = {"poisoned"}
        ''')

        index.add(effect, 5)

        self.assertIn("test_effect%poisoned", index.effect_names)

        expected = [{"disadvantage": True, "advantage": False, "auto_succeed": False, "auto_fail": False, "bonus": 0}]
        result = index.get_function_results("make_attack_roll", None, None)
        self.assertEqual(result, expected)

        with self.assertRaises(ValueError):
            index.remove("test_effect%poisoned")

        index.remove("test_effect")

        self.assertNotIn("test_effect%poisoned", index.effect_names)

    def test_script_helpers(self):
        index = EffectIndex()
        effect = Effect("test_effect", '''
            function add_value()
                return AddValue(10)
            end
                        
            function set_value()
                return SetValue(20)
            end
                        
            function multiply_value()
                return MultiplyValue(30)
            end

            function speed_modifier()
                return SpeedModifier({walk = AddValue(10)})
            end
                        
            function roll_modifier()
                return RollModifier({advantage = true, bonus = 5})
            end
                        
            function duration()
                return Duration("round", 3)
            end    
        ''')

        index.add(effect, 1)

        # Verify that AddValue works
        expected = {"operation": "add", "value": 10}
        results = index.get_function_results("add_value", None, None)[0]
        self.assertDictEqual(results, expected)

        # Verify that SetValue works
        expected = {"operation": "set", "value": 20}
        results = index.get_function_results("set_value", None, None)[0]
        self.assertDictEqual(results, expected)

        # Verify that MultiplyValue works
        expected = {"operation": "multiply", "value": 30}
        results = index.get_function_results("multiply_value", None, None)[0]
        self.assertDictEqual(results, expected)

        # Verify that SpeedModifier works
        expected = {
            "walk": {"operation": "add", "value": 10},
            "fly": {"operation": "add", "value": 0},
            "swim": {"operation": "add", "value": 0},
            "climb": {"operation": "add", "value": 0},
            "burrow": {"operation": "add", "value": 0}
        }
        results = index.get_function_results("speed_modifier", None, None)[0]
        
        # Compare dictionary contents instead of direct equality
        # Compare dictionary contents instead of direct equality
        self.assertEqual(set(results.keys()), set(expected.keys()))
        for key in expected:
            self.assertDictEqual(results[key], expected[key])

        # Verify that RollModifier works
        expected = {
            "disadvantage": False,
            "advantage": True,
            "auto_succeed": False,
            "auto_fail": False,
            "bonus": 5
        }
        results = index.get_function_results("roll_modifier", None, None)[0]
        self.assertDictEqual(results, expected)

        # Verify that Duration works
        expected = {"unit": "round", "value": 3}
        results = index.get_function_results("duration", None, None)[0]
        self.assertDictEqual(results, expected)





