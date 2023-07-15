from src.stats.statblock import Statblock
from src.stats.statistics import Speed, Proficiencies
from src.util.constants import CreatureType, Languages, Size

class Monster(Statblock):
    def __init__(self, strength = 10, dexterity = 10, constitution = 10, intelligence = 10, wisdom = 10, charisma = 10, size = Size.MEDIUM, creature_type = CreatureType.HUMANOID, 
                 proficiency_bonus = 2, proficiencies = Proficiencies(), languages = [Languages.COMMON], senses = [], damage_resistances = [], damage_immunities = [],
                 condition_immunities = [], hit_points = 4, max_hit_points = 4, armor_class = 10, speed = Speed(30), features = [], actions = [], bonus_actions = [],
                 reactions = [], legendary_action_count = 0, legendary_actions = [], lair_actions = [], xp = 0, challenge = 0, notes = ""):
        super.__init__(strength, dexterity, constitution, intelligence, wisdom, charisma, size, creature_type,proficiency_bonus, proficiencies, languages, senses, damage_resistances,
                       damage_immunities, condition_immunities, hit_points, max_hit_points, armor_class, speed, features, notes)
        self._xp = xp
        self._challenge = challenge

        self._actions = actions
        self._bonus_actions = bonus_actions
        self._reactions = reactions

        self._legendary_actions_total = legendary_action_count
        self._legendary_actions_available = legendary_action_count
        self._legendary_actions = legendary_actions

        self._lair_actions = lair_actions
