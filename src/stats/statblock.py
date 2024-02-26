
from src.stats.statistics import Speed


class Statblock:
    def __init__(self, name, description, speed = Speed(30), size = 5):
        self._name = name
        self._description = description
        self._speed = speed
        self._size = size
    
    @property
    def name(self):
        return self._name
    
    @property
    def description(self):
        return self._description
    
    @property
    def speed(self):
        return self._speed
    
    @property
    def size(self):
        return self._size