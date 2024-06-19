
from src.stats.statistics import Speed
from src.stats.statblock import Statblock

class Character(Statblock):
    def __init__(self, name, speed = Speed(30), size = 5):
        super().__init__(name, speed, size)