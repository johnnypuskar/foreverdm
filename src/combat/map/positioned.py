from src.combat.map.map_tile_wall import MapTileWall
from src.combat.map.map_utils import MapUtils

class Positioned:
    def __init__(self, position3D, map):
        self._position3D = position3D
        self._map = map
    
    def get_position(self):
        return self._position3D
    
    def set_position(self, position3D):
        self._position3D = position3D

    def distance_to(self, other):
        if isinstance(other, Positioned):
            return self.distance_to(other.get_position())
        elif isinstance(other, tuple) and len(other) == 3 and all(isinstance(x, (int, float)) for x in other):
            return int((sum((self._position3D[i] - other[i])**2 for i in range(3)))**0.5) * self._map.TILE_SIZE
        raise TypeError(f"Expected Positioned or position tuple, got {type(other)}")
    
    def pulled_toward(self, other, distance):
        d = self.distance_to(other)
        if d == 0:
            return self._position3D
        dx = other[0] - self._position3D[0]
        dy = other[1] - self._position3D[1]
        dh = other[2] - self._position3D[2]
        target_pos =  (self._position3D[0] + dx * distance / d,
                        self._position3D[1] + dy * distance / d,
                        self._position3D[2] + dh * distance / d)
        
        return self._get_tile_toward(target_pos)
    
    def pushed_away(self, other, distance):
        return self.pushed_toward(other, -distance)
    
    def can_see(self, position):
        return self._get_tile_toward(position) == position
    
    def _get_tile_toward(self, position):
        utils = MapUtils(self._map)
        tiles = utils.get_tiles_in_line(self._position3D, position)

        for i in range(len(tiles)):
            tile = tiles[i]
            if tile[2] < self._map.get_tile(*tile[:2]).height:
                return tiles[max(0, i - 1)]

        return position
