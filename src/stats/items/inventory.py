from src.stats.items.tags import ItemTag
from src.stats.items.equippable_item import EquippableItem
from src.events.observer import Emitter
from src.util.constants import EventType

class Inventory(Emitter):
    def __init__(self, statblock):
        super().__init__()
        self._statblock = statblock
        self._armor = None
        self._main_hand = None
        self._offhand = None
        self._equipped = []
        self._items = []
    
    def has_item(self, item):
        return item in self._items

    def add_item(self, item):
        self._items.append(item)
    
    def remove_item(self, item):
        self._items.remove(item)
        if self._main_hand == item:
            self._main_hand = None
        if self._offhand == item:
            self._offhand = None
        if self._armor == item:
            self._armor = None

    def equip_item(self, item):
        if not self.has_item(item):
            self.add_item(item)
        self._equipped.append(item)
        self.emit(EventType.ITEM_APPLIED_EFFECT, item.name, item.item_effects, self._statblock)
    
    def unequip_item(self, item, statblock):
        if self.has_item(item) and item in self._equipped:
            self._equipped.remove(item)
            self.emit(EventType.ITEM_REMOVED_EFFECT, item.name, item.item_effects, self._statblock)

    @property
    def main_hand(self):
        return self._main_hand
    
    @property
    def offhand(self):
        return self._offhand
    
    @main_hand.setter
    def main_hand(self, item):
        if self._main_hand is not None and isinstance(self._main_hand, EquippableItem):
            self.emit(EventType.ITEM_REMOVED_EFFECT, self._main_hand.name, self._main_hand.item_effects)
        self._main_hand = item
        if item is not None:
            self.emit(EventType.ITEM_APPLIED_EFFECT, item.name, item.item_effects, self._statblock)
            if not self.has_item(item):
                self.add_item(item)
            if item.has_tag(ItemTag.WEAPON_TWO_HANDED):
                self.offhand = None
    
    @offhand.setter
    def offhand(self, item):
        if self._offhand is not None and isinstance(self._offhand, EquippableItem):
            self.emit(EventType.ITEM_REMOVED_EFFECT, self._offhand.name, self._offhand.item_effects, self._statblock)
        if item.has_tag(ItemTag.WEAPON_TWO_HANDED):
            self.main_hand = item
            return
        self._offhand = item
        if item is not None:
            self.emit(EventType.ITEM_APPLIED_EFFECT, item.name, item.item_effects, self._statblock)
            if not self.has_item(item):
                self.add_item(item)
    
    @property
    def armor(self):
        return self._armor
    
    @armor.setter
    def armor(self, item):
        if not item.has_tag(ItemTag.ARMOR):
            return
        if self._armor is not None and isinstance(self._armor, EquippableItem):
            self.emit(EventType.ITEM_REMOVED_EFFECT, self._armor.name, self._armor.item_effects, self._statblock)
        self._armor = item
        if item is not None:
            self.emit(EventType.ITEM_APPLIED_EFFECT, item.name, item.item_effects, self._statblock)
            if not self.has_item(item):
                self.add_item(item)
    
    @property
    def equipped(self):
        return self._equipped
    
    @property
    def items(self):
        return self._items