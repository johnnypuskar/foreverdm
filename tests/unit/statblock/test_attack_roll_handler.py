import unittest
from unittest.mock import MagicMock, patch
from src.stats.handlers.attack_roll_handler import AttackRollHandler

class TestAttackRollHandler(unittest.TestCase):
    STATBLOCK = None
    TARGET = None

    STR = 10
    DEX = 10
    OTHER_ABILITY = 10

    SELF_ATTACK = []
    TARGET_ATTACKED = []

    @patch('src.stats.statblock.Statblock')
    @patch('src.stats.statblock.Statblock')
    def setUp(self, statblock, target):
        self.STATBLOCK = statblock
        self.TARGET = target

        self.STATBLOCK.get_proficiency_bonus.return_value = 2
        self.STATBLOCK._effects.get_function_results.side_effect = lambda function_name, *args: (
            self.SELF_ATTACK if function_name == "make_attack_roll" else
            []
        )
        self.STATBLOCK._ability_scores.get_ability.side_effect = lambda ability_name: (
            MagicMock(value = self.STR) if ability_name == "strength" else
            MagicMock(value = self.DEX) if ability_name == "dexterity" else
            MagicMock(value = self.OTHER_ABILITY)
        )

        
        self.TARGET._effects.get_function_results.side_effect = lambda function_name, *args: (
            self.TARGET_ATTACKED if function_name == "receive_attack_roll" else
            []
        )
        self.TARGET.get_armor_class.return_value = 15
        self.TARGET._hit_points = MagicMock(_hp = 100, _max_hp = 100)
        self.TARGET._hit_points.get_hp.side_effect = lambda: target._hit_points._hp
        self.TARGET._hit_points.reduce_hp.side_effect = lambda amount: setattr(target._hit_points, "_hp", target._hit_points._hp - amount)
        self.assertEqual(100, target._hit_points._hp)
    
    @patch('src.util.dice.DiceRoller.roll_d20')
    @patch('src.util.dice.DiceRoller.roll_custom')
    def test_attack_roll_bonuses(self, roll_damage, roll_d20):
        statblock = self.STATBLOCK
        target = self.TARGET
        roll_damage.side_effect = lambda amount, sides: amount * sides

        roll_d20.return_value = 14
        self.assertFalse(AttackRollHandler(statblock).melee_attack_roll(target, "5 slashing").success)
        self.assertEqual(100, target._hit_points._hp)

        self.SELF_ATTACK = [{"bonus": 1}]
        self.TARGET_ATTACKED = []
        target._hit_points._hp = 100
        self.assertTrue(AttackRollHandler(statblock).melee_attack_roll(target, "5 slashing").success)
        self.assertEqual(95, target._hit_points._hp)

        self.SELF_ATTACK = []
        self.TARGET_ATTACKED = [{"bonus": 1}]
        target._hit_points._hp = 100
        self.assertTrue(AttackRollHandler(statblock).melee_attack_roll(target, "5 slashing").success)
        self.assertEqual(95, target._hit_points._hp)

        roll_d20.reset_mock()
        self.SELF_ATTACK = [{"advantage": True}]
        self.TARGET_ATTACKED = []
        target._hit_points._hp = 100
        self.assertFalse(AttackRollHandler(statblock).melee_attack_roll(target, "5 slashing").success)
        self.assertEqual(100, target._hit_points._hp)
        self.assertTrue(roll_d20.call_args[0][0])
        self.assertFalse(roll_d20.call_args[0][1])

        roll_d20.reset_mock()
        self.SELF_ATTACK = []
        self.TARGET_ATTACKED = [{"advantage": True}]
        self.assertFalse(AttackRollHandler(statblock).melee_attack_roll(target, "5 slashing").success)
        self.assertEqual(100, target._hit_points._hp)
        self.assertTrue(roll_d20.call_args[0][0])
        self.assertFalse(roll_d20.call_args[0][1])

        roll_d20.reset_mock()
        self.SELF_ATTACK = [{"disadvantage": True}]
        self.TARGET_ATTACKED = []
        self.assertFalse(AttackRollHandler(statblock).melee_attack_roll(target, "5 slashing").success)
        self.assertEqual(100, target._hit_points._hp)
        self.assertFalse(roll_d20.call_args[0][0])
        self.assertTrue(roll_d20.call_args[0][1])

        roll_d20.reset_mock()
        self.SELF_ATTACK = []
        self.TARGET_ATTACKED = [{"disadvantage": True}]
        self.assertFalse(AttackRollHandler(statblock).melee_attack_roll(target, "5 slashing").success)
        self.assertEqual(100, target._hit_points._hp)
        self.assertFalse(roll_d20.call_args[0][0])
        self.assertTrue(roll_d20.call_args[0][1])

        roll_d20.reset_mock()
        self.SELF_ATTACK = [{"advantage": True}]
        self.TARGET_ATTACKED = [{"disadvantage": True}]
        self.assertFalse(AttackRollHandler(statblock).melee_attack_roll(target, "5 slashing").success)
        self.assertEqual(100, target._hit_points._hp)
        self.assertTrue(roll_d20.call_args[0][0])
        self.assertTrue(roll_d20.call_args[0][1])

        roll_d20.reset_mock()
        roll_d20.return_value = 1
        target.get_armor_class.return_value = 50
        self.SELF_ATTACK = [{"auto_succeed": True}]
        self.TARGET_ATTACKED = []
        self.assertTrue(AttackRollHandler(statblock).melee_attack_roll(target, "5 slashing").success)
        self.assertEqual(95, target._hit_points._hp)
        
        self.SELF_ATTACK = []
        self.TARGET_ATTACKED = [{"auto_succeed": True}]
        target._hit_points._hp = 100
        self.assertTrue(AttackRollHandler(statblock).melee_attack_roll(target, "5 slashing").success)
        self.assertEqual(95, target._hit_points._hp)

        roll_d20.reset_mock()
        roll_d20.return_value = 19
        target.get_armor_class.return_value = 1
        self.SELF_ATTACK = [{"auto_fail": True}]
        self.TARGET_ATTACKED = []
        target._hit_points._hp = 100
        self.assertFalse(AttackRollHandler(statblock).melee_attack_roll(target, "5 slashing").success)
        self.assertEqual(100, target._hit_points._hp)

        self.SELF_ATTACK = []
        self.TARGET_ATTACKED = [{"auto_fail": True}]
        self.assertFalse(AttackRollHandler(statblock).melee_attack_roll(target, "5 slashing").success)
        self.assertEqual(100, target._hit_points._hp)

        self.SELF_ATTACK = [{"auto_succeed": True}]
        self.assertFalse(AttackRollHandler(statblock).melee_attack_roll(target, "5 slashing").success)
        self.assertEqual(100, target._hit_points._hp)
    
    @patch('src.util.dice.DiceRoller.roll_d20')
    @patch('src.util.dice.DiceRoller.roll_custom')
    def test_melee_attack(self, roll_damage, roll_d20):
        statblock = self.STATBLOCK
        target = self.TARGET
        roll_damage.side_effect = lambda amount, sides: amount * sides

        roll_d20.return_value = 14
        self.assertFalse(AttackRollHandler(statblock).melee_attack_roll(target, "5 slashing").success)
        self.assertEqual(100, target._hit_points._hp)

        self.DEX = 14
        self.assertFalse(AttackRollHandler(statblock).melee_attack_roll(target, "5 slashing").success)
        self.assertEqual(100, target._hit_points._hp)

        self.STR = 14
        self.assertTrue(AttackRollHandler(statblock).melee_attack_roll(target, "5 slashing").success)
        self.assertEqual(93, target._hit_points._hp)

        self.STR = 7
        self.assertFalse(AttackRollHandler(statblock).melee_attack_roll(target, "5 slashing").success)
        self.assertEqual(93, target._hit_points._hp)
        roll_d20.return_value = 17
        self.assertTrue(AttackRollHandler(statblock).melee_attack_roll(target, "5 slashing").success)
        self.assertEqual(88, target._hit_points._hp)
    
    @patch('src.util.dice.DiceRoller.roll_d20')
    @patch('src.util.dice.DiceRoller.roll_custom')
    def test_ranged_attack(self, roll_damage, roll_d20):
        statblock = self.STATBLOCK
        target = self.TARGET
        roll_damage.side_effect = lambda amount, sides: amount * sides

        roll_d20.return_value = 14
        self.assertFalse(AttackRollHandler(statblock).ranged_attack_roll(target, "5 piercing").success)
        self.assertEqual(100, target._hit_points._hp)

        self.STR = 14
        self.assertFalse(AttackRollHandler(statblock).ranged_attack_roll(target, "5 piercing").success)
        self.assertEqual(100, target._hit_points._hp)

        self.DEX = 14
        self.assertTrue(AttackRollHandler(statblock).ranged_attack_roll(target, "5 piercing").success)
        self.assertEqual(93, target._hit_points._hp)

        self.DEX = 7
        self.assertFalse(AttackRollHandler(statblock).ranged_attack_roll(target, "5 piercing").success)
        self.assertEqual(93, target._hit_points._hp)
        roll_d20.return_value = 17
        self.assertTrue(AttackRollHandler(statblock).ranged_attack_roll(target, "5 piercing").success)
        self.assertEqual(88, target._hit_points._hp)

    @patch('src.util.dice.DiceRoller.roll_d20')
    @patch('src.util.dice.DiceRoller.roll_custom')
    def test_ability_score_attack(self, roll_damage, roll_d20):
        statblock = self.STATBLOCK
        target = self.TARGET
        roll_damage.side_effect = lambda amount, sides: amount * sides

        roll_d20.return_value = 14
        self.assertFalse(AttackRollHandler(statblock).ability_attack_roll(target, "charisma", "5 slashing").success)
        self.assertEqual(100, target._hit_points._hp)

        self.STR = 14
        self.assertFalse(AttackRollHandler(statblock).ability_attack_roll(target, "charisma", "5 slashing").success)
        self.assertEqual(100, target._hit_points._hp)

        self.DEX = 14
        self.assertFalse(AttackRollHandler(statblock).ability_attack_roll(target, "charisma", "5 slashing").success)
        self.assertEqual(100, target._hit_points._hp)

        self.OTHER_ABILITY = 14
        self.assertTrue(AttackRollHandler(statblock).ability_attack_roll(target, "charisma", "5 slashing").success)
        self.assertEqual(93, target._hit_points._hp)

        self.OTHER_ABILITY = 7
        self.assertFalse(AttackRollHandler(statblock).ability_attack_roll(target, "charisma", "5 slashing").success)
        self.assertEqual(93, target._hit_points._hp)
        roll_d20.return_value = 17
        self.assertTrue(AttackRollHandler(statblock).ability_attack_roll(target, "charisma", "5 slashing").success)
        self.assertEqual(88, target._hit_points._hp)
    
    @patch('src.util.dice.DiceRoller.roll_d20')
    @patch('src.util.dice.DiceRoller.roll_custom')
    def test_critical_hit(self, roll_damage, roll_d20):
        statblock = self.STATBLOCK
        target = self.TARGET
        roll_damage.side_effect = lambda amount, sides: amount * sides

        roll_d20.return_value = 10
        self.assertFalse(AttackRollHandler(statblock).melee_attack_roll(target, "2d4+1 slashing").success)
        self.assertEqual(100, target._hit_points._hp)

        roll_d20.return_value = 19
        self.assertTrue(AttackRollHandler(statblock).melee_attack_roll(target, "2d4+1 slashing").success)
        self.assertEqual(91, target._hit_points._hp)

        roll_d20.return_value = 20
        target._hit_points._hp = 100
        self.assertTrue(AttackRollHandler(statblock).melee_attack_roll(target, "2d4+1 slashing").success)
        self.assertEqual(83, target._hit_points._hp)

        roll_d20.return_value = 20
        target._hit_points._hp = 100
        target.get_armor_class.return_value = 50
        self.assertTrue(AttackRollHandler(statblock).melee_attack_roll(target, "3d4+1 slashing").success)
        self.assertEqual(75, target._hit_points._hp)
    
    @patch('src.util.dice.DiceRoller.roll_d20')
    @patch('src.util.dice.DiceRoller.roll_custom')
    def test_critical_threshold(self, roll_damage, roll_d20):
        statblock = self.STATBLOCK
        target = self.TARGET
        roll_damage.side_effect = lambda amount, sides: amount * sides
        
        def verify_critical_threshold(critical_threshold):
            target.get_armor_class.return_value = 50
            for i in range(1, 21):
                target._hit_points._hp = 30
                roll_d20.return_value = i
                result = AttackRollHandler(statblock).melee_attack_roll(target, "1d10 slashing")
                self.assertEqual(i >= critical_threshold, result.success, f"Attack roll was critical hit ({result.success}) at a d20 roll of {i} and threshold of {critical_threshold}, should be {i >= critical_threshold}")

        verify_critical_threshold(20)

        self.SELF_ATTACK = [{"critical_threshold_modifier": {"operation": "add", "value": -1}}]
        verify_critical_threshold(19)

        self.SELF_ATTACK = [{"critical_threshold_modifier": {"operation": "multiply", "value": 0.5}}]
        verify_critical_threshold(10)

        self.SELF_ATTACK = [{"critical_threshold_modifier": {"operation": "set", "value": 15}}]
        verify_critical_threshold(15)

        self.SELF_ATTACK = [
            {"critical_threshold_modifier": {"operation": "add", "value": -5}},
            {"critical_threshold_modifier": {"operation": "multiply", "value": 0.75}},
        ]
        verify_critical_threshold(10)

        self.SELF_ATTACK = [
            {"critical_threshold_modifier": {"operation": "add", "value": -10}},
            {"critical_threshold_modifier": {"operation": "multiply", "value": 0.5}},
            {"critical_threshold_modifier": {"operation": "set", "value": 19}},
        ]
        verify_critical_threshold(19)

    # TODO: Attacks with equipped weapon proficiency