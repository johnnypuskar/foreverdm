from src.combat.map.movement import MovementCost
from src.util.dice import DiceParser, DiceRoller
from src.stats.abilities import AbilityIndex
from src.stats.effect_index import EffectIndex
from src.stats.proficiencies import Proficiencies, ProficiencyIndex
from src.stats.resources import ResourceIndex
from src.control.controller import Controller
from src.util.resettable_value import ResettableValue
from src.stats.statistics import AbilityScore, Speed
from src.util.constants import Abilities, Skills, EventType
from src.events.event_context import *

class Statblock:
    def __init__(self, name, speed = Speed(30), size = 5):
        self._name = name
        self._size = size
        self._speed = speed

        self._hp = ResettableValue(10)
        self._temp_hp = 0

        self._level = {}

        self._ability_scores = {
            Abilities.STRENGTH: AbilityScore(Abilities.STRENGTH, 10),
            Abilities.DEXTERITY: AbilityScore(Abilities.DEXTERITY, 10),
            Abilities.CONSTITUTION: AbilityScore(Abilities.CONSTITUTION, 10),
            Abilities.INTELLIGENCE: AbilityScore(Abilities.INTELLIGENCE, 10),
            Abilities.WISDOM: AbilityScore(Abilities.WISDOM, 10),
            Abilities.CHARISMA: AbilityScore(Abilities.CHARISMA, 10)
        }
        self._proficiencies = ProficiencyIndex()

        self._armor_class = 10

        self._abilities = AbilityIndex()
        self._effects = EffectIndex()
        self._abilities.connect(self._effects)
        self._effects.connect(self._abilities)

        self._resources = ResourceIndex()
        self._turn_resources = TurnResources()
        self._controller: Controller = None

        # Equipment
        self._equipped_item = None
        self._offhand_item = None
    
    @property
    def name(self):
        return self._name

    ## Abilities
    def use_ability(self, ability_name, *args):
        # if effect grants use of ability, use that instead
        ability = self._abilities.get_ability(ability_name)
        allow_actions = all(self._effects.get_function_results("allow_actions", self, ability))
        allow_reactions = all(self._effects.get_function_results("allow_reactions", self, ability))
        if not allow_actions and (ability._use_time.is_action() or ability._use_time.is_bonus_action()):
            action_type = "bonus action." if ability._use_time.is_bonus_action() else "action."
            return (False, f"Unable to take {action_type}")
        if not allow_reactions and ability._use_time.is_reaction():
            return (False, "Unable to take reaction.")
        if not self._turn_resources.use_from_use_time(ability._use_time):
            if not ability._use_time.is_special:
                return (False, f"No action remaining to use {ability_name}.")
            else:
                return (False, f"No {str(ability._use_time)} remaining to use {ability_name}.")
        return self._abilities.run(ability_name, self, *args)

    def use_ability_chain(self, main_ability_params, *args):
        # TODO: Check for having the available actions
        for ability_params in (main_ability_params,) + args:
            if not isinstance(ability_params, tuple):
                raise ValueError("Ability chain parameters must be tuples with ability parameters")
            if not isinstance(ability_params[0], str):
                raise ValueError("First ability parameter in tuple must be ability name string")
        return self._abilities.run_sequence(main_ability_params[0], self, args, *main_ability_params[1:])

    def add_ability(self, ability):
        self._abilities.add(ability)

    def remove_ability(self, ability_name):
        self._abilities.remove(ability_name)

    ## Effects and Triggers
    def trigger(self, trigger_name):
        self._effects.get_function_results("on_trigger_" + trigger_name, self)

    def add_effect(self, effect, duration):
        self._effects.add(effect, duration, self)

    def remove_effect(self, effect_name):
        self._effects.remove(effect_name)

    def has_effect(self, effect_name):
        return effect_name in self._effects.effect_names

    async def handle_reaction(self, composite_event):
        if not self._turn_resources._reaction:
            return None
        keyed_valid_abilities = {}
        for event in composite_event.event_entries:
            print(f"{self._name} handling event {event.event_type}: {vars(event.context)}")
            for ability_name in self._abilities.get_headers_reactions_to_event(event.event_type):
                keyed_valid_abilities[ability_name] = event
        if len(keyed_valid_abilities) > 0:
            keyed_valid_abilities["^skip"] = None
            # TODO: More specific ability selection function
            selection = self._controller.select(keyed_valid_abilities.keys())
            if selection == "^skip":
                return None
            return self.use_ability(selection, *keyed_valid_abilities[selection].decompose_context())
        else:
            return None

    def trigger_custom_event(self, custom_event_type):
        self._controller.trigger_reaction(custom_event_type, EventContext(self))

    ## Leveling
    def add_level(self, class_level, levels = 1):
        if class_level not in self._level:
            self._level[class_level] = levels
        else:
            self._level[class_level] += levels

    def get_level(self, class_level = None):
        if class_level is None:
            return sum(self._level.values())
        if class_level not in self._level:
            return 0
        return self._level[class_level]
    
    ## Hit Points
    def get_hit_points(self):
        return self._hp.value
    
    def get_max_hit_points(self):
        return self._hp.initial
    
    def restore_hp(self, amount):
        self._hp.add_capped(amount)
    
    def add_temporary_hp(self, amount):
        if amount > self._temp_hp:
            self._temp_hp = amount
    
    def take_damage(self, damage_string: str, die_multiplier = 1):
        damage_instances = [d for d in damage_string.split(",") if d.strip()]
        overall_damage_table = {}
        for damage_instance in damage_instances:
            if " " not in damage_instance:
                damage_instance += " true"
            damage_dice, damage_type = damage_instance.strip().split(" ")
            damage_table = DiceParser.parse_string(damage_dice)
            overall_damage_table[damage_type] = damage_table
        
        damage_output_table = {}

        # TODO: evaluate if this is still necessary
        roll_context = NumericRollEventContext(self, damage_string)
        self._controller.trigger_reaction(EventType.TRIGGER_ROLL_DAMAGE, roll_context)

        for damage_type, damage_dice_table in overall_damage_table.items():
            damage_sum = 0
            for die_type, amount in damage_dice_table.items():
                if die_type == "MOD":
                    damage_sum += amount
                else:
                    damage_sum += DiceRoller.roll_custom(amount * die_multiplier, die_type)
            damage_output_table[damage_type] = damage_sum
        
        reaction_events = [(EventType.TRIGGER_TAKE_DAMAGE, DamageEventContext(self, event_damage_amount, event_damage_type)) for event_damage_type, event_damage_amount in damage_output_table.items()]
        self._controller.trigger_reactions(reaction_events)

        total_damage = 0

        for damage_event in reaction_events:
            damage_context = damage_event[1]
            if damage_context.proceed and damage_context.amount > 0:
                total_damage += damage_context.amount
                self._damage(damage_context.amount, damage_context.type)

        if self._abilities._concentration_tracker.concentrating:
            concentration_check_dc = max(10, total_damage // 2)
            save_success = self._saving_throw(
                concentration_check_dc, Abilities.CONSTITUTION, None,
                [EventType.TRIGGER_SAVING_THROW_ROLL, EventType.TRIGGER_CONCENTRATION_SAVING_THROW_ROLL],
                [EventType.TRIGGER_SAVING_THROW_SUCCEED, EventType.TRIGGER_CONCENTRATION_SAVING_THROW_SUCCEED],
                [EventType.TRIGGER_SAVING_THROW_FAIL, EventType.TRIGGER_CONCENTRATION_SAVING_THROW_FAIL]
            )[0]
            if not save_success:
                self._abilities._concentration_tracker.end_concentration()


    def _damage(self, amount, type):
        # TODO: Implement damage resistance and vulnerability based on type
        # TODO: Check to make sure the damage type is valid

        if self._temp_hp > 0:
            if amount <= self._temp_hp:
                self._temp_hp -= amount
                return
            else:
                amount -= self._temp_hp
                self._temp_hp = 0
        self._hp -= amount
        if self._hp.value <= 0:
            if abs(self._hp.value) >= self._hp.initial:
                # TODO: Instant death
                pass

            context = EventContext(self)
            self._controller.trigger_reaction(EventType.TRIGGER_ZERO_HP, context)

            self._hp.value = 0

    def kill(self):
        context = EventContext(self)
        self._controller.trigger_reaction(EventType.TRIGGER_DEATH, context)
        
        if not context.proceed:
            return

        # TODO: Replace character in world with corpse

    ## Position - Mostly default, properly implemented via PositionedStatblock
    def get_position(self):
        # Return default position (0, 0)
        return (0, 0)

    def set_position(self, x: int, y: int):
        # Position not stored, no changes made.
        pass

    def in_melee(self, other):
        # Position not stored, assume always in melee.
        return True

    def distance_to(self, other, y: int = None):
        # Defaults to 5 feet away.
        return 5

    def pull_towards(self, x: int, y: int, distance: int):
        # Position not stored, no changes made. Returns (0, 0) as default position.
        return (0, 0)

    def push_from(self, x: int, y: int, distance: int):
        # Position not stored, no changes made. Returns (0, 0) as default position.
        return (0, 0)

    def visibility(self):
        # No environment to check, always have full visibility unless effect prevents it.
        visibility = 2

        visibility_modifiers = self._effects.get_function_results("modify_visibility", self)
        if any(d["operation"] == "multiply" for d in visibility_modifiers):
            raise ValueError("Visibility cannot be multiplied.")
        
        visibility = self._apply_value_modifiers(visibility, visibility_modifiers)
        visibility = max(0, min(2, visibility))

        return visibility

    def sight_to(self, target, perception_value = None):
        # No environment to check, always return targets base visibility.
        if perception_value is None:
            perception_value = self.get_passive_skill("perception")
        noticed_results = target._effects.get_function_results("is_noticed", target, perception_value)
        can_see = True if len(noticed_results) == 0 else any(d for d in noticed_results)
        if not can_see:
            return 0
        return target.visibility()
    
    ## Abilities
    def get_ability_score(self, ability):
        effect_bonus_stats = self._effects.get_function_results("modify_stat", self, ability)
        base_stat = self._ability_scores[ability].value
        return self._apply_value_modifiers(base_stat, effect_bonus_stats)

    def get_ability_modifier(self, ability):
        return self.get_ability_score(ability) // 2 - 5

    ## Proficiencies and Skills
    def get_proficiency_bonus(self):
        return 2 + max(0, ((self.get_level() - 1) // 4))
    
    def add_proficiency(self, proficiency):
        self._proficiencies.add(proficiency)
    
    def remove_proficiency(self, proficiency):
        self._proficiencies.remove(proficiency)
    
    def has_proficiency(self, proficiency):
        effect_proficiencies = self._effects.get_function_results("get_proficiencies", self)
        return proficiency in effect_proficiencies or self._proficiencies.has(proficiency)

    def _get_ability_check_modifiers(self, ability_name, trigger = None):
        self_effect_bonus_stats = self._effects.get_function_results("make_ability_check", self, ability_name, trigger)
        target_effect_bonus_stats = []
        if isinstance(trigger, Statblock):
            target_effect_bonus_stats = trigger._effects.get_function_results("recieve_ability_check", trigger, ability_name, self)
        else: # TODO: Implement target effects for ability checks from objects
            pass

        modifier_table = {
            "advantage": any(d["advantage"] for d in self_effect_bonus_stats + target_effect_bonus_stats),
            "disadvantage": any(d["disadvantage"] for d in self_effect_bonus_stats + target_effect_bonus_stats),
            "auto_succeed": any(d["auto_succeed"] for d in self_effect_bonus_stats + target_effect_bonus_stats),
            "auto_fail": any(d["auto_fail"] for d in self_effect_bonus_stats + target_effect_bonus_stats),
            "bonus": sum(d["bonus"] for d in self_effect_bonus_stats + target_effect_bonus_stats),
        }

        return modifier_table, self.get_ability_modifier(ability_name)

    def _apply_value_modifiers(self, base_stat, value_modifier_table):
        # First, set the base stat to the highest value any effect directly sets it to
        if any(d["operation"] == "set" for d in value_modifier_table):
            base_stat = max(d["value"] for d in value_modifier_table if d["operation"] == "set")
        # Then, multiply the base stat by all the multipliers
        for d in value_modifier_table:
            if d["operation"] == "multiply":
                base_stat = int(d["value"] * base_stat)
        # Finally, add all the bonuses
        base_stat += sum(d["value"] for d in value_modifier_table if d["operation"] == "add")

        return base_stat

    def ability_check(self, dc, ability_name, trigger = None):
        modifier_table, roll_bonus = self._get_ability_check_modifiers(ability_name, trigger)

        return self._determine_d20_roll(
            modifier_table,
            dc,
            roll_bonus,
            [EventType.TRIGGER_ABILITY_CHECK_ROLL],
            [EventType.TRIGGER_ABILITY_CHECK_SUCCEED],
            [EventType.TRIGGER_ABILITY_CHECK_FAIL]
        )

    def saving_throw(self, dc, ability_name, trigger = None):
        return self._saving_throw(dc, ability_name, trigger)

    def _saving_throw(self, dc, ability_name, trigger = None, roll_events = [EventType.TRIGGER_SAVING_THROW_ROLL], success_events= [EventType.TRIGGER_SAVING_THROW_SUCCEED], fail_events = [EventType.TRIGGER_SAVING_THROW_SUCCEED]):
        saving_throw_proficiencies = {
            Abilities.STRENGTH: Proficiencies.SAVING_THROW_STRENGTH,
            Abilities.DEXTERITY: Proficiencies.SAVING_THROW_DEXTERITY,
            Abilities.CONSTITUTION: Proficiencies.SAVING_THROW_CONSTITUTION,
            Abilities.INTELLIGENCE: Proficiencies.SAVING_THROW_INTELLIGENCE,
            Abilities.WISDOM: Proficiencies.SAVING_THROW_WISDOM,
            Abilities.CHARISMA: Proficiencies.SAVING_THROW_CHARISMA
        }

        self_effect_bonus_stats = self._effects.get_function_results("make_saving_throw", self, ability_name, trigger)
        target_effect_bonus_stats = []
        if isinstance(trigger, Statblock):
            target_effect_bonus_stats = trigger._effects.get_function_results("force_saving_throw", trigger, ability_name, self)
        else: # TODO: Implement target effects for saving throws from objects
            pass

        modifier_table = {
            "advantage": any(d["advantage"] for d in self_effect_bonus_stats + target_effect_bonus_stats),
            "disadvantage": any(d["disadvantage"] for d in self_effect_bonus_stats + target_effect_bonus_stats),
            "auto_succeed": any(d["auto_succeed"] for d in self_effect_bonus_stats + target_effect_bonus_stats),
            "auto_fail": any(d["auto_fail"] for d in self_effect_bonus_stats + target_effect_bonus_stats),
            "bonus": sum(d["bonus"] for d in self_effect_bonus_stats + target_effect_bonus_stats),
        }

        return self._determine_d20_roll(
            modifier_table,
            dc,
            self.get_ability_modifier(ability_name) + (self.get_proficiency_bonus() if self.has_proficiency(saving_throw_proficiencies[ability_name]) else 0),
            roll_events,
            success_events,
            fail_events
        )

    def _map_skill_to_ability(self, skill_name):
        skill_ability_map = {
            Skills.ACROBATICS: Abilities.DEXTERITY,
            Skills.ANIMAL_HANDLING: Abilities.WISDOM,
            Skills.ARCANA: Abilities.INTELLIGENCE,
            Skills.ATHLETICS: Abilities.STRENGTH,
            Skills.DECEPTION: Abilities.CHARISMA,
            Skills.HISTORY: Abilities.INTELLIGENCE,
            Skills.INSIGHT: Abilities.WISDOM,
            Skills.INTIMIDATION: Abilities.CHARISMA,
            Skills.INVESTIGATION: Abilities.INTELLIGENCE,
            Skills.MEDICINE: Abilities.WISDOM,
            Skills.NATURE: Abilities.INTELLIGENCE,
            Skills.PERCEPTION: Abilities.WISDOM,
            Skills.PERFORMANCE: Abilities.CHARISMA,
            Skills.PERSUASION: Abilities.CHARISMA,
            Skills.RELIGION: Abilities.INTELLIGENCE,
            Skills.SLEIGHT_OF_HAND: Abilities.DEXTERITY,
            Skills.STEALTH: Abilities.DEXTERITY,
            Skills.SURVIVAL: Abilities.WISDOM
        }
        return skill_ability_map[skill_name]

    def _get_skill_check_modifiers(self, skill_name, trigger = None, ability_name = None):
        skill_proficiencies = {
            Skills.ACROBATICS: Proficiencies.ACROBATICS,
            Skills.ANIMAL_HANDLING: Proficiencies.ANIMAL_HANDLING,
            Skills.ARCANA: Proficiencies.ARCANA,
            Skills.ATHLETICS: Proficiencies.ATHLETICS,
            Skills.DECEPTION: Proficiencies.DECEPTION,
            Skills.HISTORY: Proficiencies.HISTORY,
            Skills.INSIGHT: Proficiencies.INSIGHT,
            Skills.INTIMIDATION: Proficiencies.INTIMIDATION,
            Skills.INVESTIGATION: Proficiencies.INVESTIGATION,
            Skills.MEDICINE: Proficiencies.MEDICINE,
            Skills.NATURE: Proficiencies.NATURE,
            Skills.PERCEPTION: Proficiencies.PERCEPTION,
            Skills.PERFORMANCE: Proficiencies.PERFORMANCE,
            Skills.PERSUASION: Proficiencies.PERSUASION,
            Skills.RELIGION: Proficiencies.RELIGION,
            Skills.SLEIGHT_OF_HAND: Proficiencies.SLIGHT_OF_HAND,
            Skills.STEALTH: Proficiencies.STEALTH,
            Skills.SURVIVAL: Proficiencies.SURVIVAL
        }

        self_effect_bonus_stats = self._effects.get_function_results("make_skill_check", self, skill_name, trigger)
        target_effect_bonus_stats = []
        if isinstance(trigger, Statblock):
            target_effect_bonus_stats = trigger._effects.get_function_results("recieve_skill_check", trigger, skill_name, self)
        else: # TODO: Implement target effects for skill checks from objects
            pass

        modifier_table = {
            "advantage": any(d["advantage"] for d in self_effect_bonus_stats + target_effect_bonus_stats),
            "disadvantage": any(d["disadvantage"] for d in self_effect_bonus_stats + target_effect_bonus_stats),
            "auto_succeed": any(d["auto_succeed"] for d in self_effect_bonus_stats + target_effect_bonus_stats),
            "auto_fail": any(d["auto_fail"] for d in self_effect_bonus_stats + target_effect_bonus_stats),
            "bonus": sum(d["bonus"] for d in self_effect_bonus_stats + target_effect_bonus_stats),
        }
        skill_bonus = self.get_ability_modifier(ability_name) + (self.get_proficiency_bonus() if self.has_proficiency(skill_proficiencies[skill_name]) else 0)

        return modifier_table, skill_bonus

    def get_skill_roll(self, skill_name, ability_name = None):
        if ability_name is None:
            ability_name = self._map_skill_to_ability(skill_name)
        
        ability_modifier_table, _ = self._get_ability_check_modifiers(ability_name)
        skill_modifier_table, roll_bonus = self._get_skill_check_modifiers(skill_name, None, ability_name)

        modifier_table = {
            "advantage": ability_modifier_table["advantage"] or skill_modifier_table["advantage"],
            "disadvantage": ability_modifier_table["disadvantage"] or skill_modifier_table["disadvantage"],
            "auto_succeed": ability_modifier_table["auto_succeed"] or skill_modifier_table["auto_succeed"],
            "auto_fail": ability_modifier_table["auto_fail"] or skill_modifier_table["auto_fail"],
            "bonus": ability_modifier_table["bonus"] + skill_modifier_table["bonus"]
        }

        return DiceRoller.roll_d20(modifier_table["advantage"], modifier_table["disadvantage"]) + roll_bonus + modifier_table["bonus"]

    def skill_check(self, dc, skill_name, trigger = None, ability_name = None):
        if ability_name is None:
            ability_name = self._map_skill_to_ability(skill_name)
        
        ability_modifier_table, _ = self._get_ability_check_modifiers(ability_name, trigger)
        skill_modifier_table, roll_bonus = self._get_skill_check_modifiers(skill_name, trigger, ability_name)

        modifier_table = {
            "advantage": ability_modifier_table["advantage"] or skill_modifier_table["advantage"],
            "disadvantage": ability_modifier_table["disadvantage"] or skill_modifier_table["disadvantage"],
            "auto_succeed": ability_modifier_table["auto_succeed"] or skill_modifier_table["auto_succeed"],
            "auto_fail": ability_modifier_table["auto_fail"] or skill_modifier_table["auto_fail"],
            "bonus": ability_modifier_table["bonus"] + skill_modifier_table["bonus"]
        }

        return self._determine_d20_roll(
            modifier_table,
            dc,
            roll_bonus,
            [EventType.TRIGGER_SKILL_CHECK_ROLL],
            [EventType.TRIGGER_SKILL_CHECK_SUCCEED],
            [EventType.TRIGGER_SKILL_CHECK_FAIL]
        )

    def get_passive_skill(self, skill_name):
        skill_roll_modifiers, roll_bonus = self._get_skill_check_modifiers(skill_name, None, self._map_skill_to_ability(skill_name))

        passive_score = 10 + roll_bonus
        passive_score += 5 if skill_roll_modifiers["advantage"] else 0
        passive_score -= 5 if skill_roll_modifiers["disadvantage"] else 0

        self_effect_passive_modifiers = self._effects.get_function_results("modify_passive_skill", self, skill_name)
        return self._apply_value_modifiers(passive_score, self_effect_passive_modifiers)

    def _determine_d20_roll(self, modifier_table, dc, roll_skill_bonus, roll_events, success_events, fail_events):
        die_result = DiceRoller.roll_d20(modifier_table["advantage"], modifier_table["disadvantage"])
        return self._handle_d20_roll(die_result, modifier_table, dc, roll_skill_bonus, roll_events, success_events, fail_events)

    def _handle_d20_roll(self, die_result, modifier_table, dc, roll_skill_bonus, roll_events, success_events, fail_events):
        roll_context = RollEventContext(self, modifier_table["advantage"], modifier_table["disadvantage"], modifier_table["auto_succeed"], modifier_table["auto_fail"], modifier_table["bonus"])
        self._controller.trigger_reactions([(event, roll_context) for event in roll_events])
        
        if roll_context.auto_fail or not roll_context.proceed:
            return False

        roll_result = die_result + roll_context.bonus + roll_skill_bonus
        result_context = RollResultEventContext(self, roll_result, roll_result >= dc, die_result == 20)
        
        if not (roll_context.auto_succeed or result_context.success):
            self._controller.trigger_reactions([(fail_event, result_context) for fail_event in fail_events])
        if roll_context.auto_succeed or result_context.success:
            self._controller.trigger_reactions([(success_event, result_context) for success_event in success_events])

            if not result_context.proceed:
                return False, roll_result
            return True, roll_result
        return False, roll_result

    ## Combat Statistics
    def get_armor_class(self):
        effect_bonus_stats = self._effects.get_function_results("modify_armor_class", self)
        base_armor_class = self._armor_class

        if any(d["operation"] == "set" for d in effect_bonus_stats):
            base_armor_class = max(d["value"] for d in effect_bonus_stats if d["operation"] == "set")
        base_armor_class += sum(d["value"] for d in effect_bonus_stats if d["operation"] == "add")

        return base_armor_class
    
    def roll_initiative(self):
        effect_roll_modifiers = self._effects.get_function_results("roll_initiative", self)
        modifier_table = {
            "advantage": any(d["advantage"] for d in effect_roll_modifiers),
            "disadvantage": any(d["disadvantage"] for d in effect_roll_modifiers),
            "bonus": sum(d["bonus"] for d in effect_roll_modifiers)
        }
        return DiceRoller.roll_d20(modifier_table["advantage"], modifier_table["disadvantage"]) + self.get_ability_modifier(Abilities.DEXTERITY) + modifier_table["bonus"]

    def melee_attack_roll(self, target, damage_string):
        effect_bonus_stats = ['str'] + list(self._effects.get_function_results("get_melee_attack_stat", self))
        return self._attack_roll(target, max(effect_bonus_stats, key = lambda x: self.get_ability_modifier(x)), damage_string, EventType.TRIGGER_ATTACK_ROLL_MELEE)
    
    def ranged_attack_roll(self, target, damage_string):
        effect_bonus_stats = ['dex'] + self._effects.get_function_results("get_ranged_attack_stat", self)
        return self._attack_roll(target, max(effect_bonus_stats, key = lambda x: self.get_ability_modifier(x)), damage_string, EventType.TRIGGER_ATTACK_ROLL_RANGED)

    def ability_attack_roll(self, target, ability_name, damage_string):
        # TODO: Properly pass melee or ranged attack type to internal attack roll function
        return self._attack_roll(target, ability_name, damage_string, EventType.TRIGGER_ATTACK_ROLL_RANGED)

    def _attack_roll(self, target, attack_stat, damage_string, attack_type_event):
        effect_roll_modifiers = self._effects.get_function_results("make_attack_roll", self, target) + target._effects.get_function_results("recieve_attack_roll", target, self)
        modifier_table = {
            "advantage": any(d["advantage"] for d in effect_roll_modifiers),
            "disadvantage": any(d["disadvantage"] for d in effect_roll_modifiers),
            "auto_succeed": any(d["auto_succeed"] for d in effect_roll_modifiers),
            "auto_fail": any(d["auto_fail"] for d in effect_roll_modifiers),
            "bonus": sum(d["bonus"] for d in effect_roll_modifiers),
            "critical_threshold_modifier": [d["critical_threshold_modifier"] for d in effect_roll_modifiers if "critical_threshold_modifier" in d]
        }
        
        roll_context = AttackRollEventContext(self, target, modifier_table["advantage"], modifier_table["disadvantage"], modifier_table["auto_succeed"], modifier_table["auto_fail"], modifier_table["bonus"])
        self._controller.trigger_reaction(EventType.TRIGGER_ATTACK_ROLL, roll_context)

        if roll_context.auto_fail or not roll_context.proceed:
            return False
        
        # Critical hit threshold does not use helper function, because set must set to minimum rather than maximum
        critical_threshold = 20
        if any(d["operation"] == "set" for d in modifier_table["critical_threshold_modifier"]):
            critical_threshold = min(d["value"] for d in modifier_table["critical_threshold_modifier"] if d["operation"] == "set")
        # Then, multiply the base stat by all the multipliers
        for d in modifier_table["critical_threshold_modifier"]:
            if d["operation"] == "multiply":
                critical_threshold = int(d["value"] * critical_threshold)
        critical_threshold += sum(d["value"] for d in modifier_table["critical_threshold_modifier"] if d["operation"] == "add")

        # TODO: Factor in proficiency bonus for equipped weapons
        roll_result = DiceRoller.roll_d20(roll_context.advantage, roll_context.disadvantage)
        result_context = TargetedRollResultEventContext(self, target, roll_result, roll_result >= critical_threshold or roll_context.auto_succeed or (roll_result != 1 and roll_result + self.get_ability_modifier(attack_stat) + roll_context.bonus >= target.get_armor_class()), roll_result >= critical_threshold)
        
        if roll_result == 1 or not (roll_context.auto_succeed or result_context.success):
            self._controller.trigger_reaction(EventType.TRIGGER_ATTACK_ROLL_FAIL, result_context)
        if roll_result == critical_threshold or roll_context.auto_succeed or result_context.success:

            events = [(EventType.TRIGGER_ATTACK_ROLL_SUCCEED, result_context)]
            if result_context.critical_success:
                events.append((EventType.TRIGGER_ATTACK_ROLL_CRITICAL, result_context))
            self._controller.trigger_reactions(events)

            if not result_context.proceed:
                return False

            hit_context = TargetedEventContext(target, self)
            target._controller.trigger_reaction(EventType.TRIGGER_HIT_BY_ATTACK, hit_context)

            target.take_damage(damage_string, 2 if result_context.critical_success else 1)

            return True
        return False

    ## Speed and Movement
    def get_speed(self):
        speed_values = {
            "walk": self._speed.walk,
            "fly": self._speed.fly,
            "swim": self._speed.swim,
            "climb": self._speed.climb,
            "burrow": self._speed.burrow,
            "hover": self._speed.hover
        }
        hover_defined = None

        effect_bonus_stats = self._effects.get_function_results("modify_speed", self)

        for speed_type in speed_values.keys():
            set_value = None
            add_value = 0
            multiplier_value = 1
            for effect_bonus_stat in effect_bonus_stats:
                modifier = effect_bonus_stat[speed_type]
                if speed_type == "hover":
                    if modifier is not None:
                        hover_defined = modifier and hover_defined if hover_defined is not None else modifier
                    continue
                if modifier["operation"] == "set":
                    set_value = max(set_value, modifier["value"]) if set_value is not None else modifier["value"]
                elif modifier["operation"] == "add":
                    add_value += modifier["value"]
                elif modifier["operation"] == "multiply":
                    multiplier_value *= modifier["value"]
            if speed_type != "hover":
                if set_value is not None:
                    speed_values[speed_type] = set_value
                speed_values[speed_type] += add_value
                speed_values[speed_type] *= multiplier_value
        
        return Speed(speed_values["walk"], speed_values["fly"], speed_values["swim"], speed_values["climb"], speed_values["burrow"], hover_defined if hover_defined is not None else self._speed.hover)

    def expend_speed(self, speed_modifier):
        walk_cost = speed_modifier["walk"].value
        if speed_modifier["walk"].operation == "set":
            walk_cost = max(0, walk_cost - self._speed.walk)
        elif speed_modifier["walk"].operation == "multiply":
            walk_cost = max(0, self._speed.walk * (1 - walk_cost))
        
        fly_cost = speed_modifier["fly"].value
        if speed_modifier["fly"].operation == "set":
            fly_cost = max(0, fly_cost - self._speed.fly)
        elif speed_modifier["fly"].operation == "multiply":
            fly_cost = max(0, self._speed.fly * (1 - fly_cost))

        swim_cost = speed_modifier["swim"].value
        if speed_modifier["swim"].operation == "set":
            swim_cost = max(0, swim_cost - self._speed.swim)
        elif speed_modifier["swim"].operation == "multiply":
            swim_cost = max(0, self._speed.swim * (1 - swim_cost))

        climb_cost = speed_modifier["climb"].value
        if speed_modifier["climb"].operation == "set":
            climb_cost = max(0, climb_cost - self._speed.climb)
        elif speed_modifier["climb"].operation == "multiply":
            climb_cost = max(0, self._speed.climb * (1 - climb_cost))

        burrow_cost = speed_modifier["burrow"].value
        if speed_modifier["burrow"].operation == "set":
            burrow_cost = max(0, burrow_cost - self._speed.burrow)
        elif speed_modifier["burrow"].operation == "multiply":
            burrow_cost = max(0, self._speed.burrow * (1 - burrow_cost))
        
        cost = MovementCost(walk_cost, fly_cost, swim_cost, climb_cost, burrow_cost)
        return self._speed.move(cost)

    def add_temporary_speed(self, new_speed):
        self._speed += new_speed

class TurnResources:
    def __init__(self):
        self._action = True
        self._bonus_action = True
        self._reaction = True
        self._free_object_interaction = True
    
    def reset(self):
        self._action = True
        self._bonus_action = True
        self._reaction = True
        self._free_object_interaction = True
    
    def can_use(self, use_time):
        if use_time.is_special:
            if use_time.is_action:
                return self._action
            elif use_time.is_bonus_action:
                return self._bonus_action
            elif use_time.is_reaction:
                return self._reaction
        else:
            return self._action
        return False  # Failsafe

    def use_from_use_time(self, use_time):
        if use_time.is_special:
            if use_time.is_action:
                return self.use_action()
            elif use_time.is_bonus_action:
                return self.use_bonus_action()
            elif use_time.is_reaction:
                return self.use_reaction()
        else:
            return self.use_action()
        return False  # Failsafe

    def use_action(self):
        if self._action:
            self._action = False
            return True
        return False
    
    def use_bonus_action(self):
        if self._bonus_action:
            self._bonus_action = False
            return True
        return False
    
    def use_reaction(self):
        if self._reaction:
            self._reaction = False
            return True
        return False    
    
    def use_free_object_interaction(self):
        if self._free_object_interaction:
            self._free_object_interaction = False
            return True
        return False