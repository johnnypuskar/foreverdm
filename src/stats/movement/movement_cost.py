class MovementCost:
    def __init__(self, walk = None, fly = None, swim = None, climb = None, burrow = None):
        self.walk = walk
        self.fly = fly if fly is not None else walk
        self.swim = swim
        self.climb = climb
        self.burrow = burrow

    def __add__(self, other):
        noneful_add = lambda a, b: b if a is None else a if b is None else a + b
        return MovementCost(
            noneful_add(self.walk, other.walk),
            noneful_add(self.fly, other.fly),
            noneful_add(self.swim, other.swim),
            noneful_add(self.climb, other.climb),
            noneful_add(self.burrow, other.burrow)
        )

    def __hash__(self):
        return hash((self.walk, self.fly, self.swim, self.climb, self.burrow))