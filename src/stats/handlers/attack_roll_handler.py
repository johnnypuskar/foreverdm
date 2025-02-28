from src.util.dice.dice_roller import DiceRoller
from src.util.return_status import ReturnStatus
from src.events.event_context import AttackRollEventContext, TargetedEventContext, TargetedRollResultEventContext
from src.util.constants import EventType
from src.stats.handlers.ability_score_handler import AbilityScoreHandler
from src.stats.handlers.hit_point_handler import HitPointHandler
from src.util.modifier_values import ModifierRolls

class AttackRollHandler:
    def __init__(self, statblock, dice_roller = None):
        self._statblock = statblock
        self._dice_roller = self._statblock._dice_roller if dice_roller is None else dice_roller
    
    def melee_attack_roll(self, target, damage_string):
        attack_stats = [AbilityScoreHandler.ABILITIES.STRENGTH.value] + self._statblock._effects.get_function_results("get_melee_attack_stat", self._statblock)
        return self._handle_attack_roll(target, max(attack_stats, key = lambda stat: AbilityScoreHandler(self._statblock).get_ability_modifier(stat)), damage_string, EventType.TRIGGER_ATTACK_ROLL_MELEE)

    def ranged_attack_roll(self, target, damage_string):
        attack_stats = [AbilityScoreHandler.ABILITIES.DEXTERITY.value] + self._statblock._effects.get_function_results("get_ranged_attack_stat", self._statblock)
        return self._handle_attack_roll(target, max(attack_stats, key = lambda stat: AbilityScoreHandler(self._statblock).get_ability_modifier(stat)), damage_string, EventType.TRIGGER_ATTACK_ROLL_RANGED)

    def ability_attack_roll(self, target, attack_stat, damage_string):
        return self._handle_attack_roll(target, attack_stat, damage_string, EventType.TRIGGER_ATTACK_ROLL_RANGED)

    def _handle_attack_roll(self, target, attack_stat, damage_string, attack_type_event):
        attack_modifiers = ModifierRolls(self._statblock._effects.get_function_results("make_attack_roll", self._statblock, target))
        attack_modifiers.merge(ModifierRolls(target._effects.get_function_results("receive_attack_roll", target, self._statblock)))

        attack_roll_context = AttackRollEventContext(self._statblock, target, attack_modifiers.advantage, attack_modifiers.disadvantage, attack_modifiers.auto_succeed, attack_modifiers.auto_fail, attack_modifiers.bonus)
        self._statblock._controller.trigger_reaction(EventType.TRIGGER_ATTACK_ROLL, attack_roll_context)

        if attack_roll_context.auto_fail or not attack_roll_context.proceed:
            return ReturnStatus(False, "Attack failed.")
        
        critical_threshold = 20
        critical_threshold = attack_modifiers.process_crit_threshold_mult(critical_threshold)
        critical_threshold = attack_modifiers.process_crit_threshold_add(critical_threshold)
        critical_threshold = attack_modifiers.process_crit_threshold_set_max(critical_threshold)

        # TODO: Factor in proficiency bonus for equipped weapons

        attack_ability_modifier = AbilityScoreHandler(self._statblock).get_ability_modifier(attack_stat)
        roll_result = self._dice_roller.roll_d20(attack_roll_context.advantage, attack_roll_context.disadvantage)
        success = roll_result >= critical_threshold or attack_roll_context.auto_succeed or \
            (roll_result != 1 and roll_result + attack_ability_modifier + attack_roll_context.bonus >= target.get_armor_class())
        result_context = TargetedRollResultEventContext(self._statblock, target, roll_result, success, roll_result >= critical_threshold)

        if roll_result == 1 or not (attack_roll_context.auto_succeed or result_context.success):
            self._statblock._controller.trigger_reaction(EventType.TRIGGER_ATTACK_ROLL_FAIL, result_context)
        if roll_result >= critical_threshold or attack_roll_context.auto_succeed or result_context.success:
            events = [(EventType.TRIGGER_ATTACK_ROLL_SUCCEED, result_context)]
            if result_context.critical_success:
                events.append((EventType.TRIGGER_ATTACK_ROLL_CRITICAL, result_context))
            self._statblock._controller.trigger_reactions(events)

            if not result_context.proceed:
                return ReturnStatus(False, "Attack roll failed.")
            
            hit_context = TargetedEventContext(self._statblock, target)
            target._controller.trigger_reaction(EventType.TRIGGER_HIT_BY_ATTACK, hit_context)

            damage_result = HitPointHandler(target, self._dice_roller).take_damage(f"{max(0, attack_ability_modifier)}+" + damage_string, 2 if result_context.critical_success else 1)

            return ReturnStatus(True, f"Hit attack for {damage_result} total damage.")
        return ReturnStatus(False, "Attack did not hit.")


