from enum import Enum

class MapTileWall:
    class WallDirection(Enum):
        TOP = 1
        LEFT = 2
        BOTTOM = 3
        RIGHT = 4
    
    def __init__(self, solid = False):
        self._solid = solid