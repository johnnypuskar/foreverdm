from enum import Enum
from src.combat.map.map_object import MapObject

class MapTileWall(MapObject):
    class WallDirection(Enum):
        TOP = 1
        LEFT = 2
        BOTTOM = 3
        RIGHT = 4
    
    def __init__(self, cover, passable, movement_cost, name = "MapTileWall", script = None):
        super().__init__(name, script)
        self.cover = cover
        self.passable = passable
        self.movement_cost = movement_cost
    
    def __getattribute__(self, name):
        return super().__getattribute__(name)