from src.combat.map.positioned import Positioned

class InventoryHandler:
    class ItemData:
        # Data holder class to not pass all item data to script
        def __init__(self, name, weight, tags, melee_damage, ranged_damage):
            self.name = name
            self.weight = weight
            self.tags = tags
            self.melee_damage = melee_damage
            self.ranged_damage = ranged_damage
        
        def has_tag(self, tag):
            return tag in self.tags

    def __init__(self, statblock):
        self._statblock = statblock
    
    def get_equipped_item(self):
        item = self._statblock._inventory.main_hand
        if item is None:
            return None
        return self.ItemData(item._name, item._weight, item._tags, item.melee_damage, item.ranged_damage)

    def get_offhand_item(self):
        item = self._statblock._inventory.offhand
        if item is None:
            return None
        return self.ItemData(item.name, item.weight, item.tags, item.melee_damage, item.ranged_damage)
    
    def drop_equipped_item(self, position = (-1, -1, 0)):
        item = self._statblock._inventory.main_hand
        if item is None:
            return
        self._statblock._inventory.remove_item(item)
        if isinstance(self._statblock, Positioned):
            x, y, _ = position
            self._statblock._map.get_tile(x, y)._props.append(item)
    
    def drop_offhand_item(self, position = (-1, -1, 0)):
        item = self._statblock._inventory.offhand
        if item is None:
            return
        self._statblock._inventory.remove_item(item)
        if isinstance(self._statblock, Positioned):
            x, y, _ = position
            self._statblock._map.get_tile(x, y)._props.append(item)