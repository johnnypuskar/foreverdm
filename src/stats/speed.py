from src.combat.map.movement_cost import MovementCost

class Speed:
    def __init__(self, walk: int, fly: int = 0, swim: int = 0, climb: int = 0, burrow: int = 0, hover: bool = False):
        self._walk = walk
        self._fly = fly
        self._swim = swim
        self._climb = climb
        self._burrow = burrow
        self._hover = hover

        self.distance_moved = 0
    
    def cost_to_move(self, cost: MovementCost):
        minimum_cost = None
        if cost.walk is not None and self._walk - self.distance_moved >= cost.walk:
            minimum_cost = cost.walk if minimum_cost is None else min(minimum_cost, cost.walk)
        if cost.fly is not None and self._fly - self.distance_moved >= cost.fly:
            minimum_cost = cost.fly if minimum_cost is None else min(minimum_cost, cost.fly)
        if cost.swim is not None and self._swim - self.distance_moved >= cost.swim:
            minimum_cost = cost.swim if minimum_cost is None else min(minimum_cost, cost.swim)
        if cost.climb is not None and self._climb - self.distance_moved >= cost.climb:
            minimum_cost = cost.climb if minimum_cost is None else min(minimum_cost, cost.climb)
        if cost.burrow is not None and self._burrow - self.distance_moved >= cost.burrow:
            minimum_cost = cost.burrow if minimum_cost is None else min(minimum_cost, cost.burrow)
        return minimum_cost

    def move(self, cost: MovementCost):
        minimum_cost = self.cost_to_move(cost)
        if minimum_cost is not None:
            self.distance_moved += minimum_cost
            return True
        return False
    
    def reset(self):
        self.distance_moved = 0
    
    def __eq__(self, other):
        return self._walk == other._walk and \
                self._fly == other._fly and \
                self._swim == other._swim and \
                self._climb == other._climb and \
                self._burrow == other._burrow and \
                self._hover == other._hover