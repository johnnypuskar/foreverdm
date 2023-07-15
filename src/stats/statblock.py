from src.stats.statistics import Stat, Speed, HitPoints, Proficiencies
from src.util.constants import CreatureType, Languages, Size
import math

class Statblock:
    def __init__(self, strength = 10, dexterity = 10, constitution = 10, intelligence = 10, wisdom = 10, charisma = 10, size = Size.MEDIUM, creature_type = CreatureType.HUMANOID,
                proficiency_bonus = 2, proficiencies = Proficiencies(), languages = [Languages.COMMON], senses = [], damage_resistances = [], damage_immunities = [],
                condition_immunities = [], hit_points = 4, max_hit_points = 4, armor_class = 10, speed = Speed(30), features = [], notes = ""):
        self._strength = Stat("strength", strength)
        self._dexterity = Stat("dexterity", dexterity)
        self._constitution = Stat("constitution", constitution)
        self._constitution = Stat("intelligence", intelligence)
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

        self._notes = notes
       
    # Stats
    @property
    def strength(self):
        return self._strength.value

    @property
    def dexterity(self):
        return self._dexterity.value

    @property
    def constitution(self):
        return self._constitution.value

    @property
    def intelligence(self):
        return self._intelligence.value

    @property
    def wisdom(self):
        return self._wisdom.value

    @property
    def charisma(self):
        return self._charisma.value

    # Stat Modifiers
    @property
    def strength_modifier(self):
        return math.floor((self._strength.value - 10) / 2.0)

    @property
    def dexterity_modifier(self):
        return math.floor((self._dexterity.value - 10) / 2.0)

    @property
    def constitution_modifier(self):
        return math.floor((self._constitution.value - 10) / 2.0)

    @property
    def intelligence_modifier(self):
        return math.floor((self._intelligence.value - 10) / 2.0)

    @property
    def wisdom_modifier(self):
        return math.floor((self._wisdom.value - 10) / 2.0) 

    @property
    def charisma_modifier(self):
        return math.floor((self._charisma.value - 10) / 2.0)

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
