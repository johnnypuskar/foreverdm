from src.stats.statblock import Statblock
from src.stats.statistics import Speed

class Token:
    def __init__(self, statblock = None, position = (-1, -1)):
        self._statblock = statblock
        self._position = position

        self._can_action = True
        self._can_bonus_action = True
        self._can_free_interaction = True
        self._can_reaction = True
    
    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        if not isinstance(value, tuple) or len(value) != 2 or not all(isinstance(x, int) for x in value):
            raise ValueError("Position must be a tuple of two integers.")
        self._position = value

    @property
    def speed(self):
        return self._statblock.speed

    @speed.setter
    def speed(self, value):
        print(type(Speed(30)))
        if not isinstance(value, Speed):
            raise ValueError(f"Speed must be a Speed object, not {type(value)}.")
        self.__speed = value

    @property
    def size(self):
        return self._statblock.size


class TokenExtension(Token):
    def __init__(self, parent):
        super.__init__()
        self._parent = parent

    @property
    def parent(self):
        return self._parent