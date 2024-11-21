from src.events.event_manager import EventManager
from src.util.dice import DiceParser, DiceRoller
from src.stats.abilities import AbilityIndex
from src.stats.effects import EffectIndex
from src.stats.proficiencies import Proficiencies, ProficiencyIndex
from src.stats.resources import ResourceIndex
from src.control.controller import Controller
from src.util.resettable_value import ResettableValue
from src.stats.statistics import AbilityScore, Speed
from src.util.constants import Abilities, Skills, EventType
from src.util.time import UseTime
from src.events.event_context import *
from src.events.event import ReactionEvent, CompositeEvent

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
        if not self._turn_resources.use_from_use_time(ability._use_time):
            if not ability._use_time.is_special:
                return (False, f"No action remaining to use {ability_name}.")
            else:
                return (False, f"No {str(ability._use_time)} remaining to use {ability_name}.")
        return self._abilities.run(ability_name, self, *args)

    def use_ability_chain(self, main_ability_params, *args):
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
        self._effects.add(effect, duration)

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
            )
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

    ## Abilities
    def get_ability_score(self, ability):
        effect_bonus_stats = self._effects.get_function_results("modify_stat", self, ability)
        base_stat = self._ability_scores[ability].value

        # First, set the base stat to the highest value any effect directly sets it to
        if any(d["operation"] == "set" for d in effect_bonus_stats):
            base_stat = max(d["value"] for d in effect_bonus_stats if d["operation"] == "set")
        # Then, add all the bonuses
        base_stat += sum(d["value"] for d in effect_bonus_stats if d["operation"] == "add")

        return base_stat

    def get_ability_modifier(self, ability):
        return self.get_ability_score(ability) // 2 - 5

    ## Proficiencies and Skills
    def get_proficiency_bonus(self):
        return 2 + ((self.get_level() - 1) // 4)
    
    def add_proficiency(self, proficiency):
        self._proficiencies.add(proficiency)
    
    def remove_proficiency(self, proficiency):
        self._proficiencies.remove(proficiency)
    
    def has_proficiency(self, proficiency):
        effect_proficiencies = self._effects.get_function_results("get_proficiencies", self)
        return proficiency in effect_proficiencies or self._proficiencies.has(proficiency)

    def ability_check(self, dc, ability_name, trigger = None):
        self_effect_bonus_stats = self._effects.get_function_results("ability_check_make", self, ability_name, trigger)
        target_effect_bonus_stats = []
        if isinstance(trigger, Statblock):
            target_effect_bonus_stats = trigger._effects.get_function_results("ability_check_impose", trigger, ability_name, self)
        else: # TODO: Implement target effects for ability checks from objects
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
            self.get_ability_modifier(ability_name),
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

        self_effect_bonus_stats = self._effects.get_function_results("saving_throw_make", self, ability_name, trigger)
        target_effect_bonus_stats = []
        if isinstance(trigger, Statblock):
            target_effect_bonus_stats = trigger._effects.get_function_results("saving_throw_impose", trigger, ability_name, self)
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

    def skill_check(self, dc, skill_name, trigger = None):
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

        self_effect_bonus_stats = self._effects.get_function_results("skill_check_make", self, skill_name, trigger)
        target_effect_bonus_stats = []
        if isinstance(trigger, Statblock):
            target_effect_bonus_stats = trigger._effects.get_function_results("skill_check_impose", trigger, skill_name, self)
        else: # TODO: Implement target effects for skill checks from objects
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
            self.get_ability_modifier(skill_ability_map[skill_name]) + (self.get_proficiency_bonus() if self.has_proficiency(skill_proficiencies[skill_name]) else 0),
            [EventType.TRIGGER_SKILL_CHECK_ROLL],
            [EventType.TRIGGER_SKILL_CHECK_SUCCEED],
            [EventType.TRIGGER_SKILL_CHECK_FAIL]
        )

    def _determine_d20_roll(self, modifier_table, dc, roll_skill_bonus, roll_events, success_events, fail_events):
        roll_context = RollEventContext(self, modifier_table["advantage"], modifier_table["disadvantage"], modifier_table["auto_succeed"], modifier_table["auto_fail"], modifier_table["bonus"])
        self._controller.trigger_reactions([(event, roll_context) for event in roll_events])
        
        if roll_context.auto_fail or not roll_context.proceed:
            return False

        die_result = DiceRoller.roll_d20(roll_context.advantage, roll_context.disadvantage)
        roll_result = die_result + roll_context.bonus + roll_skill_bonus
        result_context = RollResultEventContext(self, roll_result, roll_result >= dc, die_result == 20)
        
        if not (roll_context.auto_succeed or result_context.success):
            self._controller.trigger_reactions([(fail_event, result_context) for fail_event in fail_events])
        if roll_context.auto_succeed or result_context.success:
            self._controller.trigger_reactions([(success_event, result_context) for success_event in success_events])

            if not result_context.proceed:
                return False

            return True
        return False

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
        effect_roll_modifiers = self._effects.get_function_results("make_attack_roll", self, target)
        modifier_table = {
            "advantage": any(d["advantage"] for d in effect_roll_modifiers),
            "disadvantage": any(d["disadvantage"] for d in effect_roll_modifiers),
            "auto_succeed": any(d["auto_succeed"] for d in effect_roll_modifiers),
            "auto_fail": any(d["auto_fail"] for d in effect_roll_modifiers),
            "bonus": sum(d["bonus"] for d in effect_roll_modifiers)
        }
        
        roll_context = AttackRollEventContext(self, target, modifier_table["advantage"], modifier_table["disadvantage"], modifier_table["auto_succeed"], modifier_table["auto_fail"], modifier_table["bonus"])
        self._controller.trigger_reaction(EventType.TRIGGER_ATTACK_ROLL, roll_context)

        if roll_context.auto_fail or not roll_context.proceed:
            return False
        
        # TODO: Factor in proficiency bonus for equipped weapons
        roll_result = DiceRoller.roll_d20(roll_context.advantage, roll_context.disadvantage)
        result_context = TargetedRollResultEventContext(self, target, roll_result, roll_result == 20 or roll_context.auto_succeed or (roll_result != 1 and roll_result + self.get_ability_modifier(attack_stat) + roll_context.bonus >= target.get_armor_class()), roll_result == 20)
        
        if roll_result == 1 or not (roll_context.auto_succeed or result_context.success):
            self._controller.trigger_reaction(EventType.TRIGGER_ATTACK_ROLL_FAIL, result_context)
        if roll_result == 20 or roll_context.auto_succeed or result_context.success:

            events = [(EventType.TRIGGER_ATTACK_ROLL_SUCCEED, result_context)]
            if roll_result == 20:
                events.append((EventType.TRIGGER_ATTACK_ROLL_CRITICAL, result_context))
            self._controller.trigger_reactions(events)

            if not result_context.proceed:
                return False

            hit_context = TargetedEventContext(target, self)
            target._controller.trigger_reaction(EventType.TRIGGER_HIT_BY_ATTACK, hit_context)

            target.take_damage(damage_string, 2 if roll_result == 20 else 1)

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
            max_set_value = None
            add_value = 0
            multiplier_value = 1
            for effect_bonus_stat in effect_bonus_stats:
                modifier = effect_bonus_stat[speed_type]
                if speed_type == "hover":
                    if modifier is not None:
                        hover_defined = modifier and hover_defined if hover_defined is not None else modifier
                    continue
                if modifier["operation"] == "set":
                    max_set_value = max(max_set_value, modifier["value"]) if max_set_value is not None else modifier["value"]
                elif modifier["operation"] == "add":
                    add_value += modifier["value"]
                elif modifier["operation"] == "multiply":
                    multiplier_value *= modifier["value"]
            if speed_type != "hover":
                if max_set_value is not None:
                    speed_values[speed_type] = max_set_value
                speed_values[speed_type] += add_value
                speed_values[speed_type] *= multiplier_value
        
        return Speed(speed_values["walk"], speed_values["fly"], speed_values["swim"], speed_values["climb"], speed_values["burrow"], hover_defined if hover_defined is not None else self._speed.hover)

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