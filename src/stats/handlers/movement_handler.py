from src.stats.movement.movement_cost import MovementCost
from src.util.modifier_values import ModifierSpeed

class MovementHandler:
    def __init__(self, statblock):
        self._statblock = statblock

    def modify_speed(self, speed_modifier):
        walk_cost, fly_cost, swim_cost, climb_cost, burrow_cost = None, None, None, None, None
        if "walk" in speed_modifier.keys():
            walk_cost = speed_modifier["walk"]["value"]
            if speed_modifier["walk"]["operation"] == "set":
                walk_cost = self._statblock._speed.walk - walk_cost
            elif speed_modifier["walk"]["operation"] == "multiply":
                walk_cost = self._statblock._speed.walk * (1 - walk_cost)
        if "fly" in speed_modifier.keys():
            fly_cost = speed_modifier["fly"]["value"]
            if speed_modifier["fly"]["operation"] == "set":
                fly_cost = self._statblock._speed.fly - fly_cost
            elif speed_modifier["fly"]["operation"] == "multiply":
                fly_cost = self._statblock._speed.fly * (1 - fly_cost)
        if "swim" in speed_modifier.keys():
            swim_cost = speed_modifier["swim"]["value"]
            if speed_modifier["swim"]["operation"] == "set":
                swim_cost = self._statblock._speed.swim - swim_cost
            elif speed_modifier["swim"]["operation"] == "multiply":
                swim_cost = self._statblock._speed.swim * (1 - swim_cost)
        if "climb" in speed_modifier.keys():
            climb_cost = speed_modifier["climb"]["value"]
            if speed_modifier["climb"]["operation"] == "set":
                climb_cost = self._statblock._speed.climb - climb_cost
            elif speed_modifier["climb"]["operation"] == "multiply":
                climb_cost = self._statblock._speed.climb * (1 - climb_cost)
        if "burrow" in speed_modifier.keys():
            burrow_cost = speed_modifier["burrow"]["value"]
            if speed_modifier["burrow"]["operation"] == "set":
                burrow_cost = self._statblock._speed.burrow - burrow_cost
            elif speed_modifier["burrow"]["operation"] == "multiply":
                burrow_cost = self._statblock._speed.burrow * (1 - burrow_cost)
        
        cost = MovementCost(walk_cost, fly_cost, swim_cost, climb_cost, burrow_cost)
        return self._statblock._speed.move(cost)
        