from src.stats.statistics import Stat, Speed, HitPoints, Proficiencies
from src.util.constants import CreatureType, Languages, Size
from src.stats.profiles import StatProfile, AttackProfile, AttackedProfile, ModifierProfile, MoveProfile, SpellcastProfile
import math

class Statblock:

    def __init__(self, strength = 10, dexterity = 10, constitution = 10, intelligence = 10, wisdom = 10, charisma = 10, size = Size.MEDIUM, creature_type = CreatureType.HUMANOID,
                proficiency_bonus = 2, proficiencies = Proficiencies(), languages = [Languages.COMMON], senses = [], damage_resistances = [], damage_immunities = [],
                condition_immunities = [], hit_points = 4, max_hit_points = 4, armor_class = 10, speed = Speed(30), features = [], notes = ""):
        self._strength = Stat("strength", strength)
        self._dexterity = Stat("dexterity", dexterity)
        self._constitution = Stat("constitution", constitution)
        self._intelligence = Stat("intelligence", intelligence)
        self._wisdom = Stat("wisdom", wisdom)
        self._charisma = Stat("charisma", charisma)

        self._size = size
        self._creature_type = creature_type

        self._proficiencies = proficiencies
        self.proficiency_bonus = proficiency_bonus
        self.languages = languages
        self._senses = senses
        self._features = features

        self._hit_points = HitPoints(hit_points, max_hit_points)
        self._armor_class = armor_class
        self._speed = speed

        self._damage_resistances = damage_resistances
        self._damage_immunities = damage_immunities

        self._conditions = dict()
        self._condition_immunities = condition_immunities

        self._held_items = []

        self._abilities = {
            "attack": [],
            "attacked": [],
            "move": [],
            "strength_check": [],
            "dexterity_check": [],
            "constitution_check": [],
            "intelligence_check": [],
            "wisdom_check": [],
            "charisma_check": [],
            "strength_save": [],
            "dexterity_save": [],
            "constitution_save": [],
            "intelligence_save": [],
            "wisdom_save": [],
            "charisma_save": [],
            "acrobatics": [],
            "animal_handling": [],
            "arcana": [],
            "athletics": [],
            "deception": [],
            "history": [],
            "insight": [],
            "intimidation": [],
            "investigation": [],
            "medicine": [],
            "nature": [],
            "perception": [],
            "performance": [],
            "persuasion": [],
            "religion": [],
            "sleight_of_hand": [],
            "stealth": [],
            "survival": [],
            "equipment": [],
            "initiative": [],
            "spellcast": []
        }

        self.STAT_PROFILES = {
            "attack": self.stat_profile_attack
        }

        self._notes = notes
       
    # Ability Scores
    @property
    def strength(self):
        return self._strength

    @property
    def dexterity(self):
        return self._dexterity

    @property
    def constitution(self):
        return self._constitution

    @property
    def intelligence(self):
        return self._intelligence

    @property
    def wisdom(self):
        return self._wisdom

    @property
    def charisma(self):
        return self._charisma

    # Other Stats

    @property
    def size(self):
        return self._size
    
    @property
    def creature_type(self):
        return self._creature_type
    
    @property
    def armor_class(self):
        return self._armor_class
    
    @property
    def speed(self):
        return self._speed

    # Equipment and Inventory



    # Stat Profiles

    def get_stat_profile(self, profile):
        if profile not in self.STAT_PROFILES:
            raise ValueError(f"Stat profile '{profile}' does not exist.")
        return self.STAT_PROFILES[profile]()

    def stat_profile_attack(self):
        return AttackProfile(self._held_items, self._abilities["attack"])

    # Skills
    def skill_proficiency_bonus(self, proficiency):
        return proficiency if self._proficiencies.has(proficiency) else 0

    @property
    def skill_acrobatics(self):
        return self.dexterity_modifier + self.skill_proficiency_bonus(Proficiencies.ACROBATICS)

    @property
    def skill_animal_handling(self):
        return self.wisdom_modifier + self.skill_proficiency_bonus(Proficiencies.ANIMAL_HANDLING)

    @property
    def skill_arcana(self):
        return self.intelligence_modifier + self.skill_proficiency_bonus(Proficiencies.ARCANA)

    @property
    def skill_athletics(self):
        return self.strength_modifier + self.skill_proficiency_bonus(Proficiencies.ATHLETICS)

    @property
    def skill_deception(self):
        return self.charisma_modifier + self.skill_proficiency_bonus(Proficiencies.DECEPTION)

    @property
    def skill_history(self):
        return self.intelligence_modifier + self.skill_proficiency_bonus(Proficiencies.HISTORY)

    @property
    def skill_insight(self):
        return self.wisdom_modifier + self.skill_proficiency_bonus(Proficiencies.INSIGHT)

    @property
    def skill_intimidation(self):
        return self.charisma_modifier + self.skill_proficiency_bonus(Proficiencies.INTIMIDATION)

    @property
    def skill_investigation(self):
        return self.intelligence_modifier + self.skill_proficiency_bonus(Proficiencies.INVESTIGATION)

    @property
    def skill_medicine(self):
        return self.wisdom_modifier + self.skill_proficiency_bonus(Proficiencies.MEDICINE)

    @property
    def skill_nature(self):
        return self.intelligence_modifier + self.skill_proficiency_bonus(Proficiencies.NATURE)

    @property
    def skill_perception(self):
        return self.wisdom_modifier + self.skill_proficiency_bonus(Proficiencies.PERCEPTION)

    @property
    def passive_perception(self):
        return 10 + self.skill_perception

    @property
    def skill_performance(self):
        return self.charisma_modifier + self.skill_proficiency_bonus(Proficiencies.PERFORMANCE)

    @property
    def skill_persuasion(self):
        return self.charisma_modifier + self.skill_proficiency_bonus(Proficiencies.PERSUASION)

    @property
    def skill_religion(self):
        return self.intelligence_modifier + self.skill_proficiency_bonus(Proficiencies.RELIGION)

    @property
    def skill_slight_of_hand(self):
        return self.dexterity_modifier + self.skill_proficiency_bonus(Proficiencies.SLIGHT_OF_HAND)

    @property
    def skill_stealth(self):
        return self.dexterity_modifier + self.skill_proficiency_bonus(Proficiencies.STEALTH)

    @property
    def skill_survival(self):
        return self.wisdom_modifier + self.skill_proficiency_bonus(Proficiencies.WISDOM)
    
    # Conditions
    @property
    def conditions(self):
        return self._conditions

    @property
    def condition_datastring(self):
        datastring = ""
        for key in self._conditions.keys():
            datastring += str(key) + " from " + str(self._conditions[key]) + ", "
        return "(" + datastring[:-2] + ")" if datastring != "" else "()"

    def apply_condition(self, condition, source):
        if condition in self._conditions:
            self._conditions[condition].append(source)
        else:
            self._conditions[condition] = [source]

    def remove_condition(self, condition, index):
        if condition in self._conditions and index < len(self._conditions[condition]):
            self._conditions[condition].pop(index)
            if not self._conditions[condition]:
                self._conditions.pop(condition)

    def condition_count(self, condition):
        if condition in self._conditions:
            return len(self._conditions[condition])
        return 0
