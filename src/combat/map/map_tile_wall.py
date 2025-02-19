from enum import Enum
from src.combat.map.map_object import MapObject

class MapTileWall(MapObject):
    class WallDirection(Enum):
        TOP = 1
        LEFT = 2
        BOTTOM = 3
        RIGHT = 4
    
    def __init__(self, cover = 0, passable = True, movement_penalty = 0, name = "MapTileWall", script = None):
        super().__init__(name, script)
        self.cover = cover
        self.passable = passable
        self.movement_penalty = movement_penalty
        self._climb_dc = 25
    
    @property
    def climb_dc(self):
        return self._climb_dc if not self.passable else None

    def __getattribute__(self, name):
        return super().__getattribute__(name)