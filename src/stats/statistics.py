from src.map.movement import MovementCost
from src.util.resettable_value import ResettableValue

class Stat:
    def __init__(self, name, base_value):
        self._name = name
        self._base_value = base_value
        self._modifiers = []

    @property
    def value(self):
        value = self._base_value
        for modifier in self._modifiers:
            value += modifier.value
        return value

    def add_modifier(self, modifier):
        self._modifiers.append(modifier)

    def remove_modifier(self, index):
        self._modifiers.pop(index)

    @property
    def datastring(self):
        datastring = self._name + ": " + str(self.value)
        if len(self._modifiers) > 0:
            datastring += " (" + str(self._base_value) + " (base) with modifiers ["
            for modifier in self._modifiers:
                datastring += str(modifier) + ", "
            datastring = datastring[:-2] + "]"
        return datastring

class StatModifier:
    def __init__(self, value, source):
        self._value = value
        self._source = source

    @property
    def value(self):
        return self._value

    def __str__(self):
        return ("+" if self._value >= 0 else "") + str(self._value) + " (from " + str(self._source) + ")"

class HitPoints:
    def __init__(self, hit_points, maximum, temp = 0):
        self._hit_points = hit_points
        self._maximum = maximum
        self._temp = temp

    def __str__(self):
        return "hit points " + str(self._hit_points) + " of " + str(self._maximum) + ("" if self._temp <= 0 else " and " + str(self._temp) + "temp")

class Speed:
    def __init__(self, value, fly = 0, swim = 0, climb = 0, burrow = 0, hover = False):
        if (swim is not None and value < swim) or (climb is not None and value < climb) or (burrow is not None and value < burrow):
            raise ValueError("Base walking speed cannot be less than swimming, climbing, or burrowing speeds.")
        self._value = ResettableValue(value)
        self._fly = ResettableValue(fly) if fly is not None else None
        self._hover = hover
        self._swim = ResettableValue(swim) if swim is not None else None
        self._climb = ResettableValue(climb) if climb is not None else None
        self._burrow = ResettableValue(burrow) if burrow is not None else None

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
    def value(self):
        return self._value.value

    @value.setter
    def value(self, new_value):
        self._value.value = new_value

    @property
    def fly(self):
        return self._fly.value if self._fly is not None else None

    @fly.setter
    def fly(self, new_value):
        self._fly.value = new_value

    @property
    def swim(self):
        return self._swim.value if self._swim is not None else None

    @swim.setter
    def swim(self, new_value):
        self._swim.value = new_value

    @property
    def climb(self):
        return self._climb.value if self._climb is not None else None

    @climb.setter
    def climb(self, new_value):
        self._climb.value = new_value

    @property
    def burrow(self):
        return self._burrow.value if self._burrow is not None else None

    @burrow.setter
    def burrow(self, new_value):
        self._burrow.value = new_value
    
    @property
    def hover(self):
        return self._hover

    def _get_min_move_cost(self, movement_cost):
        if not isinstance(movement_cost, MovementCost):
            raise TypeError("movement_cost must be a MovementCost object")
        
        min_cost = None
        for cost_attr in movement_cost.cost_types:
            speed = getattr(self, self.get_attribute_for(cost_attr))
            cost = getattr(movement_cost, cost_attr)

            if cost is not None and cost <= speed:
                if min_cost is None or cost < min_cost:
                    min_cost = cost
        return min_cost
    
    def can_move(self, movement_cost):
        return self._get_min_move_cost(movement_cost) is not None

    def move(self, movement_cost):
        min_cost = self._get_min_move_cost(movement_cost)

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
        return Speed(self._value.value, self._fly.value, self._hover, self._swim.value, self._climb.value, self._burrow.value)

    def __str__(self):
        return str(self._value) + " ft." + ("" if self._fly is None else " (fly " + str(self._fly) + " ft.)") + ("" if self._swim is None else " (swim " + str(self._swim) + " ft.)") + ("" if self._climb is None else " (climb " + str(self._climb) + " ft.)") + ("" if self._burrow is None else " (burrow " + str(self._burrow) + " ft.)") + ("" if not self._hover else " (hover)")

    def __add__(self, other):
        if isinstance(other, Speed):
            return Speed(self._value.value + other.value,
                         sum(x for x in [self.fly, other.fly] if x is not None),
                         sum(x for x in [self.swim, other.swim] if x is not None),
                         sum(x for x in [self.climb, other.climb] if x is not None),
                         sum(x for x in [self.burrow, other.burrow] if x is not None),
                         self._hover or other._hover
            )
        else:
            raise TypeError("Unsupported operand type: can only add two Speed objects")

    def __sub__(self, other):
        if isinstance(other, Speed):
            return Speed(
                self._value.value - other.value,
                self.fly - other.fly,
                self.swim - other.swim,
                self.climb - other.climb,
                self.burrow - other.burrow,
            )
        elif isinstance(other, MovementCost):
            return Speed(
                self._value.value - other.walking,
                self.fly - (other.flying if other.flying is not None else 0),
                self.swim - (other.swimming if other.swimming is not None else 0),
                self.climb - (other.climbing if other.climbing is not None else 0),
                self.burrow - (other.burrowing if other.burrowing is not None else 0),
            )

class Proficiencies:
    # Skills
    ACROBATICS = "acrobatics"
    ANIMAL_HANDLING = "animal handling"
    ARCANA = "arcana"
    ATHLETICS = "athletics"
    DECEPTION = "deception"
    HISTORY = "history"
    INSIGHT = "insight"
    INTIMIDATION = "intimidation"
    INVESTIGATION = "investigation"
    MEDICINE = "medicine"
    NATURE = "nature"
    PERCEPTION = "perception"
    PERFORMANCE = "performance"
    RELIGION = "religion"
    SLIGHT_OF_HAND = "slight of hand"
    STEALTH = "stealth"
    SURVIVAL = "survival"
    
    # Saving Throws
    SAVING_THROW_STRENGTH = "strength saving throws"
    SAVING_THROW_DEXTERITY = "dexterity saving throws"
    SAVING_THROW_CONSTITUTION = "constitution saving throws"
    SAVING_THROW_INTELLIGENCE = "intelligence saving throws"
    SAVING_THROW_WISDOM = "wisdom saving throws"
    SAVING_THROW_CHARISMA = "charisma saving throws"

    # Armor and Weaponry
    LIGHT_ARMOR = "light armor"
    MEDIUM_ARMOR = "medium armor"
    HEAVY_ARMOR = "heavy armor"
    SHIELD = "shields"
    SIMPLE_WEAPONS = "simple weapons"
    MARTIAL_WEAPONS = "martial weapons"
    FIREARMS = "firearms"

    # Games
    DICE_GAMES = "dice gaming sets"
    CARD_GAMES = "card gaming sets"

    # Instruments
    INSTRUMENT_BAGPIPES = "bagpipes"
    INSTRUMENT_DRUM = "drum"
    INSTRUMENT_DULCIMER = "dulcimer"
    INSTRUMENT_FLUTE = "flute"
    INSTRUMENT_LUTE = "lute"
    INSTRUMENT_LYRE = "lyre"
    INSTRUMENT_HORN = "horn"
    INSTRUMENT_PAN_FLUTE = "pan flute"
    INSTRUMENT_SHAWM = "shawm"
    INSTRUMENT_VIOL = "viol"

    # Tools
    TOOLS_ALCHEMIST = "alchemists supplies"
    TOOLS_BREWER = "brewers supplies"
    TOOLS_CALLIGRAPHER = "calligraphers supplies"
    TOOLS_CARPENTER = "carpenters tools"
    TOOLS_CARTOGRAPHER = "cartographers tools"
    TOOLS_COBBLER = "cobblers tools"
    TOOLS_COOK = "cooks utensils"
    TOOLS_GLASSBLOWER = "glassblowers tools"
    TOOLS_JEWELER = "jewelers tools"
    TOOLS_LEATHERWORKER = "leatherworkers tools"
    TOOLS_MASON = "masons tools"
    TOOLS_PAINTER = "painters supplies"
    TOOLS_POTTER = "potters tools"
    TOOLS_SMITH = "smiths tools"
    TOOLS_TINKER = "tinkers tools"
    TOOLS_WEAVER = "weavers tools"
    TOOLS_WOODCARVER = "woodcarvers tools"
    TOOLS_NAVIGATOR = "navigators tools"
    TOOLS_THIEVES = "thieves tools"

    # Vehicles
    VEHICLES_LAND = "land vehicles"
    VEHICLES_SEA = "sea vehicles"

    # Miscellanous
    DISGUISE_KIT = "disguise kit"
    FORGERY_KIT = "forgery kit"
    HERBALISM_KIT = "herbalism kit"
    POISONERS_KIT = "poisoners kit"

    def __init__(self):
        self._proficiencies = set()

    def add(self, proficiency):
        self._proficiencies.add(proficiency)
        return self

    def remove(self, proficiency):
        self._proficiencies.discard(proficiency)
        return self

    def has(self, proficiency):
        return proficiency in self._proficiencies

class Sense:
    BLINDSIGHT = "blindsight"
    DARKVISION = "darkvision"
    TREMORSENSE = "tremorsense"
    TRUESIGHT = "truesight"

    def __init__(self, sense, distance):
        self._sense = sense
        self._distance = distance
        
    def __str__(self):
        return str(self._sense) + " " + str(self._distance) + "ft"