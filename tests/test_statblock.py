import unittest
from unittest.mock import patch, MagicMock
from src.stats.effects import Effect
from src.stats.statblock import Statblock

class TestStatblock(unittest.TestCase):

    # Base Statistics
    def test_get_name(self):
        statblock = Statblock("Tester")

        self.assertEqual("Tester", statblock.get_name())
    
    def test_get_size(self):
        statblock = Statblock("Tester", size = 5)

        self.assertEqual(5, statblock._size)

    def test_leveling(self):
        statblock = Statblock("Tester")

        self.assertEqual(0, statblock.get_level())

        statblock.add_level("fighter")

        self.assertEqual(1, statblock.get_level())

        statblock.add_level("fighter", 2)

        self.assertEqual(3, statblock.get_level())

        statblock.add_level("wizard")

        self.assertEqual(4, statblock.get_level())
        self.assertEqual(3, statblock.get_level("fighter"))
        self.assertEqual(1, statblock.get_level("wizard"))

    def test_ability_scores(self):
        statblock = Statblock("Tester")

        self.assertEqual(10, statblock.get_ability_score("str"))
        self.assertEqual(0, statblock.get_ability_modifier("str"))

        self.assertEqual(10, statblock.get_ability_score("dex"))
        self.assertEqual(0, statblock.get_ability_modifier("dex"))

        self.assertEqual(10, statblock.get_ability_score("con"))
        self.assertEqual(0, statblock.get_ability_modifier("con"))

        self.assertEqual(10, statblock.get_ability_score("int"))
        self.assertEqual(0, statblock.get_ability_modifier("int"))

        self.assertEqual(10, statblock.get_ability_score("wis"))
        self.assertEqual(0, statblock.get_ability_modifier("wis"))

        self.assertEqual(10, statblock.get_ability_score("cha"))
        self.assertEqual(0, statblock.get_ability_modifier("cha"))

        statblock._ability_scores["cha"].value = 16

        self.assertEqual(16, statblock.get_ability_score("cha"))
        self.assertEqual(3, statblock.get_ability_modifier("cha"))

    def test_proficiency_bonus(self):
        statblock = Statblock("Tester")

        statblock.add_level("fighter")

        self.assertEqual(2, statblock.get_proficiency_bonus())

        statblock.add_level("fighter", 3)
        self.assertEqual(2, statblock.get_proficiency_bonus())

        statblock.add_level("fighter", 1)
        self.assertEqual(3, statblock.get_proficiency_bonus())

        statblock.add_level("fighter", 3)
        self.assertEqual(3, statblock.get_proficiency_bonus())

        statblock.add_level("fighter", 1)
        self.assertEqual(4, statblock.get_proficiency_bonus())

        statblock.add_level("fighter", 3)
        self.assertEqual(4, statblock.get_proficiency_bonus())

        statblock.add_level("fighter", 1)
        self.assertEqual(5, statblock.get_proficiency_bonus())

        statblock.add_level("fighter", 3)
        self.assertEqual(5, statblock.get_proficiency_bonus())

        statblock.add_level("fighter", 1)
        self.assertEqual(6, statblock.get_proficiency_bonus())

        statblock.add_level("fighter", 3)
        self.assertEqual(6, statblock.get_proficiency_bonus())
        self.assertEqual(20, statblock.get_level())

    # Abilities
    @patch('src.stats.abilities.Ability')
    def test_add_ability(self, AbilityMock):
        statblock = Statblock("Tester")
        ability = AbilityMock.return_value

        self.assertEqual(0, len(statblock._abilities._abilities))

        statblock.add_ability(ability)

        self.assertEqual(1, len(statblock._abilities._abilities))

    @patch('src.stats.abilities.Ability')
    def test_remove_ability(self, AbilityMock):
        statblock = Statblock("Tester")
        ability = AbilityMock.return_value
        ability._name = "test_ability"
        statblock.add_ability(ability)

        self.assertEqual(1, len(statblock._abilities._abilities))

        statblock.remove_ability("test_ability")

        self.assertEqual(0, len(statblock._abilities._abilities))

    @patch('src.stats.abilities.Ability')
    def test_run_ability(self, AbilityMock):
        # Create statblock and ability
        statblock = Statblock("Tester")
        ability = AbilityMock.return_value
        ability._name = "test_ability"
        ability.is_modifier = False
        ability.run.return_value = (True, "Ran test")

        # Add ability and verify running returns correct values
        statblock.add_ability(ability)
        self.assertEqual((True, "Ran test"), statblock.use_ability("test_ability"))

        # Verify running with parameters returns correct values and passes parameters
        self.assertEqual((True, "Ran test"), statblock.use_ability("test_ability", 1, 2))
        self.assertEqual((1, 2), ability.run.call_args[0])
    
    @patch('src.stats.abilities.Ability')
    def test_run_ability_chain(self, AbilityMock):
        # Create statblock and abilities
        statblock = Statblock("Tester")
        ability_main = MagicMock()
        ability_main._name = "test_ability_main"
        ability_main.is_modifier = False
        ability_main.initialize.return_value.run.return_value = (True, "Ran test main.")

        ability_sub = MagicMock()
        ability_sub._name = "test_ability_sub"
        ability_sub.is_modifier = True
        ability_sub.can_modify.return_value = True
        ability_sub.run.return_value = (True, "Ran test sub.")

        # Add abilities
        statblock.add_ability(ability_main)
        statblock.add_ability(ability_sub)

        # Verify running chain returns correct values
        self.assertEqual((True, "Ran test sub. Ran test main."), statblock.use_ability_chain(("test_ability_main",), ("test_ability_sub",)))

        # Verify running chain with parameters returns correct values and passes parameters
        self.assertEqual((True, "Ran test sub. Ran test main."), statblock.use_ability_chain(("test_ability_main", 1, 2), ("test_ability_sub", 3, 4)))
        self.assertEqual((1, 2), ability_main.initialize.return_value.run.call_args[0][1:])
        self.assertEqual((3, 4), ability_sub.run.call_args[0])

    # Health
    def test_get_hit_points(self):
        statblock = Statblock("Tester")
        statblock._hp._initial = 15
        statblock._hp.value = 15

        self.assertEqual(15, statblock.get_hit_points())
        self.assertEqual(15, statblock.get_max_hit_points())

        statblock._hp.value = 10

        self.assertEqual(10, statblock.get_hit_points())
        self.assertEqual(15, statblock.get_max_hit_points())

    def test_restore_hit_points(self):
        statblock = Statblock("Tester")
        statblock._hp._initial = 15
        statblock._hp.value = 10

        self.assertEqual(10, statblock.get_hit_points())

        statblock.restore_hp(2)

        self.assertEqual(12, statblock.get_hit_points())

        statblock.restore_hp(10)

        self.assertEqual(15, statblock.get_hit_points())
    
    def test_add_temporary_hit_points(self):
        statblock = Statblock("Tester")
        statblock._hp._initial = 15
        statblock._hp.value = 10

        self.assertEqual(10, statblock.get_hit_points())
        self.assertEqual(0, statblock._temp_hp)

        statblock.add_temporary_hp(5)

        self.assertEqual(10, statblock.get_hit_points())
        self.assertEqual(5, statblock._temp_hp)

        statblock.add_temporary_hp(10)

        self.assertEqual(10, statblock.get_hit_points())
        self.assertEqual(10, statblock._temp_hp)

        statblock.add_temporary_hp(8)

        self.assertEqual(10, statblock.get_hit_points())
        self.assertEqual(10, statblock._temp_hp)
    
    def test_take_damage(self):
        statblock = Statblock("Tester")
        statblock._hp._initial = 15
        statblock._hp.value = 10

        self.assertEqual(10, statblock.get_hit_points())

        statblock.take_damage(5, "piercing")

        self.assertEqual(5, statblock.get_hit_points())

        statblock.take_damage(10, "slashing")

        self.assertEqual(0, statblock.get_hit_points())
    
    def test_take_damage_temporary_hp(self):
        statblock = Statblock("Tester")
        statblock._hp._initial = 15
        statblock._hp.value = 10
        statblock._temp_hp = 5

        self.assertEqual(10, statblock.get_hit_points())
        self.assertEqual(5, statblock._temp_hp)

        statblock.take_damage(2, "piercing")

        self.assertEqual(10, statblock.get_hit_points())
        self.assertEqual(3, statblock._temp_hp)

        statblock.take_damage(10, "slashing")

        self.assertEqual(3, statblock.get_hit_points())
        self.assertEqual(0, statblock._temp_hp)

    # Combat Statistics

    def test_get_armor_class(self):
        statblock = Statblock("Tester")
        statblock._armor_class = 15

        self.assertEqual(15, statblock.get_armor_class())

    @patch('src.util.dice.DiceRoller.roll_d20', return_value = 15)
    def test_melee_attack_roll(self, roll_d20):
        # Create statblocks
        statblock = Statblock("Tester")
        target = Statblock("Target")
        
        # Verify attack roll succeeds with no bonuses
        target._armor_class = 10
        self.assertTrue(statblock.melee_attack_roll(target, "1d4 slashing"))

        # Verify attack roll fails with armor class higher than roll result
        target._armor_class = 16
        self.assertFalse(statblock.melee_attack_roll(target, "1d4 slashing"))

        # Verify strength modifier is added to attack roll
        statblock._ability_scores["str"].value = 16 #(+3 to STR)
        self.assertTrue(statblock.melee_attack_roll(target, "1d4 slashing"))

        # Verify ranged attack roll still fails
        self.assertFalse(statblock.ranged_attack_roll(target, "1d4 slashing"))

    @patch('src.util.dice.DiceRoller.roll_d20', return_value = 15)
    def test_ranged_attack_roll(self, roll_d20):
        # Create statblocks
        statblock = Statblock("Tester")
        target = Statblock("Target")
        
        # Verify attack roll succeeds with no bonuses
        target._armor_class = 10
        self.assertTrue(statblock.ranged_attack_roll(target, "1d4 slashing"))

        # Verify attack roll fails with armor class higher than roll result
        target._armor_class = 16
        self.assertFalse(statblock.ranged_attack_roll(target, "1d4 slashing"))

        # Verify dexterity modifier is added to attack roll
        statblock._ability_scores["dex"].value = 16 #(+3 to DEX)
        self.assertTrue(statblock.ranged_attack_roll(target, "1d4 slashing"))

        # Verify melee attack roll still fails
        self.assertFalse(statblock.melee_attack_roll(target, "1d4 slashing"))
    
    @patch('src.util.dice.DiceRoller.roll_d20', return_value = 15)
    def test_attack_modifier_effects(self, roll_d20):
        # Create statblocks
        statblock = Statblock("Tester")
        target = Statblock("Target")

        # Create effect
        effect = MagicMock(spec=Effect)
        effect._name = "test_effect"

        def test_has_function(function_name):
            return function_name == "make_attack_roll"
        effect.has_function.side_effect = test_has_function

        effect.run.return_value = {"advantage": False, "disadvantage": False, "auto_succeed": False, "auto_fail": False, "bonus": 5}

        # Verify attack roll fails without effect
        target._armor_class = 16
        self.assertFalse(statblock.melee_attack_roll(target, "1d4 slashing"))

        # Add effect to statblock
        statblock.add_effect(effect, 1)

        # Verify attack roll succeeds with effect
        self.assertTrue(statblock.melee_attack_roll(target, "1d4 slashing"))
    
    @patch('src.util.dice.DiceRoller.roll_d20', return_value = 15)
    def test_attack_advantage_effects(self, roll_d20):
        # Create statblocks
        statblock = Statblock("Tester")
        target = Statblock("Target")

        # Create effect
        effect = MagicMock(spec=Effect)
        effect._name = "test_effect"

        def test_has_function(function_name):
            return function_name == "make_attack_roll"
        effect.has_function.side_effect = test_has_function

        effect.run.return_value = {"advantage": True, "disadvantage": False, "auto_succeed": False, "auto_fail": False, "bonus": 0}

        # Verify attack roll is not run with advantage or disadvantage
        statblock.melee_attack_roll(target, "1d4 slashing")
        self.assertFalse(roll_d20.call_args[0][0])
        self.assertFalse(roll_d20.call_args[0][1])

        # Add effect to statblock
        statblock.add_effect(effect, 1)

        # Verify attack roll is run with just advantage
        statblock.melee_attack_roll(target, "1d4 slashing")
        self.assertTrue(roll_d20.call_args[0][0])
        self.assertFalse(roll_d20.call_args[0][1])

        # Change effect to disadvantage
        effect.run.return_value = {"advantage": False, "disadvantage": True, "auto_succeed": False, "auto_fail": False, "bonus": 0}

        # Verify attack roll is just run with disadvantage
        statblock.melee_attack_roll(target, "1d4 slashing")
        self.assertFalse(roll_d20.call_args[0][0])
        self.assertTrue(roll_d20.call_args[0][1])
    
    @patch('src.util.dice.DiceRoller.roll_d20', return_value = 15)
    def test_attack_auto_result(self, roll_d20):
        # Create statblocks
        statblock = Statblock("Tester")
        target = Statblock("Target")

        # Create effect
        effect = MagicMock(spec=Effect)
        effect._name = "test_effect"

        def test_has_function(function_name):
            return function_name == "make_attack_roll"
        effect.has_function.side_effect = test_has_function

        effect.run.return_value = {"advantage": False, "disadvantage": False, "auto_succeed": True, "auto_fail": False, "bonus": 0}

        # Verify nigh-impossible attack roll fails
        target._armor_class = 1000
        self.assertFalse(statblock.melee_attack_roll(target, "1d4 slashing"))
        
        # Verify attack roll succeeds with auto succeed regardless of die result and armor class with effect
        statblock.add_effect(effect, 1)
        self.assertTrue(statblock.melee_attack_roll(target, "1d4 slashing"))

        # Change effect to auto fail and reduce armor class
        effect.run.return_value = {"advantage": False, "disadvantage": False, "auto_succeed": False, "auto_fail": True, "bonus": 0}
        target._armor_class = 0

        # Verify attack roll fails with auto fail regardless of die result and armor class with effect
        self.assertFalse(statblock.melee_attack_roll(target, "1d4 slashing"))
    
    @patch('src.util.dice.DiceRoller.roll_d20', return_value = 20)
    @patch('src.util.dice.DiceRoller.roll_custom', return_value = 0)
    def test_attack_critical_hit(self, roll_custom, roll_d20):
        # Create statblocks
        statblock = Statblock("Tester")
        target = Statblock("Target")

        # Verify critical hit always hits
        target._armor_class = 1000
        self.assertTrue(statblock.melee_attack_roll(target, "1d4 slashing"))

        # Verify die count is doubled on critical hit
        self.assertEqual(2, roll_custom.call_args[0][1])

    @patch('src.util.dice.DiceRoller.roll_d20', return_value = 1)
    def test_attack_critical_miss(self, roll_d20):
        # Create statblocks
        statblock = Statblock("Tester")
        target = Statblock("Target")

        # Verify critical miss always misses
        target._armor_class = 0
        self.assertFalse(statblock.melee_attack_roll(target, "1d4 slashing"))

    @patch('src.util.dice.DiceRoller.roll_d20', return_value = 15)
    @patch('src.util.dice.DiceRoller.roll_custom', return_value = 3)
    def test_attack_damage_string_parse(self, roll_custom, roll_d20):
        # Create statblocks
        statblock = Statblock("Tester")
        target = MagicMock()
        target.get_armor_class.return_value = 10

        # Run attack with multiple damage types
        statblock.melee_attack_roll(target, "1d4 slashing, 2d6+1d4+2 fire, 3d8+4 cold")

        # Verify correct number of dice are rolled for each damage type
        self.assertEqual(1, roll_custom.call_args_list[0][0][1])
        self.assertEqual(2, roll_custom.call_args_list[1][0][1])
        self.assertEqual(1, roll_custom.call_args_list[2][0][1])
        self.assertEqual(3, roll_custom.call_args_list[3][0][1])

        # Verify correct die type is rolled for each damage type
        self.assertEqual(4, roll_custom.call_args_list[0][0][0])
        self.assertEqual(6, roll_custom.call_args_list[1][0][0])
        self.assertEqual(4, roll_custom.call_args_list[2][0][0])
        self.assertEqual(8, roll_custom.call_args_list[3][0][0])

        # Verify the correct amount of damage is being applied
        self.assertEqual(3, target.take_damage.call_args_list[0][0][0])
        self.assertEqual(8, target.take_damage.call_args_list[1][0][0])
        self.assertEqual(7, target.take_damage.call_args_list[2][0][0])

        # Verify the correct damage types are being applied
        self.assertEqual("slashing", target.take_damage.call_args_list[0][0][1])
        self.assertEqual("fire", target.take_damage.call_args_list[1][0][1])
        self.assertEqual("cold", target.take_damage.call_args_list[2][0][1])

    @patch('src.util.dice.DiceRoller.roll_d20', return_value = 15)
    def test_roll_initiative(self, roll_d20):
        # Create statblock
        statblock = Statblock("Tester")

        # Verify initiative roll is returned
        self.assertEqual(15, statblock.roll_initiative())

        # Verify dexterity modifier is added to initiative roll
        statblock._ability_scores["dex"].value = 16 #(+3 to DEX)
        self.assertEqual(18, statblock.roll_initiative())

    @patch('src.util.dice.DiceRoller.roll_d20', return_value = 15)
    def test_roll_initiative_effects(self, roll_d20):
        # Create statblock
        statblock = Statblock("Tester")

        # Create effect
        effect = MagicMock(spec=Effect)
        effect._name = "test_effect"

        def test_has_function(function_name):
            return function_name == "roll_initiative"
        effect.has_function.side_effect = test_has_function

        effect.run.return_value = {"advantage": False, "disadvantage": False, "auto_succeed": False, "auto_fail": False, "bonus": 10}

        # Verify baseline initiative roll
        self.assertEqual(15, statblock.roll_initiative())

        # Add effect to statblock
        statblock.add_effect(effect, 1)

        # Verify initiative roll with effect
        self.assertEqual(25, statblock.roll_initiative())

        # Change effect to grant advantage
        effect.run.return_value = {"advantage": True, "disadvantage": False, "auto_succeed": False, "auto_fail": False, "bonus": 0}

        # Verify initiative roll with just advantage
        statblock.roll_initiative()
        self.assertTrue(roll_d20.call_args[0][0])
        self.assertFalse(roll_d20.call_args[0][1])

        # Change effect to grant disadvantage
        effect.run.return_value = {"advantage": False, "disadvantage": True, "auto_succeed": False, "auto_fail": False, "bonus": 0}

        # Verify initiative roll with just disadvantage
        statblock.roll_initiative()
        self.assertFalse(roll_d20.call_args[0][0])
        self.assertTrue(roll_d20.call_args[0][1])
    
    def test_base_speed(self):
        speed = MagicMock()
        statblock = Statblock("Tester", speed = speed)

        self.assertEqual(speed, statblock.get_base_speed())

    def test_temporary_speed(self):
        speed = MagicMock()
        temp_speed = MagicMock()
        statblock = Statblock("Tester", speed = speed)

        statblock.add_temporary_speed(temp_speed)
        speed.__iadd__.assert_called_with(temp_speed)