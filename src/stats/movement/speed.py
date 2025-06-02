from src.stats.movement.movement_cost import MovementCost
from server.backend.database.util.data_storer import DataStorer

class Speed(DataStorer):
    def __init__(self, walk: int, fly: int = 0, swim: int = 0, climb: int = 0, burrow: int = 0, hover: bool = False):
        super().__init__()
        self._walk = walk
        self._fly = fly
        self._swim = swim
        self._climb = climb
        self._burrow = burrow
        self._hover = hover

        self.distance_moved = 0

        self.map_data_property("_walk", "walk")
        self.map_data_property("_fly", "fly")
        self.map_data_property("_swim", "swim")
        self.map_data_property("_climb", "climb")
        self.map_data_property("_burrow", "burrow")
        self.map_data_property("_hover", "hover")
        self.map_data_property("distance_moved", "distance_moved")
    
    @property
    def walk(self):
        return self._walk
    
    @property
    def fly(self):
        return self._fly
    
    @property
    def swim(self):
        return self._swim
    
    @property
    def climb(self):
        return self._climb
    
    @property
    def burrow(self):
        return self._burrow
    
    @property
    def hover(self):
        return self._hover
    
    def reset(self):
        self.distance_moved = 0
    
    def make_copy(self):
        copy = Speed(self._walk, self._fly, self._swim, self._climb, self._burrow, self._hover)
        copy.distance_moved = self.distance_moved
        return copy

    def __eq__(self, other):
        return self._walk == other._walk and \
                self._fly == other._fly and \
                self._swim == other._swim and \
                self._climb == other._climb and \
                self._burrow == other._burrow and \
                self._hover == other._hover