from enum import Enum
from src.combat.map.map_object import MapObject
from server.backend.database.util.data_storer import DataStorer

class MapTileWall(MapObject):
    class WallDirection(Enum):
        TOP = 1
        LEFT = 2
        BOTTOM = 3
        RIGHT = 4
    
    class WallStats(DataStorer):
        def __init__(self, cover, passable, movement_penalty, climb_dc):
            super().__init__()
            self.cover = cover
            self.passable = passable
            self.movement_penalty = movement_penalty
            self.climb_dc = climb_dc

            self.map_data_property("cover", "cover")
            self.map_data_property("passable", "passable")
            self.map_data_property("movement_penalty", "movement_penalty")
            self.map_data_property("climb_dc", "climb_dc")

    def __init__(self, cover = 0, passable = True, movement_penalty = 0, height = 1, name = "MapTileWall", script = None):
        MapObject.__init__(self, name, script)
        self._wall_stats = []
        for i in range(height):
            self._wall_stats.append(MapTileWall.WallStats(cover, passable, movement_penalty, 25))

        self.map_data_property("_wall_stats", "wall_stats", 
            export_function = lambda v: [{
                "cover": stat.cover,
                "passable": stat.passable,
                "movement_penalty": stat.movement_penalty,
                "climb_dc": stat.climb_dc
            } for stat in v],
            import_function = lambda df, v: [MapTileWall.WallStats(
                cover = stat["cover"],
                passable = stat["passable"],
                movement_penalty = stat["movement_penalty"],
                climb_dc = stat["climb_dc"]
            ) for stat in v]
        )
    
    def export_data(self):
        data = super().export_data()
        del data["name"]
        return data

    @property
    def wall_side(self):
        return self._wall_side.value
    
    @wall_side.setter
    def set_wall_side(self, value):
        if isinstance(value, MapTileWall.WallDirection):
            self._wall_side = value
        elif isinstance(value, int):
            self._wall_side = MapTileWall.WallDirection(value)
        else:
            raise ValueError(f"Invalid type for MapTileWall wall_side: {value}. Must be WallDirection or int.")

    def get_cover(self, height):
        return self._wall_stats[height].cover
    
    def get_passable(self, height):
        return self._wall_stats[height].passable
    
    def get_movement_penalty(self, height):
        return self._wall_stats[height].movement_penalty

    def get_climb_dc(self, height):
        return self._wall_stats[height].climb_dc if not self.get_passable(height) else None

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

    def set_climb_dc(self, dc, height = None):
        if height is None:
            for wall_stat in self._wall_stats:
                wall_stat.climb_dc = dc
        else:
            self._wall_stats[height].climb_dc = dc

    def __getattr__(self, name):
        return super().__getattr__(name)