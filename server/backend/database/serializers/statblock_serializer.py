from src.stats.movement.speed import Speed
from src.stats.abilities.ability_index import AbilityIndex
from src.stats.effects.effect_index import EffectIndex
from src.stats.statblock import Statblock

class StatblockSerializer:
    @staticmethod
    def to_data(statblock: Statblock) -> dict:
        data = {
            'name': statblock._name,
            'id': statblock.id,
            'size': statblock._size.size_class,
            'speed': {
                'walk': statblock._speed.walk,
                'fly': statblock._speed.fly,
                'swim': statblock._speed.swim,
                'climb': statblock._speed.climb,
                'burrow': statblock._speed.burrow,
                'hover': statblock._speed.hover
            },
            'hit_points': {
                'max_hp': statblock._hit_points.max_hp,
                'current_hp': statblock._hit_points.hp,
                'temp_hp': statblock._hit_points.temp_hp
            },
            'ability_scores': {
                'strength': statblock._ability_scores.strength.value,
                'dexterity': statblock._ability_scores.dexterity.value,
                'constitution': statblock._ability_scores.constitution.value,
                'intelligence': statblock._ability_scores.intelligence.value,
                'wisdom': statblock._ability_scores.wisdom.value,
                'charisma': statblock._ability_scores.charisma.value
            },
            'level': {class_name: level for class_name, level in statblock._level._levels.items()},
            'abilities': statblock._abilities.to_data(),
            'effects': statblock._effects.to_data(),
            'turn_resources': {
                'action': statblock._turn_resources.use_action,
                'bonus_action': statblock._turn_resources.use_bonus_action,
                'reaction': statblock._turn_resources.use_reaction,
                'free_object_interaction': statblock._turn_resources.use_free_object_interaction
            }
        }
        return data
    
    @staticmethod
    def from_data(data) -> Statblock:
        name = data.get('name')
        sb_id = data.get('id')
        size = data.get('size')
        speed_data = data.get('speed')
        speed = Speed(speed_data['walk'], speed_data['fly'], speed_data['swim'], speed_data['climb'], speed_data['burrow'], speed_data['hover'])
        statblock = Statblock(name, sb_id, size, speed)

        hp_data = data.get('hit_points')
        statblock._hit_points._max_hp = hp_data['max_hp']
        statblock._hit_points._hp = hp_data['current_hp']
        statblock._hit_points._temp_hp = hp_data['temp_hp']

        ability_score_data = data.get('ability_scores')
        statblock._ability_scores.strength.value = ability_score_data['strength']
        statblock._ability_scores.dexterity.value = ability_score_data['dexterity']
        statblock._ability_scores.constitution.value = ability_score_data['constitution']
        statblock._ability_scores.intelligence.value = ability_score_data['intelligence']
        statblock._ability_scores.wisdom.value = ability_score_data['wisdom']
        statblock._ability_scores.charisma.value = ability_score_data['charisma']

        level_data = data.get('level')
        for class_name, level in level_data.items():
            statblock._level.add_level(class_name, level)

        ability_data = data.get('abilities')
        statblock._abilities = AbilityIndex.from_data(ability_data)

        effect_data = data.get('effects')
        statblock._effects = EffectIndex.from_data(effect_data)

        turn_resource_data = data.get('turn_resources')
        statblock._turn_resources.use_action = turn_resource_data['action']
        statblock._turn_resources.use_bonus_action = turn_resource_data['bonus_action']
        statblock._turn_resources.use_reaction = turn_resource_data['reaction']
        statblock._turn_resources.use_free_object_interaction = turn_resource_data['free_object_interaction']

        return statblock