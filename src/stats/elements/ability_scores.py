import math

class AbilityScores:
    def __init__(self, str, dex, con, int, wis, cha):
        self.strength = AbilityScore("strength", str)
        self.dexterity = AbilityScore("dexterity", dex)
        self.constitution = AbilityScore("constitution", con)
        self.intelligence = AbilityScore("intelligence", int)
        self.wisdom = AbilityScore("wisdom", wis)
        self.charisma = AbilityScore("charisma", cha)
    
    def get_ability(self, ability_name):
        """
        Returns the AbilityScore property for the given ability.
        Ability is determined by matching the first three letters of the given ability name, case-insensitive.

        param ability_name: str - name of the ability to get the AbilityScore property for

        return: AbilityScore - the AbilityScore property for the given ability
        """
        formatted_ability_name = self.full_ability_name(self.shortened_ability_name(ability_name))
        return getattr(self, formatted_ability_name)

    @staticmethod
    def shortened_ability_name(ability_name):
        """Returns the shortened name of the ability score - i.e. 'Strength' to 'str'"""
        return ability_name[:3].lower()

    @staticmethod
    def full_ability_name(shortened_ability_name):
        """Returns the full name of the ability score in lowercase - i.e. 'str' to 'strength'"""
        ABILITIES = {
            'str': 'strength',
            'dex': 'dexterity',
            'con': 'constitution',
            'int': 'intelligence',
            'wis': 'wisdom',
            'cha': 'charisma'
        }
        return ABILITIES[shortened_ability_name.lower()]

class AbilityScore:
    def __init__(self, name, value):
        self._name = name
        self._value = value
    
    @property
    def name(self):
        """Returns the name of the ability score."""
        return self._name

    @property
    def value(self):
        """Returns the value of the ability score."""
        return self._value

    @value.setter
    def value(self, new_value):
        """Sets the value of the ability score."""
        self._value = new_value

    @property
    def modifier(self):
        """Returns the ability modifier value of the ability score."""
        return math.floor((self._value - 10) / 2)
    
    def __repr__(self):
        """Returns the string representation of the ability score - i.e. '10 STR'"""
        return f"{self._value} {self._name.upper()[:3]}"