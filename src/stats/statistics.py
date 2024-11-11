import math
from src.combat.map.movement import MovementCost
from src.util.resettable_value import ResettableValue, CappedValue

class AbilityScore:
    def __init__(self, name, value):
        self._name = name
        self._value = value
    
    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

    @property
    def modifier(self):
        return math.floor((self._value - 10) / 2)
    
    def __repr__(self):
        return f"{self._value} {self._name.upper()}"

class Speed:
    def __init__(self, value: int, fly = 0, swim = 0, climb = 0, burrow = 0, hover = False):
        # if (swim is not None and value < swim) or (climb is not None and value < climb) or (burrow is not None and value < burrow):
        #     raise ValueError("Base walking speed cannot be less than swimming, climbing, or burrowing speeds.")
        self._value = ResettableValue(value)
        self._fly = ResettableValue(fly)
        self._hover = hover
        self._swim = ResettableValue(swim)
        self._climb = ResettableValue(climb)
        self._burrow = ResettableValue(burrow)

    def get_attribute_for(self, cost):
        cost_pair_dict = {
            'walking': 'value',
            'flying': 'fly',
            'swimming': 'swim',
            'climbing': 'climb',
            'burrowing': 'burrow'
        }
        return cost_pair_dict[cost]

    @property
    def highest_speed(self):
        return max(self._value.value, self._fly.value, self._swim.value, self._climb.value, self._burrow.value)

    @property
    def distance_moved(self):
        return max(self._value.initial - self._value.value, self._fly.initial - self._fly.value, self._swim.initial - self._swim.value, self._climb.initial - self._climb.value, self._burrow.initial - self._burrow.value)

    @property
    def walk(self):
        return self._value.value

    @property
    def value(self):
        return self._value.value

    @value.setter
    def value(self, new_value):
        self._value.value = new_value

    @property
    def fly(self):
        return self._fly.value

    @fly.setter
    def fly(self, new_value):
        self._fly.value = new_value

    @property
    def swim(self):
        return self._swim.value

    @swim.setter
    def swim(self, new_value):
        self._swim.value = new_value

    @property
    def climb(self):
        return self._climb.value

    @climb.setter
    def climb(self, new_value):
        self._climb.value = new_value

    @property
    def burrow(self):
        return self._burrow.value

    @burrow.setter
    def burrow(self, new_value):
        self._burrow.value = new_value
    
    @property
    def hover(self):
        return self._hover

    def get_min_move_cost(self, movement_cost):
        if not isinstance(movement_cost, MovementCost):
            raise TypeError("movement_cost must be a MovementCost object")
        
        min_cost = None
        for cost_attr in movement_cost.cost_types:
            speed = getattr(self, self.get_attribute_for(cost_attr))
            cost = getattr(movement_cost, cost_attr)

            if cost is not None and speed is not None and cost <= speed:
                if min_cost is None or cost < min_cost:
                    min_cost = cost
        return min_cost
    
    def can_move(self, movement_cost):
        return self.get_min_move_cost(movement_cost) is not None

    def move(self, movement_cost):
        min_cost = self.get_min_move_cost(movement_cost)

        if min_cost is None:
            return False

        self._value.value -= min_cost
        self._fly.value = max(0, self._fly.value - min_cost)
        self._swim.value = max(0, self._swim.value - min_cost)
        self._climb.value = max(0, self._climb.value - min_cost)
        self._burrow.value = max(0, self._burrow.value - min_cost)

        return True

    def reset(self):
        self.value.reset()
        self.fly.reset()
        self.swim.reset()
        self.climb.reset()
        self.burrow.reset()

    def duplicate(self):
        return Speed(self._value.initial, self._fly.initial, self._swim.initial, self._climb.initial, self._burrow.initial, self._hover)

    def __str__(self):
        return str(self._value) + " ft." + ("" if self._fly.initial <= 0 else " (fly " + str(self._fly) + " ft.)") + ("" if self._swim.initial <= 0 else " (swim " + str(self._swim) + " ft.)") + ("" if self._climb.initial <= 0 else " (climb " + str(self._climb) + " ft.)") + ("" if self._burrow.initial <= 0 else " (burrow " + str(self._burrow) + " ft.)") + ("" if not self._hover else " (hover)")
    
    def __repr__(self):
        return str(self)

    def __add__(self, other):
        if isinstance(self, MovementCost):
            summed_speed = Speed(self._value._initial + other._walking, self._fly._initial + other._flying, self._swim._initial + other._swimming, self._climb._initial + other._climbing, self._burrow._initial + other._burrowing, self._hover)
            summed_speed._value._value -= (self._value._initial - self._value._value)
            summed_speed._fly._value -= (self._fly._initial - self._fly._value)
            summed_speed._swim._value -= (self._swim._initial - self._swim._value)
            summed_speed._climb._value -= (self._climb._initial - self._climb._value)
            summed_speed._burrow._value -= (self._burrow._initial - self._burrow._value)
            return summed_speed
        else:
            raise TypeError(f"Unsupported operand type {type(other)}: can only add a MovementCost object to a Speed object")

    def __sub__(self, other):
        if isinstance(other, int):
            return Speed(
                max(0, self.value - other),
                max(0, self.fly - other),
                max(0, self.swim - other),
                max(0, self.climb - other),
                max(0, self.burrow - other)
            )
        else:
            raise TypeError(f"Unsupported operand type {type(other)}: can only subtract an integer from a Speed object")
        
    def __mul__(self, other):
        if isinstance(other, MovementCost):
            mult_speed = Speed(self._value._initial * other._walking, self._fly._initial * other._flying, self._swim._initial * other._swimming, self._climb._initial * other._climbing, self._burrow._initial * other._burrowing, self._hover)
            mult_speed._value._value -= (self._value._initial - self._value._value)
            mult_speed._fly._value -= (self._fly._initial - self._fly._value)
            mult_speed._swim._value -= (self._swim._initial - self._swim._value)
            mult_speed._climb._value -= (self._climb._initial - self._climb._value)
            mult_speed._burrow._value -= (self._burrow._initial - self._burrow._value)
            return mult_speed
        else:
            raise TypeError(f"Unsupported operand type {type(other)}: can only multiply a Speed object by an integer")
    
    def __lt__(self, other):
        if isinstance(other, Speed):
            return self.highest_speed < other.highest_speed