from src.combat.map.positioned import Positioned

class PositionHandler:
    def __init__(self, statblock):
        self._statblock = statblock
    
    def distance_to(self, target):
        if not isinstance(self._statblock, Positioned) or not isinstance(target, Positioned):
            return 5
        return self._statblock.distance_to(target)