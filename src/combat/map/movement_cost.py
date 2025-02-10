class MovementCost:
    def __init__(self, walk = None, fly = None, swim = None, climb = None, burrow = None):
        self.walk = walk
        self.fly = fly if fly is not None else walk
        self.swim = swim
        self.climb = climb
        self.burrow = burrow