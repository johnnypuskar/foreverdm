from src.combat.map.map_tile_wall import MapTileWall

class MapTile:
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

        self.wall_top = None
        self.wall_left = None
        self.wall_bottom = None
        self.wall_right = None
    
    @property
    def x(self):
        return self._x
    
    @property
    def y(self):
        return self._y

    @property
    def position(self):
        return (self._x, self._y)

    def get_wall(self, direction):
        if direction == MapTileWall.WallDirection.TOP:
            return self.wall_top
        elif direction == MapTileWall.WallDirection.LEFT:
            return self.wall_left
        elif direction == MapTileWall.WallDirection.BOTTOM:
            return self.wall_bottom
        elif direction == MapTileWall.WallDirection.RIGHT:
            return self.wall_right
        else:
            raise ValueError(f"Invalid wall direction: {direction}")