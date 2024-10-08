from src.util.dice import DiceSum

class Item:
    def __init__(self, name, abilities = []):
        self._name = name
        self._abilities = abilities

    @property
    def damage_roll():
        return DiceSum(d4=1).roll()

class Weapon(Item):
    PROPERTY_AMMUNITION = "ammunition"
    PROPERTY_FINESSE = "finesse"
    PROPERTY_HEAVY = "heavy"
    PROPERTY_LIGHT = "light"
    PROPERTY_LOADING = "loading"
    PROPERTY_RANGE = "range"
    PROPERTY_REACH = "reach"
    PROPERTY_SPECIAL = "special"
    PROPERTY_THROWN = "thrown"
    PROPERTY_TWO_HANDED = "two_handed"
    PROPERTY_VERSATILE = "versatile"
    
    def __init__(self, name, damage: DiceSum, properties = [], abilities = []):
        super().__init__(name, abilities)
        self._damage = damage
        self._properties = properties
    
    @property
    def damage_roll(self):
        return self._damage.roll()