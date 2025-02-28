from src.stats.handlers.ability_handler import AbilityHandler
from src.stats.handlers.ability_roll_handler import AbilityRollHandler
from src.stats.handlers.ability_score_handler import AbilityScoreHandler
from src.stats.handlers.attack_roll_handler import AttackRollHandler
from src.stats.handlers.effect_handler import EffectHandler
from src.stats.handlers.hit_point_handler import HitPointHandler
from src.stats.handlers.movement_handler import MovementHandler
from src.stats.handlers.skill_handler import SkillHandler
from src.stats.handlers.world_sense_handler import WorldSenseHandler
from src.stats.handlers.inventory_handler import InventoryHandler
from src.stats.handlers.position_handler import PositionHandler

class StatblockWrapper:
    def __init__(self, statblock):
        if isinstance(statblock, StatblockWrapper):
            statblock = statblock._statblock
        self._statblock = statblock

        self._ability_handler = AbilityHandler(self._statblock)
        self._ability_roll_handler = AbilityRollHandler(self._statblock)
        self._ability_score_handler = AbilityScoreHandler(self._statblock)
        self._attack_roll_handler = AttackRollHandler(self._statblock)
        self._effect_handler = EffectHandler(self._statblock)
        self._hit_point_handler = HitPointHandler(self._statblock)
        self._movement_handler = MovementHandler(self._statblock)
        self._skill_handler = SkillHandler(self._statblock)
        self._world_sense_handler = WorldSenseHandler(self._statblock)
        self._inventory_handler = InventoryHandler(self._statblock)
        self._position_handler = PositionHandler(self._statblock)

    # Base Statblock Functions
    def get_name(self):
        return self._statblock.get_name()
    
    def get_hp(self):
        return self._statblock._hit_points.get_hp()
    
    def add_temp_hp(self, temp_hp):
        return self._statblock._hit_points.add_temp_hp(temp_hp)
    
    def reduce_hp(self, amount):
        return self._statblock._hit_points.reduce_hp(amount)

    def get_level(self, class_name = None):
        return self._statblock._level.get_level(class_name)
    
    def add_level(self, class_name, level = 1):
        return self._statblock._level.add_level(class_name, level)
    
    def get_size(self):
        return self._statblock.get_size()
    
    def get_speed(self):
        return self._statblock.get_speed()
    
    def get_armor_class(self):
        return self._statblock.get_armor_class()
    
    def get_proficiency_bonus(self):
        return self._statblock.get_proficiency_bonus()
    
    # Ability Handler
    def add_ability(self, ability):
        return self._ability_handler.add_ability(ability).unpack()
    
    def remove_ability(self, ability_name):
        return self._ability_handler.remove_ability(ability_name).unpack()
    
    def use_ability(self, ability_name, *args):
        return self._ability_handler.use_ability(ability_name, *args).unpack()
    
    # Ability Roll Handler
    def ability_check(self, dc, ability_name, target = None):
        return self._ability_roll_handler.ability_check(dc, ability_name, target).unpack()
    
    def skill_check(self, dc, skill_name, target = None, ability_name: str = None):
        return self._ability_roll_handler.skill_check(dc, skill_name, target, ability_name).unpack()
    
    def saving_throw(self, dc, ability_name, trigger = None):
        return self._ability_roll_handler.saving_throw(dc, ability_name, trigger).unpack()
    
    # Ability Score Handler
    def get_ability_score(self, ability_name):
        return self._ability_score_handler.get_ability_score(ability_name)
    
    def get_ability_modifier(self, ability_name):
        return self._ability_score_handler.get_ability_modifier(ability_name)
    
    # Attack Roll Handler
    def melee_attack_roll(self, target, damage_string):
        return self._attack_roll_handler.melee_attack_roll(target, damage_string).unpack()
    
    def ranged_attack_roll(self, target, damage_string):
        return self._attack_roll_handler.ranged_attack_roll(target, damage_string).unpack()
    
    def ability_attack_roll(self, target, attack_stat, damage_string):
        return self._attack_roll_handler.ability_attack_roll(target, attack_stat, damage_string).unpack()
    
    # Effect Handler
    def add_effect(self, effect, duration):
        return self._effect_handler.add_effect(effect, duration).unpack()
    
    def remove_effect(self, effect_name):
        return self._effect_handler.remove_effect(effect_name).unpack()

    def add_condition(self, condition, duration):
        return self._effect_handler.add_condition(condition, duration).unpack()
    
    def remove_condition(self, condition_name):
        return self._effect_handler.remove_condition(condition_name).unpack()

    # Hit Point Handler
    def get_max_hp(self):
        return self._hit_point_handler.get_max_hp()
    
    def restore_hp(self, amount):
        return self._hit_point_handler.restore_hp(amount).unpack()
    
    def take_damage(self, damage_string):
        return self._hit_point_handler.take_damage(damage_string).unpack()
    
    # Movement Handler
    def modify_speed(self, speed_modifier):
        return self._movement_handler.expend_speed(speed_modifier)
    
    # Skill Handler
    def has_proficiency(self, proficiency_name):
        return self._skill_handler.has_proficiency(proficiency_name)
    
    def get_passive_skill_score(self, skill_name):
        return self._skill_handler.get_passive_skill_score(skill_name)
    
    # World Sense Handler
    def visibility(self):
        return self._world_sense_handler.visibility()
    
    def sight_to(self, target, perception_value = None):
        return self._world_sense_handler.sight_to(target, perception_value)
    
    # Inventory Handler
    def get_equipped_item(self):
        return self._inventory_handler.get_equipped_item()
    
    def get_offhand_item(self):
        return self._inventory_handler.get_offhand_item()

    def drop_equipped_item(self, x = -1, y = -1):
        return self._inventory_handler.drop_equipped_item(x, y)
    
    def drop_offhand_item(self, x = -1, y = -1):
        return self._inventory_handler.drop_offhand_item(x, y)

    # Position Handler
    def distance_to(self, target):
        return self._position_handler.distance_to(target)

    # Misc
    def __eq__(self, value):
        if isinstance(value, StatblockWrapper):
            return self._statblock == value._statblock
        return self._statblock == value