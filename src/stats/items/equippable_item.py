from src.stats.items.game_item import GameItem

class EquippableItem(GameItem):
    def __init__(self, name, description, weight, size, tags, item_effects = {}):
        super().__init__(name, description, weight, size, tags)
        self._item_effects = item_effects
    
    @property
    def item_effects(self):
        return self._item_effects