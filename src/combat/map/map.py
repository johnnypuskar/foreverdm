import math
from src.combat.map.map_tile import MapTile
from src.combat.map.map_tile_wall import MapTileWall

class Map:
    def __init__(self, width: int, height: int):
        self._width = width
        self._height = height
        self._tiles = []

        for y in range(self._height):
            self._tiles.append([])
            for x in range(self._width):
                tile = MapTile(x, y)
                tile.wall_top = self._tiles[y - 1][x].wall_bottom if y > 0 else MapTileWall()
                tile.wall_left = self._tiles[y][x - 1].wall_right if x > 0 else MapTileWall()
                tile.wall_bottom = MapTileWall()
                tile.wall_right = MapTileWall()
                self._tiles[y].append(tile)

    
    @property
    def width(self):
        return self._width
    
    @property
    def height(self):
        return self._height
    
    def get_tile(self, x: int, y: int):
        return self._tiles[y][x]

    def get_all_tiles(self):
        return [tile for row in self._tiles for tile in row]