from src.stats.elements.numeric_stat import NumericStat

class AbilityScore(NumericStat):
    def __init__(self, name, value):
        super().__init__(name, value)
    
    @property
    def modifier(self):
        return (self.value - 10) // 2

class AbilityScores:
    def __init__(self, strength = 10, dexterity = 10, constitution = 10, intelligence = 10, wisdom = 10, charisma = 10):
        self._strength = AbilityScore("strength", strength)
        self._dexterity = AbilityScore("dexterity", dexterity)
        self._constitution = AbilityScore("constitution", constitution)
        self._intelligence = AbilityScore("intelligence", intelligence)
        self._wisdom = AbilityScore("wisdom", wisdom)
        self._charisma = AbilityScore("charisma", charisma)
    
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
        