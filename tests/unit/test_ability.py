import unittest
from unittest.mock import MagicMock, patch
from src.util.constants import EventType
from src.util.time import UseTime
from src.stats.abilities import AbilityIndex, Ability, CompositeAbility

class TestAbility(unittest.TestCase):
    def test_add_ability(self):
        # Create test index and ability
        index = AbilityIndex()
        ability = Ability("test_ability", '''
            function run()
                statblock:restore_hp(10)
            end
        ''')

        # Add ability to index and verify it was added correctly
        index.add(ability)
        self.assertEqual(1, len(index._abilities))
        self.assertEqual(ability, index.get_ability("test_ability"))

    def test_remove_ability(self):
        # Create test index and ability
        index = AbilityIndex()
        ability = Ability("test_ability", '''
            function run()
                statblock:restore_hp(10)
            end
        ''')

        # Add ability to index and verify it was added correctly
        index.add(ability)
        self.assertEqual(1, len(index._abilities))
        self.assertEqual(ability, index.get_ability("test_ability"))

        # Remove ability from index and verify it was removed correctly
        index.remove("test_ability")
        self.assertEqual(0, len(index._abilities))
        with self.assertRaises(ValueError):
            index.get_ability("test_ability")
    
    def test_get_headers(self):
        # Create test index and abilities
        index = AbilityIndex()
        ability_a = Ability("ability_a", "function run() end")
        ability_b = Ability("ability_b", "function run(target) end")
        ability_c = Ability("ability_c", "function run(position) end")

        # Add abilities to index
        index.add(ability_a)
        index.add(ability_b)
        index.add(ability_c)

        # Verify headers are correct
        expected = [
            ("ability_a", ()),
            ("ability_b", ("target",)),
            ("ability_c", ("position",))
        ]
        self.assertEqual(expected, index.get_headers())
    
    def test_get_composite_headers(self):
        # Create test index and composite abilities
        index = AbilityIndex()
        composite = CompositeAbility("composite", "")
        ability_a = Ability("ability_a", "function run() end")
        ability_b = Ability("ability_b", "function run(target) end")

        ability_c = Ability("ability_c", "function run(position) end")

        # Add abilities to composite ability
        composite.add(ability_a)
        composite.add(ability_b)

        # Add composite ability to index
        index.add(composite)
        index.add(ability_c)

        # Verify headers are correct
        expected = [
            ("composite.ability_a", ()),
            ("composite.ability_b", ("target",)),
            ("ability_c", ("position",))
        ]
        self.assertEqual(expected, index.get_headers())

    def test_run_ability(self):
        # Create test index and ability
        index = AbilityIndex()
        ability = Ability("test_ability", '''
            function run()
                return 15
            end
        ''')

        # Add ability to index and run it
        index.add(ability)
        expected = 15
        result = index.run("test_ability", None)

        # Verify ability was run correctly
        self.assertEqual(expected, result)

    def test_run_composite_ability(self):
        # Create test index and composite ability
        index = AbilityIndex()
        composite = CompositeAbility("composite", "")
        ability_a = Ability("ability_a", '''
            function run()
                return 15
            end
        ''')
        ability_b = Ability("ability_b", '''
            function run()
                return 20
            end
        ''')

        ability_c = Ability("ability_c", '''
            function run()
                return 25
            end
        ''')

        # Add abilities to composite ability
        composite.add(ability_a)
        composite.add(ability_b)

        # Add composite ability to index
        index.add(composite)
        index.add(ability_c)
        
        # Run abilities and verify they were run correctly
        expected = 15
        result = index.run("composite.ability_a", None)
        self.assertEqual(expected, result)

        expected = 20
        result = index.run("composite.ability_b", None)
        self.assertEqual(expected, result)

        expected = 25
        result = index.run("ability_c", None)
        self.assertEqual(expected, result)

        # Verify that attempting to run the composite ability itself raises an error
        with self.assertRaises(ValueError):
            index.run("composite", None)
    
    
    def test_run_nested_composite_ability(self):
        # Create test index and composite abilities
        index = AbilityIndex()
        composite = CompositeAbility("composite", "")
        sub_composite = CompositeAbility("sub_composite", "")
        ability_a = Ability("ability_a", '''
            function run()
                return 15
            end
        ''')
        ability_b = Ability("ability_b", '''
            function run()
                return 20
            end
        ''')

        ability_c = Ability("ability_c", '''
            function run()
                return 25
            end
        ''')

        # Add abilities to composite abilities
        composite.add(ability_a)
        composite.add(ability_b)
        sub_composite.add(ability_c)

        # Add composite abilities to composite ability
        composite.add(sub_composite)

        # Add composite ability to index
        index.add(composite)
        
        # Run abilities and verify they were run correctly
        expected = 15
        result = index.run("composite.ability_a", None)
        self.assertEqual(expected, result)

        expected = 20
        result = index.run("composite.ability_b", None)
        self.assertEqual(expected, result)

        expected = 25
        result = index.run("composite.sub_composite.ability_c", None)
        self.assertEqual(expected, result)

        # Verify that attempting to run the composite ability itself raises an error
        with self.assertRaises(ValueError):
            index.run("composite", None)

        # Verify that attempting to run the sub composite ability itself raises an error
        with self.assertRaises(ValueError):
            index.run("composite.sub_composite", None)
    
    def test_run_alternate_function_name(self):
        # Create test index and ability
        index = AbilityIndex()
        ability = Ability("test_ability", '''
            function alternate_function_name()
                return 15
            end
        ''', "alternate_function_name")

        # Add ability to index and run it
        index.add(ability)
        expected = 15
        result = index.run("test_ability", None)

        # Verify ability was run correctly
        self.assertEqual(expected, result)
    
    def test_run_modifier_ability(self):
        # Create test index and abilities
        index = AbilityIndex()
        modifier = Ability("modifier", '''
            can_modify = {"test_ability"}
            
            function modify(amount)
                modified_amount = amount
                return true, "Set modified amount"
            end
        ''', "modify", {"modified_amount": 0})
        ability_a = Ability("test_ability", '''
            function run()
                return modified_amount + 5, "Returning modified amount plus 5"
            end
        ''', "run", {"modified_amount": 0})
        ability_b = Ability("control_ability", '''
            function run()
                return 20
            end
        ''')

        # Add abilities to index
        index.add(modifier)
        index.add(ability_a)
        index.add(ability_b)

        # Run modifier ability in sequence with test ability and verify it was run correctly
        expected = 40
        result = index.run_sequence("test_ability", None, [("modifier", 35)])
        self.assertEqual(expected, result[0])

        # Verify that running the modifier ability on a non-modifiable ability raises an error
        with self.assertRaises(ValueError):
            index.run_sequence("control_ability", None, [("modifier", 35)])

        # Verify that running the modifier ability on it's own raises an error
        with self.assertRaises(ValueError):
            index.run("modifier", None, 35)
        
        # Verify that running the ability on it's own returns the unmodified value
        expected = 5
        result = index.run("test_ability", None)
        self.assertEqual(expected, result[0])
    
    def test_run_composite_modifier(self):
        # Create test index and abilities
        index = AbilityIndex()
        composite = CompositeAbility("composite", "", "", {"modified_amount": 0})
        modifier = Ability("modifier", '''
            can_modify = {"composite"}
                           
            function modify(amount)
                modified_amount = amount
                return true, "Set modified amount"
            end
        ''', "modify")
        ability_a = Ability("ability_a", '''
            function run()
                return modified_amount + 5, "Returning modified amount plus 5"
            end
        ''')
        ability_b = Ability("ability_b", '''
            function run()
                return 20
            end
        ''')

        # Add ability to composite ability
        composite.add(ability_a)

        # Add abilities to index
        index.add(composite)
        index.add(modifier)
        index.add(ability_b)

        # Run modifier ability in sequence with composite ability and verify it was run correctly
        expected = 40
        result = index.run_sequence("composite.ability_a", None, [("modifier", 35)])
        self.assertEqual(expected, result[0])

        # Verify that running the ability on it's own returns the unmodified value
        expected = 5
        result = index.run("composite.ability_a", None)
        self.assertEqual(expected, result[0])

    @patch('src.stats.statblock.Statblock')
    def test_granted_subability(self, StatblockMock):
        ability_index = AbilityIndex()
        effect_script = '''
            test_ability = {
                use_time = UseTime("action"),
                run = function(target)
                    return 15
                end
            }
        '''
        
        # Verify test ability is not in the index
        self.assertNotIn("test_ability", ability_index._abilities.keys())

        # Emit the signal containing the effect data
        ability_index.signal(EventType.EFFECT_GRANTED_ABILITY, "test_ability", effect_script, "run")

        # Verify test ability was added to the index
        self.assertIn("test_ability", ability_index._abilities.keys())

        # Create a mock statblock and target and run the ability on the test target
        statblock = StatblockMock.return_value
        target = StatblockMock.return_value

        expected = 15
        returned = ability_index.run("test_ability", statblock, target)
        self.assertEqual(expected, returned)

        # Emit the signal to remove the ability
        ability_index.signal(EventType.EFFECT_REMOVED_ABILITY, "test_ability")

        # Verify test ability was removed from the index
        self.assertNotIn("test_ability", ability_index._abilities.keys())
    
    @patch('src.stats.statblock.Statblock')
    def test_granted_multiple_subabilities(self, StatblockMock):
        ability_index = AbilityIndex()
        effect_script = '''
            first_ability = {
                use_time = UseTime("action"),
                run = function(target)
                    return 15
                end
            }
            second_ability = {
                use_time = UseTime("bonus_action"),
                run = function(target)
                    return 25
                end
            }
        '''

        # Verify test abilities are not in the index
        self.assertNotIn("first_ability", ability_index._abilities.keys())
        self.assertNotIn("second_ability", ability_index._abilities.keys())

        # Emit the signals containing the effect data
        ability_index.signal(EventType.EFFECT_GRANTED_ABILITY, "first_ability", effect_script, "run")
        ability_index.signal(EventType.EFFECT_GRANTED_ABILITY, "second_ability", effect_script, "run")

        # Verify test abilities were added to the index
        self.assertIn("first_ability", ability_index._abilities.keys())
        self.assertIn("second_ability", ability_index._abilities.keys())

        # Create a mock statblock and run the abilities
        statblock = StatblockMock.return_value
        
        expected = 15
        returned = ability_index.run("first_ability", statblock)
        self.assertEqual(expected, returned)

        expected = 25
        returned = ability_index.run("second_ability", statblock)
        self.assertEqual(expected, returned)

        # Emit the signals to remove the first ability
        ability_index.signal(EventType.EFFECT_REMOVED_ABILITY, "first_ability")

        # Verify the first ability was removed from the index but not the second
        self.assertNotIn("first_ability", ability_index._abilities.keys())
        self.assertIn("second_ability", ability_index._abilities.keys())


    @patch('src.stats.statblock.Statblock')
    def test_statblock_wrapper(self, StatblockMock):
        statblock = StatblockMock.return_value

        # Create test index and abilities
        index = AbilityIndex()
        ability = Ability("test_ability", '''
            spellcasting_ability = "int"

            function run(target)
                return statblock:spell_attack_roll(target, "1d4")
            end
        ''')
        other_ability = Ability("other_ability", '''
            function run(target)
                return statblock:melee_attack_roll(target, "2d4")
            end
        ''')
        incorrect_ability = Ability("incorrect_ability", '''
            function run(target)
                return statblock:spell_attack_roll(target, "2d4")
            end
        ''')

        # Add abilities to index
        index.add(ability)
        index.add(other_ability)
        index.add(incorrect_ability)

        # Run ability and verify it passed the correct arguments to the statblock
        index.run("test_ability", statblock, None)
        self.assertEqual(statblock.ability_attack_roll.call_args[0][0], None)
        self.assertEqual(statblock.ability_attack_roll.call_args[0][1], "int")
        self.assertEqual(statblock.ability_attack_roll.call_args[0][2], "1d4")

        # Run melee ability and verify runs melee attack roll function
        index.run("other_ability", statblock, None)
        self.assertEqual(statblock.melee_attack_roll.call_args[0][1], None)
        self.assertEqual(statblock.melee_attack_roll.call_args[0][2], "2d4")

        # Verify that running a spell attack roll in an ability with no defined spellcasting ability raises an error
        with self.assertRaises(ValueError):
            index.run("incorrect_ability", statblock, None)

    def test_use_time(self):
        # Create test index and abilities
        index = AbilityIndex()
        ability_action = Ability("test_ability", '''
            use_time = UseTime("action")
        ''')
        ability_bonus_action = Ability("test_ability", '''
            use_time = UseTime("bonus_action")
        ''')
        ability_reaction = Ability("test_ability", '''
            use_time = UseTime("reaction")
        ''')
        ability_minute = Ability("test_ability", '''
            use_time = UseTime("minute")
        ''')
        ability_minutes = Ability("test_ability", '''
            use_time = UseTime("minute", 5)
        ''')
        ability_hour = Ability("test_ability", '''
            use_time = UseTime("hour")
        ''')
        ability_hours = Ability("test_ability", '''
            use_time = UseTime("hour", 3)
        ''')
        
        self.assertTrue(ability_action._use_time.is_special)
        self.assertTrue(ability_action._use_time.is_action)
        self.assertFalse(ability_action._use_time.is_bonus_action)
        self.assertFalse(ability_action._use_time.is_reaction)
        self.assertEqual(UseTime.Special.Action.value, ability_action._use_time.minutes)

        self.assertTrue(ability_bonus_action._use_time.is_special)
        self.assertFalse(ability_bonus_action._use_time.is_action)
        self.assertTrue(ability_bonus_action._use_time.is_bonus_action)
        self.assertFalse(ability_bonus_action._use_time.is_reaction)
        self.assertEqual(UseTime.Special.BonusAction.value, ability_bonus_action._use_time.minutes)

        self.assertTrue(ability_reaction._use_time.is_special)
        self.assertFalse(ability_reaction._use_time.is_action)
        self.assertFalse(ability_reaction._use_time.is_bonus_action)
        self.assertTrue(ability_reaction._use_time.is_reaction)
        self.assertEqual(UseTime.Special.Reaction.value, ability_reaction._use_time.minutes)

        self.assertFalse(ability_minute._use_time.is_special)
        self.assertFalse(ability_minute._use_time.is_action)
        self.assertFalse(ability_minute._use_time.is_bonus_action)
        self.assertFalse(ability_minute._use_time.is_reaction)
        self.assertEqual(1, ability_minute._use_time.minutes)

        self.assertFalse(ability_minutes._use_time.is_special)
        self.assertFalse(ability_minutes._use_time.is_action)
        self.assertFalse(ability_minutes._use_time.is_bonus_action)
        self.assertFalse(ability_minutes._use_time.is_reaction)
        self.assertEqual(5, ability_minutes._use_time.minutes)

        self.assertFalse(ability_hour._use_time.is_special)
        self.assertFalse(ability_hour._use_time.is_action)
        self.assertFalse(ability_hour._use_time.is_bonus_action)
        self.assertFalse(ability_hour._use_time.is_reaction)
        self.assertEqual(60, ability_hour._use_time.minutes)

        self.assertFalse(ability_hours._use_time.is_special)
        self.assertFalse(ability_hours._use_time.is_action)
        self.assertFalse(ability_hours._use_time.is_bonus_action)
        self.assertFalse(ability_hours._use_time.is_reaction)
        self.assertEqual(180, ability_hours._use_time.minutes)