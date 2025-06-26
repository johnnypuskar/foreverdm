import json
from src.stats.statblock import Statblock
from src.combat.map.map_token import Token
from src.combat.map.map_tile import MapTile
from src.combat.map.map_tile_wall import MapTileWall
from server.backend.database.util.data_storer import DataStorer

class Map(DataStorer):
    TILE_SIZE = 5

    def __init__(self, width: int, height: int, max_height: int = 1):
        super().__init__()
        self._width = width
        self._height = height
        self._max_height = max_height
        self._height_capped = False
        self._tiles = []
        self._walls = []

        self._tokens = []
        self._map_props = []

        for y in range(self._height):
            self._tiles.append([])
            for x in range(self._width):
                tile = MapTile(x, y, 0)

                if y > 0:
                    tile._wall_top = self._tiles[y - 1][x]._wall_bottom
                else:
                    tile._wall_top = MapTileWall(height = max_height)
                    self._walls.append(tile._wall_top)
                if x > 0:
                    tile._wall_left = self._tiles[y][x - 1]._wall_right
                else:
                    tile._wall_left = MapTileWall(height = max_height)
                    self._walls.append(tile._wall_left)

                tile._wall_bottom = MapTileWall(height = max_height)
                tile._wall_right = MapTileWall(height = max_height)

                self._tiles[y].append(tile)
        
        def _export_tile_data(v):
            tile_list = []
            for row in v:
                for tile in row:
                    tile_list.append(tile.export_data())
            return tile_list

        def _import_tile_data(df, v):
            tiles = [[None for _ in range(self._width)] for _ in range(self._height)]
            for tile_data in v:
                new_tile = MapTile.new_from_data(tile_data, tile_data["x"], tile_data["y"])
                new_tile._wall_top = MapTileWall.new_from_data(tile_data["wall_top"])
                new_tile._wall_left = MapTileWall.new_from_data(tile_data["wall_left"])
                new_tile._wall_bottom = MapTileWall.new_from_data(tile_data["wall_bottom"])
                new_tile._wall_right = MapTileWall.new_from_data(tile_data["wall_right"])
                tiles[new_tile.y][new_tile.x] = new_tile
            return tiles

        def _import_token_data(df, v):
            tokens = []
            for token_data in v:
                statblock = Statblock(id = token_data["statblock_id"])
                tokens.append(Token(statblock, (token_data["x"], token_data["y"], token_data["height"]), self))
            return tokens

        self.map_data_property("_width", "width")
        self.map_data_property("_height", "height")
        self.map_data_property("_max_height", "max_height")
        self.map_data_property("_tiles", "tiles", export_function = _export_tile_data, import_function = _import_tile_data, import_reliant_properties = ["_width", "_height"])
        # self.map_data_property("_walls", "walls")
        self.map_data_property("_tokens", "tokens",
            export_function = lambda v: [token.export_data() for token in v],
            import_function = _import_token_data
        )
        self.map_data_property("_map_props", "map_props")
    
    @property
    def width(self):
        return self._width
    
    @property
    def height(self):
        return self._height

    def export_view_data(self, statblock_id):
        view_data = {
            "width": self._width,
            "height": self._height,
            "max_height": self._max_height,
            "tiles": [],
            "tokens": []
        }
        
        # TODO: Limit tiles and tokens to the statblock's view range
        for y in range(self._height):
            for x in range(self._width):
                tile = self._tiles[y][x]
                tile_data = {
                    "x": tile.x,
                    "y": tile.y,
                    "height": tile.height,
                    "max_depth": tile._max_depth,
                    "swimmable": tile.swimmable,
                    "terrain_difficulty": tile.terrain_difficulty,
                    "walls": {
                        "top": tile.get_wall(MapTileWall.WallDirection.TOP).export_data(),
                        "left": tile.get_wall(MapTileWall.WallDirection.LEFT).export_data()
                    }
                }
                if x >= self._width - 1:
                    tile_data["walls"]["right"] = tile.get_wall(MapTileWall.WallDirection.RIGHT).export_data()
                if y >= self._height - 1:
                    tile_data["walls"]["bottom"] = tile.get_wall(MapTileWall.WallDirection.BOTTOM).export_data()
                view_data["tiles"].append(tile_data)
        
        for token in self._tokens:
            view_data["tokens"].append({
                "x": token.get_position()[0],
                "y": token.get_position()[1],
                "height": token.get_position()[2],
                "id": token.statblock_id,
                "name": token.get_name(),
                "diameter": token.diameter
            })
        
        return view_data

    def add_token(self, token):
        self._tokens.append(token)
        token._map = self

    def get_tokens(self, x: int = None, y: int = None):
        if x is None and y is None:
            return self._tokens
        return [token for token in self._tokens if token.get_position()[2:] == (x, y)]
    
    def get_token_index(self, statblock_id: str):
        for index, token in enumerate(self._tokens):
            if token.statblock_id == statblock_id:
                return index
        return None

    def get_token_by_id(self, statblock_id: str):
        for token in self._tokens:
            if token.statblock_id == statblock_id:
                return token
        return None

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