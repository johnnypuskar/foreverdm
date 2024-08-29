import unittest
from unittest.mock import patch
from src.stats.effects import EffectIndex, Effect, SubEffect

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
                return RollResult({bonus = 5})
            end
        ''')
        effect_b = Effect("effect_b", '''
            function make_attack_roll(target)
                return RollResult({bonus = -2})
            end
        ''')   
        effect_c = Effect("effect_c", '''
            function receive_attack_roll(attacker)
                return RollResult({auto_fail = true})
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
            subeffects = {
                test_subeffect = {
                    receive_attack_roll = function(attacker)
                        return RollResult({auto_fail = true})
                    end
                }
            }

            function make_attack_roll(target)
                return RollResult({bonus = 5})
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
    
    @patch('src.stats.statblock.Statblock')
    def test_statblock_wrapper(self, StatblockMock):
        statblock = StatblockMock.return_value

        # Create test index and effect and add effect into index
        index = EffectIndex()
        effect = Effect("test_effect", '''
            subeffects = {
                test_subeffect = {
                    receive_attack_roll = function(attacker)
                        return RollResult({auto_fail = true})
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


