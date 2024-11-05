import unittest
from unittest.mock import patch
from src.util.constants import EventType
from src.util.time import UseTime
from src.stats.abilities import AbilityIndex, Ability, CompositeAbility, SubAbility

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

        # Test name character restriction
        with self.assertRaises(ValueError):
            Ability("^continue", "")

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
    
    def test_get_active_use_headers(self):
        # Create test index and abilities
        index = AbilityIndex()
        ability_a = Ability("ability_a", '''
            use_time = UseTime("minute", 1)
            
            function run()
                return 15
            end
        ''')
        ability_b = Ability("ability_b", '''
            use_time = UseTime("minute", 2)
            
            function run(target)
                return 15
            end
        ''')
        ability_c = Ability("ability_c", '''
            use_time = UseTime("action", 1)
                            
            function run(position)
                return 15
            end
        ''')
        
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

        # Start using ability and verify use timer began and active use headers are split correctly
        run_result = index.run("ability_a", None)
        expected = (False, "Preparing to use ability_a, 9 turns remaining.")
        self.assertEqual(expected, run_result)

        expected = [
            ("^continue.ability_a", ()),
            ("^new_use.ability_a", ()),
            ("ability_b", ("target",)),
            ("ability_c", ("position",))
        ]
        self.assertEqual(expected, index.get_headers())

        # Run different ability and verify active use headers are changed and split correctly
        run_result = index.run("ability_b", None)
        expected = (False, "Preparing to use ability_b, 19 turns remaining.")
        self.assertEqual(expected, run_result)

        expected = [
            ("ability_a", ()),
            ("^continue.ability_b", ("target",)),
            ("^new_use.ability_b", ("target",)),
            ("ability_c", ("position",))
        ]
        self.assertEqual(expected, index.get_headers())

        # Run ability with single action use time and verify active use ability is not set and headers are reset
        run_result = index.run("ability_c", None)
        expected = 15
        self.assertEqual(expected, run_result)

        expected = [
            ("ability_a", ()),
            ("ability_b", ("target",)),
            ("ability_c", ("position",))
        ]
        self.assertEqual(expected, index.get_headers())

    def test_active_use_headers_sequence(self):
        # Create test index and abilities
        index = AbilityIndex()
        modifier = Ability("modifier", '''
            can_modify = {"test_ability", "control_ability"}
            
            function modify(amount)
                modified_amount = amount
                return true, "Set modified amount"
            end
        ''', "modify", {"modified_amount": 0})
        ability_a = Ability("test_ability", '''
            use_time = UseTime("minute", 1)
            
            function run()
                return modified_amount + 5, "Returning modified amount plus 5"
            end
        ''', "run", {"modified_amount": 0})
        ability_b = Ability("control_ability", '''
            use_time = UseTime("minute", 2)
            
            function run()
                return modified_amount + 20
            end
        ''', "run", {"modified_amount": 0})

        # Add abilities to index
        index.add(modifier)
        index.add(ability_a)
        index.add(ability_b)

        # Verify initial headers
        expected = [
            ("modifier", ("amount",)),
            ("test_ability", ()),
            ("control_ability", ())
        ]
        self.assertEqual(expected, index.get_headers())

        # Run sequence and verify use timer began and active use headers are split correctly
        run_result = index.run_sequence("test_ability", None, [("modifier", 35)])
        expected = (False, "Preparing to use test_ability, 9 turns remaining.")
        self.assertEqual(expected, run_result)

        expected = [
            ("modifier", ("amount",)),
            ("^continue.test_ability", ()),
            ("^new_use.test_ability", ()),
            ("control_ability", ())
        ]
        self.assertEqual(expected, index.get_headers())

        # Run different ability sequence and verify active use headers are changed
        run_result = index.run_sequence("control_ability", None, [("modifier", 35)])
        expected = (False, "Preparing to use control_ability, 19 turns remaining.")
        self.assertEqual(expected, run_result)

        expected = [
            ("modifier", ("amount",)),
            ("test_ability", ()),
            ("^continue.control_ability", ()),
            ("^new_use.control_ability", ())
        ]
        self.assertEqual(expected, index.get_headers())

        # Verify that running the modifier ability on it's own raises an error and does not change headers
        with self.assertRaises(ValueError):
            index.run("modifier", None, 35)
        self.assertEqual(expected, index.get_headers())    

    def test_active_use_headers_composite(self):
        # Create test index and composite abilities
        index = AbilityIndex()
        composite = CompositeAbility("composite", "")
        ability_a = Ability("ability_a", '''
            use_time = UseTime("minute", 1)
            
            function run()
                return 15
            end
        ''')
        ability_b = Ability("ability_b", '''
            use_time = UseTime("minute", 2)
            
            function run(target)
                return 20
            end
        ''')
        ability_c = Ability("ability_c", '''
            use_time = UseTime("action", 1)
            
            function run(position)
                return 25
            end
        ''')

        # Add abilities to composite ability
        composite.add(ability_a)
        composite.add(ability_b)

        # Add composite ability and standalone ability to index
        index.add(composite)
        index.add(ability_c)

        # Verify initial headers are correct
        expected = [
            ("composite.ability_a", ()),
            ("composite.ability_b", ("target",)),
            ("ability_c", ("position",))
        ]
        self.assertEqual(expected, index.get_headers())

        # Start using composite ability and verify use timer began and active use headers are split correctly
        run_result = index.run("composite.ability_a", None)
        expected = (False, "Preparing to use composite.ability_a, 9 turns remaining.")
        self.assertEqual(expected, run_result)

        expected = [
            ("^continue.composite.ability_a", ()),
            ("^new_use.composite.ability_a", ()),
            ("composite.ability_b", ("target",)),
            ("ability_c", ("position",))
        ]
        self.assertEqual(expected, index.get_headers())

        # Run different composite ability and verify active use headers are changed
        run_result = index.run("composite.ability_b", None)
        expected = (False, "Preparing to use composite.ability_b, 19 turns remaining.")
        self.assertEqual(expected, run_result)

        expected = [
            ("composite.ability_a", ()),
            ("^continue.composite.ability_b", ("target",)),
            ("^new_use.composite.ability_b", ("target",)),
            ("ability_c", ("position",))
        ]
        self.assertEqual(expected, index.get_headers())

        # Run ability with single action use time and verify active use ability is not set and headers are reset
        run_result = index.run("ability_c", None)
        expected = 25
        self.assertEqual(expected, run_result)

        expected = [
            ("composite.ability_a", ()),
            ("composite.ability_b", ("target",)),
            ("ability_c", ("position",))
        ]
        self.assertEqual(expected, index.get_headers())

    def test_active_use_ability_counter(self):
        # Create test index and abilities
        index = AbilityIndex()
        ability_a = Ability("ability_a", '''
            use_time = UseTime("minute", 1)

            function run()
                return 15
            end
        ''')
        ability_b = Ability("ability_b", '''
            use_time = UseTime("minute", 2)
            
            function run(target)
                return 20
            end
        ''')

        # Add abilities to index
        index.add(ability_a)
        index.add(ability_b)

        # Use ability and verify use timer began
        expected = (False, "Preparing to use ability_a, 9 turns remaining.")
        result = index.run("ability_a", None)
        self.assertEqual(expected, result)

        # Verify attempting to use the default name throws a value error
        with self.assertRaises(ValueError):
            index.run("ability_a", None)
        
        # Continue ability use and verify use timer is decremented
        expected = (False, "Preparing to use ability_a, 8 turns remaining.")
        result = index.run("^continue.ability_a", None)
        self.assertEqual(expected, result)

        # Verify using a different ability starts it's own counter properly
        expected = (False, "Preparing to use ability_b, 19 turns remaining.")
        result = index.run("ability_b", None)
        self.assertEqual(expected, result)

        # Start new ability use and verify use timer is reset
        expected = (False, "Preparing to use ability_a, 9 turns remaining.")
        result = index.run("^new_use.ability_a", None)
        self.assertEqual(expected, result)

        # Run ability time down to completion by calling 10 times and verify it gets run
        self.assertFalse(index.run("^continue.ability_a", None)[0])
        self.assertFalse(index.run("^continue.ability_a", None)[0])
        self.assertFalse(index.run("^continue.ability_a", None)[0])
        self.assertFalse(index.run("^continue.ability_a", None)[0])
        self.assertFalse(index.run("^continue.ability_a", None)[0])
        self.assertFalse(index.run("^continue.ability_a", None)[0])
        self.assertFalse(index.run("^continue.ability_a", None)[0])
        self.assertFalse(index.run("^continue.ability_a", None)[0])
        
        expected = 15
        result = index.run("^continue.ability_a", None)
        self.assertEqual(expected, result)

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

    def test_validate_ability(self):
        # Create test index and abilities
        index = AbilityIndex()
        ability = Ability("test_ability", '''
            function validate(target)
                if target > 10 then
                    return false, "Target must be less than 10"
                end
                return true, nil
            end
                          
            function run(target)
                return 10
            end
        ''')

        # Add ability to index
        index.add(ability)

        # Verify that running the ability with a valid target returns the correct value
        expected = 10
        result = index.run("test_ability", None, 5)
        self.assertEqual(expected, result)

        # Verify that running the ability with an invalid target return false and the failed validation message
        expected = (False, "Target must be less than 10")
        result = index.run("test_ability", None, 15)
        self.assertEqual(expected, result)
        
    def test_validate_composite_ability(self):
        # Create test index and composite abilities
        index = AbilityIndex()
        composite = CompositeAbility("composite", "")
        ability_a = Ability("ability_a", '''
            function validate(target)
                if target > 10 then
                    return false, "Target must be less than 10"
                end
                return true, nil
            end
                          
            function run(target)
                return 10
            end
        ''')
        ability_b = Ability("ability_b", '''
            function validate(target)
                if target <= 10 then
                    return false, "Target must be greater or equal to than 10"
                end
                return true, nil
            end

            function run(target)
                return 20
            end
        ''')

        # Add abilities to composite ability
        composite.add(ability_a)
        composite.add(ability_b)

        # Add composite ability to index
        index.add(composite)

        # Verify that running the abilities with a valid target returns the correct value
        expected = 10
        result = index.run("composite.ability_a", None, 5)
        self.assertEqual(expected, result)

        expected = 20
        result = index.run("composite.ability_b", None, 15)
        self.assertEqual(expected, result)

        # Verify that running the abilities with an invalid target return false and the failed validation message
        expected = (False, "Target must be less than 10")
        result = index.run("composite.ability_a", None, 15)
        self.assertEqual(expected, result)

        expected = (False, "Target must be greater or equal to than 10")
        result = index.run("composite.ability_b", None, 5)
        self.assertEqual(expected, result)

    def test_validate_modifier_ability(self):
        # Create test index and abilities
        index = AbilityIndex()
        modifier = Ability("modifier", '''
            can_modify = {"test_ability"}
            
            function validate(amount)
                if amount > 10 then
                    return false, "Amount must be less than 10"
                end
                return true, nil
            end
                          
            function modify(amount)
                modified_amount = amount
                return true, "Set modified amount"
            end
        ''', "modify", {"modified_amount": 0})
        ability = Ability("test_ability", '''
            function run(amount)
                return modified_amount + amount, "Returning modified amount plus parameter"
            end
        ''', "run", {"modified_amount": 0})

        # Add abilities to index
        index.add(modifier)
        index.add(ability)

        # Verify that running the ability alone works
        expected = 5
        result = index.run("test_ability", None, 5)
        self.assertEqual(expected, result[0])

        # Verify that running the ability with a valid amount modifier works
        expected = 10
        result = index.run_sequence("test_ability", None, [("modifier", 5)], 5)
        self.assertEqual(expected, result[0])

        # Verify that running the ability with an invalid amount modifier returns false and the failed validation message
        expected = (False, "Amount must be less than 10")
        result = index.run_sequence("test_ability", None, [("modifier", 15)], 5)
        self.assertEqual(expected, result)
    
    def test_validate_subability(self):
        # Create test index and abilities
        index = AbilityIndex()
        subability = SubAbility("subability", '''
            subability = {
                validate = function(target)
                    if target > 10 then
                        return false, "Target must be less than 10"
                    end
                    return true, nil
                end,
                use_time = UseTime("action"),
                run = function(target)
                    return -20
                end
            }
                                
            function validate(target)
                return true, nil
            end
        ''')
        
        # Add subability to index
        index.add(subability)

        # Verify that running the subability with a valid target returns the correct value
        expected = -20
        result = index.run("subability", None, 5)
        self.assertEqual(expected, result)

        # Verify that running the subability with an invalid target return false and the failed validation message
        expected = (False, "Target must be less than 10")
        result = index.run("subability", None, 15)
        self.assertEqual(expected, result)
        

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