from src.combat.map.map_tile import MapTile
from src.combat.map.map_tile_wall import MapTileWall

class Map:
    def __init__(self, width: int, height: int, max_height: int = 1):
        self._width = width
        self._height = height
        self._max_height = max_height
        self._height_capped = False
        self._tiles = []

        for y in range(self._height):
            self._tiles.append([])
            for x in range(self._width):
                tile = MapTile(x, y, 0)
                tile._wall_top = self._tiles[y - 1][x]._wall_bottom if y > 0 else MapTileWall()
                tile._wall_left = self._tiles[y][x - 1]._wall_right if x > 0 else MapTileWall()
                tile._wall_bottom = MapTileWall()
                tile._wall_right = MapTileWall()
                self._tiles[y].append(tile)
    
    @property
    def width(self):
        return self._width
    
    @property
    def height(self):
        return self._height
    
    def get_tile(self, x: int, y: int):
        if x < 0 or x >= self._width or y < 0 or y >= self._height:
            return None
        return self._tiles[y][x]

    def get_all_tiles(self):
        return [tile for row in self._tiles for tile in row]

    def get_climb_dc(self, x: int, y: int, height: int):
        tile = self.get_tile(x, y)
        dc_list = []
        if self.get_tile(x - 1, y) and self.get_tile(x - 1, y).height > tile.height and self.get_tile(x - 1, y).height > height:
            dc_list.append(tile._wall_left.climb_dc)
        if self.get_tile(x + 1, y) and self.get_tile(x + 1, y).height > tile.height and self.get_tile(x + 1, y).height > height:
            dc_list.append(tile._wall_right.climb_dc)
        if self.get_tile(x, y - 1) and self.get_tile(x, y - 1).height > tile.height and self.get_tile(x, y - 1).height > height:
            dc_list.append(tile._wall_top.climb_dc)
        if self.get_tile(x, y + 1) and self.get_tile(x, y + 1).height > tile.height and self.get_tile(x, y + 1).height > height:
            dc_list.append(tile._wall_bottom.climb_dc)
        if any([dc is not None for dc in dc_list]):
            return min([dc for dc in dc_list if dc is not None])
        return None