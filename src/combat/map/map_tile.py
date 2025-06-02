
from src.util.modifier_values import ModifierSpeed
from src.stats.movement.movement_cost import MovementCost
from src.combat.map.map_tile_wall import MapTileWall
from server.backend.database.util.data_storer import DataStorer

class MapTile(DataStorer):
    def __init__(self, x: int, y: int, height: int = 0):
        super().__init__()
        self._x = x
        self._y = y

        self._height = height
        self._terrain_difficulty = 0

        self._props = []

        # Swimmable defines if the tile shoud use swim speed or walking/burrowing speed for traversal
        self._swimmable = False
        # Max depth defines how deep a creature can either swim or burrow into the tile
        self._max_depth = 0

        self._wall_top = None
        self._wall_left = None
        self._wall_bottom = None
        self._wall_right = None

        self.map_data_property("_x", "x")
        self.map_data_property("_y", "x")
        self.map_data_property("_height", "height")
        self.map_data_property("_terrain_difficulty", "terrain_difficulty")
        self.map_data_property("_swimmable", "swimmable")
        self.map_data_property("_max_depth", "max_depth")
    
    @property
    def x(self):
        return self._x
    
    @property
    def y(self):
        return self._y
    
    @property
    def height(self):
        return self._height

    @property
    def position(self):
        return (self._x, self._y)
    
    @property
    def swimmable(self):
        return self._swimmable

    @property
    def terrain_difficulty(self):
        return self._terrain_difficulty + sum([prop._additional_movement_cost for prop in self._props])

    def get_wall(self, direction):
        if direction == MapTileWall.WallDirection.TOP:
            return self._wall_top
        elif direction == MapTileWall.WallDirection.LEFT:
            return self._wall_top
        elif direction == MapTileWall.WallDirection.BOTTOM:
            return self._wall_top
        elif direction == MapTileWall.WallDirection.RIGHT:
            return self._wall_right
        else:
            raise ValueError(f"Invalid wall direction: {direction}")
    
    def has_wall(self, direction):
        if direction == MapTileWall.WallDirection.TOP:
            return self._wall_top is not None
        elif direction == MapTileWall.WallDirection.LEFT:
            return self._wall_left is not None
        elif direction == MapTileWall.WallDirection.BOTTOM:
            return self._wall_bottom is not None
        elif direction == MapTileWall.WallDirection.RIGHT:
            return self._wall_right is not None
        return False