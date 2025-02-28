from src.stats.items.equippable_item import EquippableItem

class WeaponItem(EquippableItem):
    def __init__(self, name, description, weight, size, tags, melee_damage = "1d4 bludgeoning", ranged_damage = "1d4 bludgeoning", normal_range = 20, long_range = 60, item_effects = {}):
        super().__init__(name, description, weight, size, tags, item_effects)
        self._melee_damage = melee_damage
        self._ranged_damage = ranged_damage
        self._normal_range = normal_range
        self._long_range = long_range
    
    @property
    def melee_damage(self):
        return self._melee_damage
    
    @property
    def ranged_damage(self):
        return self._ranged_damage
    
    @property
    def normal_range(self):
        return self._normal_range
    
    @property
    def long_range(self):
        return self._long_range