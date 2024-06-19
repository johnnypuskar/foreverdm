from src.stats.statistics import Speed
from src.stats.item import Weapon

class Statblock:
    def __init__(self, name, speed = Speed(30), size = 5):
        self._name = name
        self._speed = speed
        self._size = size

        self._abilities = []

        self._equipped_hand = None
        self._equipped_offhand = None
    
    @property
    def name(self):
        return self._name
    
    @property
    def speed(self):
        return self._speed
    
    @property
    def size(self):
        return self._size
    
    def add_ability(self, ability):
        self._abilities.append(ability)
    
    def remove_ability(self, ability):
        self._abilities.remove(ability)
    
    def equip(self, item):
        if self._equipped_hand is not None:
            self.unequip(self._equipped_hand)
        self._equipped_hand = item
        for ability in item._abilities:
            self.add_ability(ability)
        if item is Weapon and Weapon.PROPERTY_TWO_HANDED in item.properties:
            self.unequip(self._equipped_offhand)
    
    def unequip(self, item):
        if item in (self._equipped_hand, self._equipped_offhand):
            if self._equipped_hand is item:
                self._equipped_hand = None
            if self._equipped_offhand is item:
                self._equipped_offhand = None
            for ability in item._abilities:
                self.remove_ability(ability)