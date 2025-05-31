from src.stats.wrappers.statblock_wrapper import StatblockWrapper
from src.util.dice.dice_roller import DiceRoller
from src.stats.elements.ability_scores import AbilityScores
from src.stats.movement.speed import Speed
from src.stats.size import Size
from src.stats.elements.level import Level
from src.stats.elements.hit_points import HitPoints
from src.stats.abilities.ability_index import AbilityIndex
from src.stats.effects.effect_index import EffectIndex
from src.stats.turn_resources import TurnResources
from src.stats.items.inventory import Inventory
from src.control.controller import Controller
from src.util.modifier_values import ModifierValues, ModifierRolls, ModifierSpeed
from server.backend.database.util.data_storer import DataStorer

class Statblock(DataStorer):
    def __init__(self, name, id, size: int = Size.MEDIUM, speed: Speed = Speed(30), dice_roller = DiceRoller()):
        super().__init__()
        self.id = id

        self._name = name
        self._speed = speed
        self._size = Size(size)

        self._dice_roller = dice_roller
        
        self._hit_points = HitPoints(10)
        self._ability_scores = AbilityScores(10, 10, 10, 10, 10, 10)
        self._level = Level()
        self._abilities = AbilityIndex()
        self._effects = EffectIndex()
        self._turn_resources = TurnResources()
        self._inventory = Inventory(self)

        self.map_data_property("id", "id")
        self.map_data_property("_name", "name")
        self.map_data_property("_speed", "speed")
        self.map_data_property("_size", "size")
        self.map_data_property("_hit_points", "hit_points")
        self.map_data_property("_ability_scores", "ability_scores")
        self.map_data_property("_level", "level")
        self.map_data_property("_abilities", "abilities")
        self.map_data_property("_effects", "effects")
        self.map_data_property("_turn_resources", "turn_resources")
        # self.map_data_property("_inventory", "inventory")

        self._abilities.connect(self._effects)
        self._inventory.connect(self._effects)
        self._effects.connect(self._abilities)

        self._controller: Controller = None

    def get_name(self):
        return self._name

    def get_size(self):
        size_modifiers = ModifierValues(self._effects.get_function_results("modify_size_class", self))
        base_size = self._size.size_class
        base_size = size_modifiers.process_set_max(base_size)
        base_size = size_modifiers.process_add(base_size)
        base_size = max(0, min(5, base_size))
        return Size.from_size_class(base_size)

    def get_speed(self):
        base_speed = self._speed.make_copy()
        speed_modifiers = ModifierSpeed(self._effects.get_function_results("modify_speed", self))

        base_speed._walk = speed_modifiers.process_walk(base_speed.walk)
        base_speed._fly = speed_modifiers.process_fly(base_speed.fly)
        base_speed._swim = speed_modifiers.process_swim(base_speed.swim)
        base_speed._climb = speed_modifiers.process_climb(base_speed.climb)
        base_speed._burrow = speed_modifiers.process_burrow(base_speed.burrow)
        base_speed._hover = speed_modifiers.process_hover(base_speed.hover)

        return base_speed

    def get_initiative_modifier(self):
        initiative_modifiers = ModifierRolls(self._effects.get_function_results("modify_initiative_roll", self))
        return initiative_modifiers

    def get_armor_class(self):
        ac_modifiers = ModifierValues(self._effects.get_function_results("modify_armor_class", self))
        base_ac = 10
        base_ac = ac_modifiers.process_mult(base_ac)
        base_ac = ac_modifiers.process_add(base_ac)
        base_ac = ac_modifiers.process_set_max(base_ac)
        return base_ac
    
    def get_proficiency_bonus(self):
        return 2 + max(0, ((self._level.get_level() - 1) // 4))
    
    def tick(self, rounds = 1):
        for i in range(rounds):
            self._effects.tick_timers(self)
        self._turn_resources.reset()

    def wrap(self, wrapper):
        if isinstance(wrapper, StatblockWrapper):
            return wrapper(self)
        return self