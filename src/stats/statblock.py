from src.util.dice import DiceParser, DiceRoller
from src.stats.abilities import AbilityIndex
from src.stats.effects import EffectIndex
from src.stats.proficiencies import Proficiencies, ProficiencyIndex
from src.stats.resources import ResourceIndex
from src.util.resettable_value import ResettableValue
from src.stats.statistics import AbilityScore, Speed
from src.util.constants import Abilities, Skills

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

        self._concentration = None

        # Equipment
        self._equipped_item = None
        self._offhand_item = None
    

    def get_name(self):
        return self._name

    ## Abilities
    def use_ability(self, ability_name, *args):
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
    
    def take_damage(self, amount, type):
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
            self._hp.value = 0


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

        if modifier_table["auto_fail"]:
            return False
        elif modifier_table["auto_succeed"]:
            return True

        roll_result = DiceRoller.roll_d20(modifier_table["advantage"], modifier_table["disadvantage"]) + self.get_ability_modifier(ability_name) + modifier_table["bonus"]

        return roll_result >= dc

    def saving_throw(self, dc, ability_name, trigger = None):
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

        if modifier_table["auto_fail"]:
            return False
        elif modifier_table["auto_succeed"]:
            return True
        
        roll_result = DiceRoller.roll_d20(modifier_table["advantage"], modifier_table["disadvantage"]) + self.get_ability_modifier(ability_name) + modifier_table["bonus"] + (self.get_proficiency_bonus() if self.has_proficiency(saving_throw_proficiencies[ability_name]) else 0)

        return roll_result >= dc

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

        if modifier_table["auto_fail"]:
            return False
        elif modifier_table["auto_succeed"]:
            return True
        
        roll_result = DiceRoller.roll_d20(modifier_table["advantage"], modifier_table["disadvantage"]) + self.get_ability_modifier(skill_ability_map[skill_name]) + modifier_table["bonus"] + (self.get_proficiency_bonus() if self.has_proficiency(skill_proficiencies[skill_name]) else 0)

        return roll_result >= dc

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
        return self._attack_roll(target, max(effect_bonus_stats, key = lambda x: self.get_ability_modifier(x)), damage_string)
    
    def ranged_attack_roll(self, target, damage_string):
        effect_bonus_stats = ['dex'] + self._effects.get_function_results("get_ranged_attack_stat", self)
        return self._attack_roll(target, max(effect_bonus_stats, key = lambda x: self.get_ability_modifier(x)), damage_string)

    def ability_attack_roll(self, target, ability_name, damage_string):
        return self._attack_roll(target, ability_name, damage_string)

    def _attack_roll(self, target, attack_stat, damage_string):
        effect_roll_modifiers = self._effects.get_function_results("make_attack_roll", self, target)
        modifier_table = {
            "advantage": any(d["advantage"] for d in effect_roll_modifiers),
            "disadvantage": any(d["disadvantage"] for d in effect_roll_modifiers),
            "auto_succeed": any(d["auto_succeed"] for d in effect_roll_modifiers),
            "auto_fail": any(d["auto_fail"] for d in effect_roll_modifiers),
            "bonus": sum(d["bonus"] for d in effect_roll_modifiers)
        }
        
        if modifier_table["auto_fail"]:
            return False
        elif modifier_table["auto_succeed"]:
            return True
        
        # TODO: Factor in proficiency bonus for equipped weapons
        roll_result = DiceRoller.roll_d20(modifier_table["advantage"], modifier_table["disadvantage"])
        if roll_result == 1:
            return False
        
        if roll_result == 20 or modifier_table["auto_succeed"] or roll_result + self.get_ability_modifier(attack_stat) + modifier_table["bonus"] >= target.get_armor_class():
            damage_instances = damage_string.split(",")
            overall_damage_table = {}
            for damage_instance in damage_instances:
                damage_dice, damage_type = damage_instance.strip().split(" ")
                damage_table = DiceParser.parse_string(damage_dice)
                overall_damage_table[damage_type] = damage_table

            die_multiplier = 1
            if roll_result == 20:
                die_multiplier = 2
            
            # TODO: Roll all damage concurrently to allow for reaction abilities to modifier the whole damage roll - queue and execute system?
            for damage_type, damage_dice_table in overall_damage_table.items():
                damage_sum = 0
                for die_type, amount in damage_dice_table.items():
                    if die_type == "MOD":
                        damage_sum += amount
                    else:
                        damage_sum += DiceRoller.roll_custom(die_type, amount * die_multiplier)
                target.take_damage(damage_sum, damage_type)
            return True
    
    ## Speed and Movement
    def get_speed(self, type):
        # TODO: Factor in effects and speed modifiers
        match type:
            case "walk":
                return self._speed.walk
            case "swim":
                return self._speed.swim
            case "climb":
                return self._speed.climb
            case "fly":
                return self._speed.fly
            case "burrow":
                return self._speed.burrow
    
    def add_temporary_speed(self, new_speed):
        self._speed += new_speed

    
