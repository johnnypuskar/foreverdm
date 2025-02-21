from src.combat.map.map_tile import MapTile
from src.combat.map.map_tile_wall import MapTileWall

class Map:
    TILE_SIZE = 5

    def __init__(self, width: int, height: int, max_height: int = 1):
        self._width = width
        self._height = height
        self._max_height = max_height
        self._height_capped = False
        self._tiles = []

        self._tokens = []
        self._map_props = []

        for y in range(self._height):
            self._tiles.append([])
            for x in range(self._width):
                tile = MapTile(x, y, 0)
                tile._wall_top = self._tiles[y - 1][x]._wall_bottom if y > 0 else MapTileWall(height = max_height)
                tile._wall_left = self._tiles[y][x - 1]._wall_right if x > 0 else MapTileWall(height = max_height)
                tile._wall_bottom = MapTileWall(height = max_height)
                tile._wall_right = MapTileWall(height = max_height)
                self._tiles[y].append(tile)
    
    @property
    def width(self):
        return self._width
    
    @property
    def height(self):
        return self._height
    
    def add_token(self, token):
        self._tokens.append(token)
        token._map = self

    def get_tokens(self, x: int = None, y: int = None):
        if x is None and y is None:
            return self._tokens
        return [token for token in self._tokens if token.get_position()[2:] == (x, y)]
    
    def get_token_spaces(self):
        tokens_and_extensions = []
        for token in self._tokens:
            tokens_and_extensions.append(token)
            for extension in token._extensions.values():
                tokens_and_extensions.append(extension)
        return tokens_and_extensions
        

    def get_map_props(self, x: int = None, y: int = None):
        if x is None and y is None:
            return self._map_props
        return [map_prop for map_prop in self._map_props if map_prop.get_position()[2:] == (x, y)]

    def get_tile(self, x: int, y: int):
        if x < 0 or x >= self._width or y < 0 or y >= self._height:
            return None
        return self._tiles[y][x]

    def get_all_tiles(self):
        return [tile for row in self._tiles for tile in row]

    def get_climb_dc(self, position):
        x, y, height = position
        tile = self.get_tile(x, y)
        dc_list = []
        if self.get_tile(x - 1, y) and self.get_tile(x - 1, y).height > tile.height and self.get_tile(x - 1, y).height > height:
            dc_list.append(tile._wall_left.get_climb_dc(height))
        if self.get_tile(x + 1, y) and self.get_tile(x + 1, y).height > tile.height and self.get_tile(x + 1, y).height > height:
            dc_list.append(tile._wall_right.get_climb_dc(height))
        if self.get_tile(x, y - 1) and self.get_tile(x, y - 1).height > tile.height and self.get_tile(x, y - 1).height > height:
            dc_list.append(tile._wall_top.get_climb_dc(height))
        if self.get_tile(x, y + 1) and self.get_tile(x, y + 1).height > tile.height and self.get_tile(x, y + 1).height > height:
            dc_list.append(tile._wall_bottom.get_climb_dc(height))
        if any([dc is not None for dc in dc_list]):
            return min([dc for dc in dc_list if dc is not None])
        return None