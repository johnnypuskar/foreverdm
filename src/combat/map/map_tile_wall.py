from enum import Enum
from src.combat.map.map_object import MapObject

class MapTileWall(MapObject):
    class WallDirection(Enum):
        TOP = 1
        LEFT = 2
        BOTTOM = 3
        RIGHT = 4
    
    class WallStats:
        def __init__(self, cover, passable, movement_penalty):
            self.cover = cover
            self.passable = passable
            self.movement_penalty = movement_penalty

    def __init__(self, cover = 0, passable = True, movement_penalty = 0, height = 1, name = "MapTileWall", script = None):
        super().__init__(name, script)
        self._wall_stats = []
        for i in range(height):
            self._wall_stats.append(MapTileWall.WallStats(cover, passable, movement_penalty))

        self._climb_dc = 25
    
    def get_cover(self, height):
        return self._wall_stats[height].cover
    
    def get_passable(self, height):
        return self._wall_stats[height].passable
    
    def get_movement_penalty(self, height):
        return self._wall_stats[height].movement_penalty

    def set_cover(self, cover, height = None):
        if height is None:
            for wall_stat in self._wall_stats:
                wall_stat.cover = cover
        else:
            self._wall_stats[height].cover = cover
    
    def set_passable(self, passable, height = None):
        if height is None:
            for wall_stat in self._wall_stats:
                wall_stat.passable = passable
        else:
            self._wall_stats[height].passable = passable
    
    def set_movement_penalty(self, movement_penalty, height = None):
        if height is None:
            for wall_stat in self._wall_stats:
                wall_stat.movement_penalty = movement_penalty
        else:
            self._wall_stats[height].movement_penalty = movement_penalty

    @property
    def get_climb_dc(self, height):
        return self._climb_dc if not self.get_passable(height) else None

    def __getattribute__(self, name):
        return super().__getattribute__(name)