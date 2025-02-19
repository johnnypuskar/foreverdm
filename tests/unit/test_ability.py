import unittest
from unittest.mock import MagicMock, patch
from src.stats.wrappers.statblock_ability_wrapper import StatblockAbilityWrapper
from src.util.constants import EventType
from src.util.time import UseTime
from src.stats.abilities.ability import Ability, ReactionAbility
from src.stats.abilities.ability_index import AbilityIndex
from src.stats.abilities.composite_ability import CompositeAbility
from src.stats.abilities.sub_ability import SubAbility
from src.util.return_status import ReturnStatus

class TestAbilityInstancing(unittest.TestCase):
    INDEX = None
    STATBLOCK = None

    @patch('src.stats.statblock.Statblock')
    def setUp(self, statblock):
        self.INDEX = AbilityIndex()
        self.STATBLOCK = statblock

    def test_create_ability_name_error(self):
        with self.assertRaises(ValueError):
            Ability("^continue", "")
        
        with self.assertRaises(ValueError):
            Ability("making$$$", "")
        
        ability = Ability("test_ability", "")
        self.assertEqual("test_ability", ability._name)
    
    def test_reaction_ability_class_instancing(self):
        ability_reaction = Ability("test_ability_reaction", '''
            use_time = UseTime("reaction", 1)
            reaction_trigger = "test_event"
                                      
            function run()
                return true, "Used test_ability_reaction."
            end
        ''')
        ability_action = Ability("test_ability_action", '''
            use_time = UseTime("action", 1)
                                      
            function run()
                return true, "Used test_ability_action."
            end
        ''')

        self.assertTrue(isinstance(ability_reaction, ReactionAbility))
        self.assertFalse(isinstance(ability_action, ReactionAbility))
    
    def test_global_values(self):
        ability = Ability("test_ability", '''
            use_time = UseTime("action", 1)
            used = 0
            
            function run()
                used = used + 1
                return true, "Used test_ability."
            end
        ''')
        self.INDEX.add(ability)

        self.assertEqual(0, ability._globals['used'])
        self.INDEX.run_ability("test_ability", self.STATBLOCK)
        self.assertEqual(1, ability._globals['used'])
        self.INDEX.run_ability("test_ability", self.STATBLOCK)
        self.INDEX.run_ability("test_ability", self.STATBLOCK)
        self.assertEqual(3, ability._globals['used'])
    
    def test_use_time(self):
        # Create test index and abilities
        ability_action = Ability("test_ability", '''
            use_time = UseTime("action")
        ''')
        ability_bonus_action = Ability("test_ability", '''
            use_time = UseTime("bonus_action")
        ''')
        ability_reaction = Ability("test_ability", '''
            use_time = UseTime("reaction")
            reaction_trigger = "test_event"
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
        self.assertEqual(UseTime.Special.Bonus_Action.value, ability_bonus_action._use_time.minutes)

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

class TestAbilityIndexing(unittest.TestCase):
    INDEX = None
    EMPTY_INDEX = None
    STATBLOCK = None

    ABILITY = None
    ABILITY_TARGETED = None
    ABILITY_REACTION = None
    ABILITY_COMPOSITE = None
    ABILITY_MODIFIER = None
    ABILITY_MINUTE = None

    ABILITY_DICT = {}

    @patch('src.stats.statblock.Statblock')
    def setUp(self, statblock):
        self.EMPTY_INDEX = AbilityIndex()
        self.INDEX = AbilityIndex()
        self.STATBLOCK = statblock

        self.ABILITY = Ability("test_ability", '''
            use_time = UseTime("action", 1)
            
            function run()
                statblock.restore_hp(10)     
                return true, "Used test_ability."  
            end
        ''')
        self.ABILITY_TARGETED = Ability("test_ability_targeted", '''
            use_time = UseTime("bonus_action", 1)
            
            function run(target)
                target.restore_hp(10)
                return true, "Used test_ability_targeted."
            end
        ''')
        self.ABILITY_REACTION = Ability("test_ability_reaction", '''
            use_time = UseTime("reaction", 1)
            reaction_trigger = "test_event"
                                        
            function run()
                statblock.restore_hp(5)
                return true, "Used test_ability_reaction."
            end
        ''')
        self.ABILITY_COMPOSITE = CompositeAbility("test_composite_ability", "")
        sub_composite = Ability("sub_composite", '''
            use_time = UseTime("action", 1)
                                
            function run()
                statblock.restore_hp(15)
                return true, "Used sub_composite."
            end
        ''')
        sub_long_composite = Ability("sub_long_composite", '''
            use_time = UseTime("minute", 1)
                                     
            function run()
                statblock.restore_hp(25)
                return true, "Used sub_long_composite."
            end
        ''')
        self.ABILITY_COMPOSITE.add(sub_composite)
        self.ABILITY_COMPOSITE.add(sub_long_composite)
        self.ABILITY_MODIFIER = Ability("modifier", '''
            can_modify = {"test_ability", "test_ability_minute", "test_ability_composite"}
            
            function modify(amount)
                statblock.add_temp_hp(amount)
            end
        ''')
        self.ABILITY_MINUTE = Ability("test_ability_minute", '''
            use_time = UseTime("minute", 1)
            
            function run()
                statblock.restore_hp(40)
                return true, "Used test_ability_minute."
            end
        ''')

        self.INDEX.add(self.ABILITY)
        self.INDEX.add(self.ABILITY_TARGETED)
        self.INDEX.add(self.ABILITY_REACTION)
        self.INDEX.add(self.ABILITY_COMPOSITE)

        self.ABILITY_DICT = {
            "test_ability": self.ABILITY,
            "test_ability_targeted": self.ABILITY_TARGETED,
            "test_ability_reaction": self.ABILITY_REACTION,
            "test_composite_ability": self.ABILITY_COMPOSITE
        }

    def test_add_ability(self):
        new_ability = Ability("new_ability", "")
        
        self.assertDictEqual(self.ABILITY_DICT, self.INDEX._abilities)

        self.INDEX.add(new_ability)

        self.assertDictEqual({**self.ABILITY_DICT, "new_ability": new_ability}, self.INDEX._abilities)

        with self.assertRaises(ValueError):
            self.INDEX.add(new_ability)

    
    def test_remove_ability(self):
        self.assertDictEqual(self.ABILITY_DICT, self.INDEX._abilities)

        self.INDEX.remove("test_ability")

        self.assertDictEqual({
            "test_ability_targeted": self.ABILITY_TARGETED,
            "test_ability_reaction": self.ABILITY_REACTION,
            "test_composite_ability": self.ABILITY_COMPOSITE
        }, self.INDEX._abilities)

        with self.assertRaises(ValueError):
            self.INDEX.remove("test_ability")
    
    def test_get_ability_headers(self):
        expected = [
            ("test_ability", ()),
            ("test_ability_targeted", ("target",)),
            ("test_ability_reaction", ()),
            ("test_composite_ability.sub_composite", ()),
            ("test_composite_ability.sub_long_composite", ())
        ]
        self.assertEqual(expected, self.INDEX.get_headers())
    
    def test_get_action_headers(self):
        expected = [
            ("test_ability", ()),
            ("test_ability_targeted", ("target",)),
            ("test_composite_ability.sub_composite", ()),
            ("test_composite_ability.sub_long_composite", ())
        ]
        self.assertEqual(expected, self.INDEX.get_headers_turn_actions())
    
    def test_get_reaction_headers(self):
        expected = [
            ("test_ability_reaction", ())
        ]
        self.assertEqual(expected, self.INDEX.get_headers_reactions())
    
    def test_get_event_reaction_headers(self):
        reaction_ability = Ability("test_reaction_one", '''
            use_time = UseTime("reaction", 1)
            reaction_trigger = "other_event"
                                   
            function run()
                return true, "Used test_reaction_one."
            end
        ''')
        other_reaction_ability = Ability("test_reaction_two", '''
            use_time = UseTime("reaction", 1)
            reaction_trigger = "other_event"
                                   
            function run()
                return true, "Used test_reaction_two."
            end
        ''')
        self.INDEX.add(reaction_ability)
        self.INDEX.add(other_reaction_ability)

        expected = [
            ("test_ability_reaction", ())
        ]
        self.assertEqual(expected, self.INDEX.get_headers_reactions_to_event("test_event"))

        expected = [
            ("test_reaction_one", ()),
            ("test_reaction_two", ())
        ]
        self.assertEqual(expected, self.INDEX.get_headers_reactions_to_event("other_event"))

    def test_get_active_use_headers(self):
        timed_ability = Ability("timed_ability", '''
            use_time = UseTime("minute", 2)
                                
            function run(target)
                target.restore_hp(20)
                return true, "Used timed_ability."
            end
        ''')
        self.EMPTY_INDEX.add(timed_ability)
        self.EMPTY_INDEX.add(self.ABILITY)


        expected = [
            ("timed_ability", ("target",)),
            ("test_ability", ())
        ]
        self.assertEqual(expected, self.EMPTY_INDEX.get_headers())
        
        run_result = self.EMPTY_INDEX.run_ability("timed_ability", self.STATBLOCK)
        expected = ReturnStatus(False, "Preparing to use timed_ability, 19 turns remaining.")
        self.assertEqual(expected, run_result)

        expected = [
            ("^continue.timed_ability", ("target",)),
            ("^new_use.timed_ability", ("target",)),
            ("test_ability", ())
        ]
        self.assertEqual(expected, self.EMPTY_INDEX.get_headers())
    
    def test_get_active_use_headers_composite(self):
        self.EMPTY_INDEX.add(self.ABILITY)
        self.EMPTY_INDEX.add(self.ABILITY_COMPOSITE)

        expected = [
            ("test_ability", ()),
            ("test_composite_ability.sub_composite", ()),
            ("test_composite_ability.sub_long_composite", ())
        ]
        self.assertEqual(expected, self.EMPTY_INDEX.get_headers())

        run_result = self.EMPTY_INDEX.run_ability("test_composite_ability.sub_long_composite", self.STATBLOCK)
        expected = ReturnStatus(False, "Preparing to use test_composite_ability.sub_long_composite, 9 turns remaining.")
        self.assertEqual(expected, run_result)

        expected = [
            ("test_ability", ()),
            ("test_composite_ability.sub_composite", ()),
            ("^continue.test_composite_ability.sub_long_composite", ()),
            ("^new_use.test_composite_ability.sub_long_composite", ())
        ]
        self.assertEqual(expected, self.EMPTY_INDEX.get_headers())
    
    def test_get_active_use_headers_modifier(self):
        self.EMPTY_INDEX.add(self.ABILITY_MINUTE)
        self.EMPTY_INDEX.add(self.ABILITY_MODIFIER)

        expected = [
            ("test_ability_minute", ()),
            ("modifier", ("amount",))
        ]
        self.assertEqual(expected, self.EMPTY_INDEX.get_headers())

        run_result = self.EMPTY_INDEX.run_ability("test_ability_minute", self.STATBLOCK, modifier_abilities=[("modifier", 10)])
        expected = ReturnStatus(False, "Preparing to use test_ability_minute, 9 turns remaining.")
        self.assertEqual(expected, run_result)

        expected = [
            ("^continue.test_ability_minute", ()),
            ("^new_use.test_ability_minute", ()),
            ("modifier", ("amount",))
        ]
        self.assertEqual(expected, self.EMPTY_INDEX.get_headers())

class TestAbilityUse(unittest.TestCase):
    INDEX = None
    STATBLOCK = None
    RESTORE_HP = None

    ABILITY = None
    ABILITY_TARGETED = None
    ABILITY_REACTION = None
    ABILITY_COMPOSITE = None
    ABILITY_MODIFIER = None
    ABILITY_MINUTE = None

    ABILITY_DICT = {}

    @patch('src.stats.statblock.Statblock')
    def setUp(self, statblock):
        self.INDEX = AbilityIndex()
        self.STATBLOCK = statblock
        self.STATBLOCK._hit_points._max_hp = 100
        self.STATBLOCK._hit_points._hp = 50

        self.ABILITY = Ability("test_ability", '''
            use_time = UseTime("action", 1)
            
            function run()
                statblock.restore_hp(10)     
                return true, "Used test_ability."  
            end
        ''')
        self.ABILITY_TARGETED = Ability("test_ability_targeted", '''
            use_time = UseTime("bonus_action", 1)
            
            function run(target)
                target.restore_hp(10)
                return true, "Used test_ability_targeted."
            end
        ''')
        self.ABILITY_REACTION = Ability("test_ability_reaction", '''
            use_time = UseTime("reaction", 1)
            reaction_trigger = "test_event"
                                        
            function run()
                statblock.restore_hp(5)
                return true, "Used test_ability_reaction."
            end
        ''')
        self.ABILITY_COMPOSITE = CompositeAbility("test_composite_ability", "")
        sub_composite = Ability("sub_composite", '''
            use_time = UseTime("action", 1)
                                
            function run()
                statblock.restore_hp(15)
                return true, "Used sub_composite."
            end
        ''')
        sub_long_composite = Ability("sub_long_composite", '''
            use_time = UseTime("minute", 1)
                                     
            function run()
                statblock.restore_hp(25)
                return true, "Used sub_long_composite."
            end
        ''')
        self.ABILITY_COMPOSITE.add(sub_composite)
        self.ABILITY_COMPOSITE.add(sub_long_composite)
        self.ABILITY_MODIFIER = Ability("test_ability_modifier", '''
            can_modify = {"test_ability", "test_ability_minute", "test_ability_composite"}
            
            function modify(amount)
                statblock.add_temp_hp(amount)
                return true, "Added " .. amount .. " temp HP."
            end
        ''')
        self.ABILITY_MINUTE = Ability("test_ability_minute", '''
            use_time = UseTime("minute", 1)
            
            function run()
                statblock.restore_hp(40)
                return true, "Used test_ability_minute."
            end
        ''')

        self.INDEX.add(self.ABILITY)
        self.INDEX.add(self.ABILITY_TARGETED)
        self.INDEX.add(self.ABILITY_REACTION)
        self.INDEX.add(self.ABILITY_COMPOSITE)
        self.INDEX.add(self.ABILITY_MODIFIER)
        self.INDEX.add(self.ABILITY_MINUTE)

        self.ABILITY_DICT = {
            "test_ability": self.ABILITY,
            "test_ability_targeted": self.ABILITY_TARGETED,
            "test_ability_reaction": self.ABILITY_REACTION,
            "test_composite_ability": self.ABILITY_COMPOSITE,
            "test_ability_modifier": self.ABILITY_MODIFIER,
            "test_ability_minute": self.ABILITY_MINUTE
        }

    def test_run_ability(self):
        expected = ReturnStatus(True, "Used test_ability.")
        result = self.INDEX.run_ability("test_ability", self.STATBLOCK)
        self.assertEqual(expected, result)
        self.assertEqual(60, self.STATBLOCK._hit_points._hp)

    def test_run_modifier_ability(self):
        expected = ReturnStatus(True, "Added 7 temp HP. Used test_ability.")
        result = self.INDEX.run_ability("test_ability", self.STATBLOCK, modifier_abilities=[("test_ability_modifier", 7)])
        self.assertEqual(expected, result)

        self.STATBLOCK._hit_points.add_temp_hp.assert_called_once_with(7)
        self.assertEqual(60, self.STATBLOCK._hit_points._hp)
    
    def test_run_composite_ability(self):
        expected = ReturnStatus(True, "Used sub_composite.")
        result = self.INDEX.run_ability("test_composite_ability.sub_composite", self.STATBLOCK)
        self.assertEqual(expected, result)
        self.assertEqual(65, self.STATBLOCK._hit_points._hp)

        with self.assertRaises(ValueError):
            self.INDEX.run_ability("test_composite_ability", self.STATBLOCK)
    
    def test_run_composite_modifier_ability(self):
        composite_modifier = Ability("composite_modifier", '''
            can_modify = {"test_composite_ability.sub_composite"}
            
            function modify(amount)
                statblock.add_temp_hp(amount)
                return true, "Added " .. amount .. " temp HP."
            end
        ''')
        new_composite = CompositeAbility("powers", "")
        new_composite.add(composite_modifier)
        self.INDEX.add(new_composite)

        expected = ReturnStatus(True, "Added 7 temp HP. Used sub_composite.")
        result = self.INDEX.run_ability("test_composite_ability.sub_composite", self.STATBLOCK, modifier_abilities=[("powers.composite_modifier", 7)])
        self.assertEqual(expected, result)
        self.assertEqual(65, self.STATBLOCK._hit_points._hp)
        self.STATBLOCK._hit_points.add_temp_hp.assert_called_once_with(7)

    def test_run_modify_composite_outer(self):
        modifier = Ability("modify", '''
            can_modify = {"test_composite_ability"}
                           
            function modify(amount)
                statblock.add_temp_hp(amount)
                return true, "Added " .. amount .. " temp HP."
            end
        ''')
        self.INDEX.add(modifier)

        expected = ReturnStatus(True, "Added 7 temp HP. Used sub_composite.")
        result = self.INDEX.run_ability("test_composite_ability.sub_composite", self.STATBLOCK, modifier_abilities=[("modify", 7)])
        self.assertEqual(expected, result)
        self.STATBLOCK._hit_points.add_temp_hp.assert_called_once_with(7)

        self.STATBLOCK.reset_mock()
        expected = ReturnStatus(False, "Preparing to use test_composite_ability.sub_long_composite, 9 turns remaining.")
        result = self.INDEX.run_ability("test_composite_ability.sub_long_composite", self.STATBLOCK, modifier_abilities=[("modify", 7)])
        self.assertEqual(expected, result)

        for i in range(0, 7):
            self.INDEX.run_ability("^continue.test_composite_ability.sub_long_composite", self.STATBLOCK)

        with self.assertRaises(ValueError):
            self.INDEX.run_ability("^continue.test_composite_ability.sub_long_composite", self.STATBLOCK, modifier_abilities=[("modify", 7)])
        self.INDEX.run_ability("test_composite_ability.sub_long_composite", self.STATBLOCK)
        
        expected = ReturnStatus(True, "Added 7 temp HP. Used sub_long_composite.")
        result = self.INDEX.run_ability("^continue.test_composite_ability.sub_long_composite", self.STATBLOCK)
        self.assertEqual(expected, result)

    def test_run_nested_composite_ability(self):
        nested_composite = CompositeAbility("nested_composite", "")
        nested_ability = Ability("nested_ability", '''
            use_time = UseTime("action", 1)

            function run()
                statblock.restore_hp(33)
                return true, "Used nested_composite."
            end
        ''')
        nested_composite.add(nested_ability)
        self.INDEX._abilities["test_composite_ability"].add(nested_composite)

        expected = ReturnStatus(True, "Used nested_composite.")
        result = self.INDEX.run_ability("test_composite_ability.nested_composite.nested_ability", self.STATBLOCK)
        self.assertEqual(expected, result)
        self.assertEqual(83, self.STATBLOCK._hit_points._hp)
    
    def test_run_ability_delayed_use(self):
        expected = ReturnStatus(False, "Preparing to use test_ability_minute, 9 turns remaining.")
        result = self.INDEX.run_ability("test_ability_minute", self.STATBLOCK)
        self.assertEqual(expected, result)
        self.assertEqual(50, self.STATBLOCK._hit_points._hp)

        for i in range(8, 0, -1):
            expected = ReturnStatus(False, f"Preparing to use test_ability_minute, {i} turns remaining.")
            result = self.INDEX.run_ability("^continue.test_ability_minute", self.STATBLOCK)
            self.assertEqual(expected, result)
            self.STATBLOCK.restore_hp.assert_not_called()

        expected = ReturnStatus(True, "Used test_ability_minute.")
        result = self.INDEX.run_ability("^continue.test_ability_minute", self.STATBLOCK)
        self.assertEqual(expected, result)
        self.assertEqual(90, self.STATBLOCK._hit_points._hp)
    
    def test_run_ability_interrupt_delayed_use(self):
        expected = ReturnStatus(False, "Preparing to use test_ability_minute, 9 turns remaining.")
        result = self.INDEX.run_ability("test_ability_minute", self.STATBLOCK)
        self.assertEqual(expected, result)
        self.assertEqual(50, self.STATBLOCK._hit_points._hp)

        for i in range(8, 5, -1):
            expected = ReturnStatus(False, f"Preparing to use test_ability_minute, {i} turns remaining.")
            result = self.INDEX.run_ability("^continue.test_ability_minute", self.STATBLOCK)
            self.assertEqual(expected, result)
            self.assertEqual(50, self.STATBLOCK._hit_points._hp)
        
        expected = ReturnStatus(True, "Used test_ability.")
        result = self.INDEX.run_ability("test_ability", self.STATBLOCK)
        self.assertEqual(expected, result)
        self.assertEqual(60, self.STATBLOCK._hit_points._hp)

        with self.assertRaises(ValueError): 
            self.INDEX.run_ability("^continue.test_ability_minute", self.STATBLOCK)
        
        expected = ReturnStatus(False, "Preparing to use test_ability_minute, 9 turns remaining.")
        result = self.INDEX.run_ability("test_ability_minute", self.STATBLOCK)
        self.assertEqual(expected, result)
    
    def test_run_ability_delayed_new_use(self):
        expected = ReturnStatus(False, "Preparing to use test_ability_minute, 9 turns remaining.")
        result = self.INDEX.run_ability("test_ability_minute", self.STATBLOCK)
        self.assertEqual(expected, result)
        self.assertEqual(50, self.STATBLOCK._hit_points._hp)

        for i in range(8, 5, -1):
            expected = ReturnStatus(False, f"Preparing to use test_ability_minute, {i} turns remaining.")
            result = self.INDEX.run_ability("^continue.test_ability_minute", self.STATBLOCK)
            self.assertEqual(expected, result)
            self.assertEqual(50, self.STATBLOCK._hit_points._hp)
        
        expected = ReturnStatus(False, "Preparing to use test_ability_minute, 9 turns remaining.")
        result = self.INDEX.run_ability("^new_use.test_ability_minute", self.STATBLOCK)
        self.assertEqual(expected, result)
        self.assertEqual(50, self.STATBLOCK._hit_points._hp)

        for i in range(8, 0, -1):
            expected = ReturnStatus(False, f"Preparing to use test_ability_minute, {i} turns remaining.")
            result = self.INDEX.run_ability("^continue.test_ability_minute", self.STATBLOCK)
            self.assertEqual(expected, result)
            self.assertEqual(50, self.STATBLOCK._hit_points._hp)

        expected = ReturnStatus(True, "Used test_ability_minute.")
        result = self.INDEX.run_ability("^continue.test_ability_minute", self.STATBLOCK)
        self.assertEqual(expected, result)
        self.assertEqual(90, self.STATBLOCK._hit_points._hp)

class TestAbilityValidation(unittest.TestCase):
    INDEX = None
    STATBLOCK = None

    ABILITY = None
    ABILITY_COMPOSITE = None
    ABILITY_MODIFIER = None

    @patch('src.stats.statblock.Statblock')
    @patch('src.stats.statblock.Statblock')
    def setUp(self, statblock, target):
        self.INDEX = AbilityIndex()
        self.STATBLOCK = statblock
        self.STATBLOCK._hit_points._max_hp = 100
        self.STATBLOCK._hit_points._hp = 50

        self.ABILITY = Ability("test_ability", '''
            use_time = UseTime("action", 1)
            
            function validate(target)
                if target <= 0 then
                    return false, "Failed validation."
                end
                return true, nil
            end

            function run(target)
                statblock.restore_hp(30)     
                return true, "Used test_ability."  
            end
        ''')
        self.ABILITY_COMPOSITE = CompositeAbility("test_composite_ability", "")
        sub_composite = Ability("test_subcomposite", '''
            use_time = UseTime("action", 1)
                                
            function validate(target)
                if target <= 0 then
                    return false, "Failed validation."
                end
                return true, nil
            end
                                
            function run(target)
                statblock.restore_hp(15)
                return true, "Used test_subcomposite."
            end
        ''')
        self.ABILITY_COMPOSITE.add(sub_composite)
        self.ABILITY_MODIFIER = Ability("test_modifier", '''
            can_modify = {"test_ability", "test_composite_ability"}
            
            function validate(target)
                if target <= 5 then
                    return false, "Failed validation."
                end
                return true, nil
            end
                                        
            function modify(target)
                statblock.add_temp_hp(10)
                return true, "Added 10 temp HP."
            end
        ''')
        self.SUBABILITY = SubAbility("test_subability", '''
            test_subability = {
                use_time = UseTime("bonus_action", 1),
                validate = function(target)
                    if target <= 0 then
                        return false, "Failed validation."
                    end
                    return true, nil
                end,
                run = function(target)
                    statblock.restore_hp(5)
                    return true, "Used test_subability."
                end
            }
                                     
            function validate(target)
                return true, nil
            end
        ''')
        self.INDEX.add(self.ABILITY)
        self.INDEX.add(self.ABILITY_COMPOSITE)
        self.INDEX.add(self.ABILITY_MODIFIER)
        self.INDEX.add(self.SUBABILITY)
    
    def test_validate_ability(self):
        expected = ReturnStatus(False, "Invalid test_ability use. Failed validation.")
        result = self.INDEX.run_ability("test_ability", self.STATBLOCK, 0)
        self.assertEqual(expected, result)
        self.assertEqual(50, self.STATBLOCK._hit_points._hp)

        expected = ReturnStatus(True, "Used test_ability.")
        result = self.INDEX.run_ability("test_ability", self.STATBLOCK, 1)
        self.assertEqual(expected, result)
        self.assertEqual(80, self.STATBLOCK._hit_points._hp)

    def test_validate_composite_ability(self):
        expected = ReturnStatus(False, "Invalid test_composite_ability.test_subcomposite use. Failed validation.")
        result = self.INDEX.run_ability("test_composite_ability.test_subcomposite", self.STATBLOCK, 0)
        self.assertEqual(expected, result)
        self.assertEqual(50, self.STATBLOCK._hit_points._hp)

        expected = ReturnStatus(True, "Used test_subcomposite.")
        result = self.INDEX.run_ability("test_composite_ability.test_subcomposite", self.STATBLOCK, 1)
        self.assertEqual(expected, result)
        self.assertEqual(65, self.STATBLOCK._hit_points._hp)
    
    def test_modifier_validation(self):
        # Validation error message prioritizes main ability.
        expected = ReturnStatus(False, "Invalid test_ability use. Failed validation.")
        result = self.INDEX.run_ability("test_ability", self.STATBLOCK, 0, modifier_abilities=[("test_modifier", 2)])
        self.assertEqual(expected, result)
        self.STATBLOCK._hit_points.add_temp_hp.assert_not_called()
        self.assertEqual(50, self.STATBLOCK._hit_points._hp)

        # Modifier validation only validates based off of it's own arguments.
        expected = ReturnStatus(False, "Invalid test_modifier use. Failed validation.")
        result = self.INDEX.run_ability("test_ability", self.STATBLOCK, 15, modifier_abilities=[("test_modifier", 2)])
        self.assertEqual(expected, result)
        self.STATBLOCK._hit_points.add_temp_hp.assert_not_called()
        self.assertEqual(50, self.STATBLOCK._hit_points._hp)

        expected = ReturnStatus(True, "Added 10 temp HP. Used test_ability.")
        result = self.INDEX.run_ability("test_ability", self.STATBLOCK, 5, modifier_abilities=[("test_modifier", 15)])
        self.assertEqual(expected, result)
        self.STATBLOCK._hit_points.add_temp_hp.assert_called_once_with(10)
        self.assertEqual(80, self.STATBLOCK._hit_points._hp)
    
    def test_subability_validation(self):
        expected = ReturnStatus(False, "Invalid test_subability use. Failed validation.")
        result = self.INDEX.run_ability("test_subability", self.STATBLOCK, 0)
        self.assertEqual(expected, result)

        expected = ReturnStatus(True, "Used test_subability.")
        result = self.INDEX.run_ability("test_subability", self.STATBLOCK, 1)
        self.assertEqual(expected, result)


class TestAbilityModifiers(unittest.TestCase):
    INDEX = None
    STATBLOCK = None

    ABLITY_1 = None
    ABLITY_2 = None
    ABLITY_3 = None
    ABLITY_4 = None
    ABLITY_5 = None

    LAYER_1 = None
    LAYER_2 = None

    @patch('src.stats.statblock.Statblock')
    def setUp(self, statblock):
        self.STATBLOCK = statblock
        self.INDEX = AbilityIndex()

        self.ABLITY_1 = Ability("ability_1", '''
            use_time = UseTime("action", 1)
                          
            function run()
                statblock.restore_hp(10)
                return true, "Used ability_1."
            end
        ''')
        self.ABLITY_2 = Ability("ability_2", '''
            use_time = UseTime("action", 1)
                          
            function run()
                statblock.restore_hp(20)
                return true, "Used ability_2."
            end
        ''')
        self.ABLITY_3 = Ability("ability_3", '''
            use_time = UseTime("action", 1)
                                 
            function run()
                statblock.restore_hp(30)
                return true, "Used ability_3."
            end
        ''')
        self.ABLITY_4 = Ability("ability_4", '''
            use_time = UseTime("action", 1)
                                 
            function run()
                statblock.restore_hp(40)
                return true, "Used ability_4."
            end
        ''')
        self.ABLITY_5 = Ability("ability_5", '''
            use_time = UseTime("action", 1)
                                 
            function run()
                statblock.restore_hp(50)
                return true, "Used ability_5."
            end
        ''')

        self.LAYER_1 = CompositeAbility("layer_1", "")
        self.LAYER_2 = CompositeAbility("layer_2", "")
    
    def ModifierConstructor(self, name, can_modify):
        return Ability(name, f'''
            can_modify = {{"{can_modify}"}}

            function modify(amount)
                statblock.add_temp_hp(amount)
                return true, "Added " .. amount .. " temp HP."
            end
        ''')
    
    def test_modifiers_on_all_subcomposites(self):
        modifier = self.ModifierConstructor("modifier", "layer_1")
        
        self.assertTrue(modifier.can_modify("layer_1"))
        self.assertTrue(modifier.can_modify("layer_1.ability"))
        self.assertTrue(modifier.can_modify("layer_1.sub_layer.ability"))
        self.assertTrue(modifier.can_modify("overlayer.layer_1.ability"))
    
    def test_modifiers_on_composite_combos(self):
        modifier = self.ModifierConstructor("modifier", "layer_1.sub_layer")

        self.assertTrue(modifier.can_modify("layer_1.sub_layer.ability"))
        self.assertFalse(modifier.can_modify("layer_1.ability"))
        self.assertTrue(modifier.can_modify("overlayer.layer_1.sub_layer.ability"))
        self.assertFalse(modifier.can_modify("overlayer.layer_1.ability.sub_layer"))

class TestAbilitySignals(unittest.TestCase):
    INDEX = None
    STATBLOCK = None

    EFFECT_SCRIPT = ""
    ALT_EFFECT_SCRIPT = ""

    @patch('src.stats.statblock.Statblock')
    def setUp(self, statblock):
        self.INDEX = AbilityIndex()
        self.STATBLOCK = statblock

        self.EFFECT_SCRIPT = '''
            effect_ability = {
                use_time = UseTime("action", 1),
                run = function(target)
                    return true, "Used effect_ability."
                end
            }
        '''
        self.ALT_EFFECT_SCRIPT = '''
            alt_effect_ability = {
                use_time = UseTime("action", 1),
                run = function(target)
                    return true, "Used alt_effect_ability."
                end
            }
        '''

    def test_effect_grants_subability(self):
        self.assertNotIn("effect_ability", self.INDEX._abilities.keys())

        self.INDEX.signal(EventType.EFFECT_GRANTED_ABILITY, "effect_ability", self.EFFECT_SCRIPT)

        self.assertIn("effect_ability", self.INDEX._abilities.keys())

        expected = ReturnStatus(True, "Used effect_ability.")
        result = self.INDEX.run_ability("effect_ability", self.STATBLOCK)
        self.assertEqual(expected, result)
    
    def test_effect_grants_multiple_subability(self):
        self.assertNotIn("effect_ability", self.INDEX._abilities.keys())
        self.assertNotIn("alt_effect_ability", self.INDEX._abilities.keys())

        self.INDEX.signal(EventType.EFFECT_GRANTED_ABILITY, "effect_ability", self.EFFECT_SCRIPT)
        self.INDEX.signal(EventType.EFFECT_GRANTED_ABILITY, "alt_effect_ability", self.ALT_EFFECT_SCRIPT)

        self.assertIn("effect_ability", self.INDEX._abilities.keys())
        self.assertIn("alt_effect_ability", self.INDEX._abilities.keys())

        expected = ReturnStatus(True, "Used effect_ability.")
        result = self.INDEX.run_ability("effect_ability", self.STATBLOCK)
        self.assertEqual(expected, result)

        expected = ReturnStatus(True, "Used alt_effect_ability.")
        result = self.INDEX.run_ability("alt_effect_ability", self.STATBLOCK)
        self.assertEqual(expected, result)

    def test_effect_removes_subability(self):
        self.INDEX.signal(EventType.EFFECT_GRANTED_ABILITY, "effect_ability", self.EFFECT_SCRIPT)

        self.assertIn("effect_ability", self.INDEX._abilities.keys())

        self.INDEX.signal(EventType.EFFECT_REMOVED_ABILITY, "effect_ability")

        self.assertNotIn("effect_ability", self.INDEX._abilities.keys())

class TestAbilityConcentration(unittest.TestCase):
    INDEX = None
    STATBLOCK = None

    ABILITY = None
    OTHER_ABILITY = None
    SMALL_ABILITY = None

    @patch('src.stats.statblock.Statblock')
    def setUp(self, statblock):
        self.INDEX = AbilityIndex()
        self.STATBLOCK = statblock
        self.STATBLOCK._hit_points._max_hp = 100
        self.STATBLOCK._hit_points._hp = 50

        self.ABILITY = Ability("test_ability", '''
            use_time = UseTime("action", 1)
            spell_duration = Duration("minute", 1)
            spell_concentration = true
                          
            function run()
                statblock.restore_hp(10)
                return true, "Used test_ability."
            end
        ''')
        self.OTHER_ABILITY = Ability("other_ability", '''
            use_time = UseTime("action", 1)
            spell_duration = Duration("minute", 1)
            spell_concentration = true
                                     
            function run()
                statblock.restore_hp(20)
                return true, "Used other_ability."
            end
        ''')
        self.SMALL_ABILITY = Ability("small_ability", '''
            use_time = UseTime("action", 1)
                                     
            function run()
                statblock.restore_hp(5)
                return true, "Used small_ability."
            end
        ''')
        self.INDEX.add(self.ABILITY)
        self.INDEX.add(self.OTHER_ABILITY)
        self.INDEX.add(self.SMALL_ABILITY)

    def test_concentration(self):
        self.assertFalse(self.INDEX._concentration_tracker.concentrating)
        self.assertIsNone(self.INDEX._concentration_tracker._ability)
        
        expected = ReturnStatus(True, "Used test_ability.")
        result = self.INDEX.run_ability("test_ability", self.STATBLOCK)
        self.assertEqual(expected, result)

        self.assertTrue(self.INDEX._concentration_tracker.concentrating)
        self.assertEqual(self.INDEX._concentration_tracker._ability, self.ABILITY)
        self.assertEqual(self.INDEX._concentration_tracker._remaining_ticks, 10)

        for i in range(9, 0, -1):
            self.INDEX.tick_timers()
            self.assertTrue(self.INDEX._concentration_tracker.concentrating)
            self.assertEqual(self.INDEX._concentration_tracker._remaining_ticks, i)
        
        self.INDEX.tick_timers()
        self.assertFalse(self.INDEX._concentration_tracker.concentrating)
        self.assertIsNone(self.INDEX._concentration_tracker._ability)
    
    def test_concentration_interrupt(self):
        expected = ReturnStatus(True, "Used test_ability.")
        result = self.INDEX.run_ability("test_ability", self.STATBLOCK)
        self.assertEqual(expected, result)

        self.assertTrue(self.INDEX._concentration_tracker.concentrating)
        self.assertEqual(self.INDEX._concentration_tracker._ability, self.ABILITY)
        self.assertEqual(self.INDEX._concentration_tracker._remaining_ticks, 10)

        for i in range(9, 5, -1):
            self.INDEX.tick_timers()
            self.assertTrue(self.INDEX._concentration_tracker.concentrating)
            self.assertEqual(self.INDEX._concentration_tracker._remaining_ticks, i)

        expected = ReturnStatus(True, "Used other_ability.")
        result = self.INDEX.run_ability("other_ability", self.STATBLOCK)
        self.assertEqual(expected, result)

        self.assertTrue(self.INDEX._concentration_tracker.concentrating)
        self.assertEqual(self.INDEX._concentration_tracker._ability, self.OTHER_ABILITY)

        self.INDEX.tick_timers()
        self.assertEqual(self.INDEX._concentration_tracker._remaining_ticks, 9)

        expected = ReturnStatus(True, "Used small_ability.")
        result = self.INDEX.run_ability("small_ability", self.STATBLOCK)
        self.assertEqual(expected, result)

        self.assertTrue(self.INDEX._concentration_tracker.concentrating)
        self.assertEqual(self.INDEX._concentration_tracker._ability, self.OTHER_ABILITY)
        self.assertEqual(self.INDEX._concentration_tracker._remaining_ticks, 9)
    
    def test_breaking_concentration(self):
        self.INDEX.run_ability("test_ability", self.STATBLOCK)

        self.assertTrue(self.INDEX._concentration_tracker.concentrating)
        self.assertEqual(self.INDEX._concentration_tracker._ability, self.ABILITY)
        self.assertEqual(self.INDEX._concentration_tracker._remaining_ticks, 10)

        self.INDEX.tick_timers()
        self.INDEX.tick_timers()
        self.INDEX.tick_timers()
        self.assertEqual(self.INDEX._concentration_tracker._remaining_ticks, 7)

        self.INDEX.break_concentration()

        self.assertFalse(self.INDEX._concentration_tracker.concentrating)
        self.assertIsNone(self.INDEX._concentration_tracker._ability)

class TestAbilityStatblockWrapper(unittest.TestCase):
    STATBLOCK = None
    ABILITY = None
    WRAPPER = None

    @patch('src.stats.statblock.Statblock')
    def setUp(self, statblock):
        self.STATBLOCK = statblock
        self.ABILITY = Ability("test_ability", '''
            use_time = UseTime("action", 1)
            random_global = 10
            spellcasting_ability = "int"
                               
            sub_ability = {
                use_time = UseTime("bonus_action", 1),
                random_global = 40,
                run = function()
                    statblock.restore_hp(5)
                    return true, "Used sub_ability."
                end
            }

            function run()
                statblock.restore_hp(10)
                return true, "Used test_ability."
            end
        ''')
        self.WRAPPER = StatblockAbilityWrapper(self.STATBLOCK, self.ABILITY)
    
    def test_add_ability(self):
        self.WRAPPER.add_ability("sub_ability")
        self.STATBLOCK._abilities.add.assert_called_once()

        added_ability = self.STATBLOCK._abilities.add.call_args[0][0]
        self.assertEqual(added_ability._name, "sub_ability")
        self.assertEqual(added_ability._globals["random_global"], 40)
        self.assertIsInstance(added_ability, SubAbility)
    
    def test_remove_ability(self):
        self.WRAPPER.remove_ability()
        self.STATBLOCK._abilities.remove.assert_called_once_with("test_ability")

        self.STATBLOCK._abilities.remove.reset_mock()
        self.WRAPPER.remove_ability("sub_ability")
        self.STATBLOCK._abilities.remove.assert_called_once_with("sub_ability")
    
    def test_add_effect(self):
        self.WRAPPER.add_effect("test_effect", 5)
        self.STATBLOCK._abilities.emit.assert_called_once_with(EventType.ABILITY_APPLIED_EFFECT, "test_effect", self.ABILITY._script, 5, self.ABILITY._uuid)
    
    def test_remove_effect(self):
        self.WRAPPER.remove_effect("test_effect")
        self.STATBLOCK._abilities.emit.assert_called_once_with(EventType.ABILITY_REMOVED_EFFECT, "test_effect")
    
    @patch('src.stats.handlers.attack_roll_handler.AttackRollHandler.ability_attack_roll')
    def test_spell_attack_roll(self, ability_attack_roll):
        target = MagicMock()
        self.WRAPPER.spell_attack_roll(target, "2d6+4 fire")
        ability_attack_roll.assert_called_once_with(target, "int", "2d6+4 fire")
    
    @patch('src.stats.statblock.Statblock')
    @patch('src.stats.statblock.Statblock')
    def test_statblock_reference(self, target_A, target_B):
        reference_ability = Ability("reference", '''
            use_time = UseTime("action", 1)
            reference = nil
            
            function run(target)
                if reference ~= nil then
                    reference.get_hp()
                end
                reference = target
                return true, "Used reference."
            end
        ''')
        index = AbilityIndex()
        index.add(reference_ability)

        def reset_mocks():
            target_A.reset_mock()
            target_B.reset_mock()

        target_A.wrap.side_effect = lambda w: StatblockAbilityWrapper(target_A, reference_ability)
        target_B.wrap.side_effect = lambda w: StatblockAbilityWrapper(target_B, reference_ability)

        reset_mocks()
        index.run_ability("reference", self.STATBLOCK, target_A)
        self.assertEqual(reference_ability._globals["reference"]._statblock, target_A)
        target_A._hit_points.get_hp.assert_not_called()
        target_B._hit_points.get_hp.assert_not_called()

        reset_mocks()
        index.run_ability("reference", self.STATBLOCK, target_B)
        self.assertEqual(reference_ability._globals["reference"]._statblock, target_B)
        target_A._hit_points.get_hp.assert_called_once()
        target_B._hit_points.get_hp.assert_not_called()

        reset_mocks()
        index.run_ability("reference", self.STATBLOCK, None)
        self.assertIsNone(reference_ability._globals["reference"])
        target_A._hit_points.get_hp.assert_not_called()
        target_B._hit_points.get_hp.assert_called_once()

        reset_mocks()
        index.run_ability("reference", self.STATBLOCK, target_A)
        self.assertEqual(reference_ability._globals["reference"]._statblock, target_A)
        target_A._hit_points.get_hp.assert_not_called()
        target_B._hit_points.get_hp.assert_not_called()