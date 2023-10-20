
from src.stats.elements.numeric_stat import NumericStat

class ProficiencyRegister:
    def __init__(self, proficiency_bonus):
        self._proficiency_bonus = NumericStat("prof bonus", proficiency_bonus)
        self._proficiencies = set()
    
    def add(self, proficiency):
        self._proficiencies.add(proficiency)
    
    def remove(self, proficiency):
        self._proficiencies.remove(proficiency)

    def __str__(self):
        return "implement this lol"