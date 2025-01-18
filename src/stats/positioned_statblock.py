from src.stats.statblock import Statblock
from src.stats.statistics import Speed
from src.combat.map.battlemap import Map
import math

class PositionedStatblock(Statblock):

    def __init__(self, name, speed = Speed(30), size = 5, position = (0, 0), map = None):
        if map is not None and not isinstance(map, Map):
            raise ValueError(f"Invalid map type ({type(map)}): PositionedStatblock map must be a Map object.")
        super().__init__(name, speed, size)
        self._position = position
        self._map = map
    
    @classmethod
    def from_statblock(cls, statblock, position = (0, 0), map = None):
        if not isinstance(statblock, Statblock):
            raise ValueError(f"Invalid statblock type ({type(statblock)}): PositionedStatblock must be created from a Statblock object.")
        if map is not None and not isinstance(map, Map):
            raise ValueError(f"Invalid map type ({type(map)}): PositionedStatblock map must be a Map object.")
        positioned = cls(name=statblock.name)
        positioned.__dict__.update(statblock.__dict__)

        positioned._position = (0, 0)
        positioned._map = map
        return positioned

    def to_statblock(self):
        statblock = Statblock(name=self.name)
        attr_dict = {k:v for k,v in self.__dict__.items() if k not in ['_position', '_map']}
        statblock.__dict__.update(attr_dict)
        return statblock
    
    def get_position(self):
        return self._position
    
    def set_position(self, x, y):
        self._position = (x, y)
    
    def in_melee(self, other):
        dx = abs(self._position[0] - other._position[0])
        dy = abs(self._position[1] - other._position[1])
        return dx <= 1 and dy <= 1

    def distance_to(self, other, y: int = None):
        if isinstance(other, int) and y is not None and isinstance(y, int):
            dx = other - self._position[0]
            dy = y - self._position[1]
            return math.floor(math.sqrt(dx*dx + dy*dy))
        else:
            try:
                other_pos = other.get_position()
                return self.distance_to(other_pos[0], other_pos[1])
            except:
                return -1

    def pull_towards(self, x: int, y: int, distance: int):
        if distance == 0:
            return self._position

        # Calculate direction vector
        dx = x - self._position[0]
        dy = y - self._position[1]
        
        # Calculate magnitude of the direction vector
        magnitude = math.sqrt(dx*dx + dy*dy)
        
        # If already at destination, don't move
        if magnitude == 0:
            return self._position
            
        # Normalize direction vector and multiply by distance
        dx = int(round((dx / magnitude) * distance))
        dy = int(round((dy / magnitude) * distance))
        
        # Calculate and return new position
        new_position = (self._position[0] + dx, self._position[1] + dy)
        self.set_position(new_position[0], new_position[1])
        return new_position

    def push_from(self, x: int, y: int, distance: int):
        return self.pull_towards(x, y, -distance)

