from src.util.modifier_values import ModifierValues
from src.stats.handlers.skill_handler import SkillHandler

class WorldSenseHandler:
    def __init__(self, statblock):
        self._statblock = statblock
    
    def visibility(self):
        visibility = 2

        # Adds any effect modifiers to the visibility value, and then sets it to any effect minimums as blocking visiblity would override granted visibility.
        modifiers = ModifierValues(self._statblock._effects.get_function_results("modify_visibility", self))
        visibility = modifiers.process_add(visibility)
        visibility = modifiers.process_set_min(visibility)
        
        # Clamp the visibility value to the range [0, 2]
        visibility = max(0, min(2, visibility))

        return visibility

    def sight_to(self, target, perception_value = None):
        if perception_value is None:
            perception_value = SkillHandler(self._statblock).get_passive_skill_score("perception")
        
        noticed = target._effects.get_function_results("is_noticed", target, perception_value)
        can_see = len(noticed) == 0 or any(b for b in noticed)
        if not can_see:
            return 0
        return WorldSenseHandler(target).visibility()
        