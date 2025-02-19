from src.stats.wrappers.statblock_wrapper import StatblockWrapper
from src.stats.ability_scores import AbilityScores
from src.stats.movement.speed import Speed
from src.stats.size import Size
from src.stats.level import Level
from src.stats.hit_points import HitPoints
from src.stats.abilities.ability_index import AbilityIndex
from src.stats.effects.effect_index import EffectIndex
from src.control.controller import Controller
from src.util.modifier_values import ModifierValues, ModifierRolls

class Statblock:
    def __init__(self, name, size: int = Size.MEDIUM, speed: Speed = Speed(30)):
        self._name = name
        self._speed = speed
        
        self._size = Size(size)
        self._hit_points = HitPoints(10)
        self._ability_scores = AbilityScores(10, 10, 10, 10, 10, 10)
        self._level = Level()
        self._abilities = AbilityIndex()
        self._effects = EffectIndex()

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
        return self._speed

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
    
    def wrap(self, wrapper):
        if isinstance(wrapper, StatblockWrapper):
            return wrapper(self)
        return self