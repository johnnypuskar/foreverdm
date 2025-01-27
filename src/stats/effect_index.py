from src.events.observer import Emitter, Observer
from src.stats.conditions import Condition
from src.stats.condition_manager import ConditionManager
from src.stats.effects import Effect, StatblockSubEffectWrapper, SubEffect
from src.util.constants import EventType

class EffectIndex(Observer, Emitter):
    def __init__(self):
        super().__init__()
        self._effects = {}
        self._condition_manager = ConditionManager()
    
    def signal(self, event: str, *data):
        if event == EventType.ABILITY_APPLIED_EFFECT:
            # [data] = [effect_name, script, duration, globals, ability_uuid]
            ability_effect = SubEffect(data[0], data[1], data[3], data[4])
            self.add(ability_effect, data[2])
        elif event == EventType.ABILITY_REMOVED_EFFECT:
            # [data] = [effect_name]
            self.remove(data[0])
        elif event == EventType.ABILITY_CONCENTRATION_ENDED:
            # [data] = [ability_uuid]
            keys = list(self.effect_names)
            for effect_name in keys:
                effect = self._effects[effect_name]
                if isinstance(effect, SubEffect) and effect._ability_uuid == data[0]:
                    self.remove(effect_name)

    @property
    def effect_names(self):
        return self._effects.keys()

    def add(self, effect, duration, statblock = None):
        if isinstance(effect, Effect):
            if effect._name in self._effects:
                raise ValueError(f"Effect {effect._name} already exists in index.")
            effect.duration = duration
            self._effects[effect._name] = effect
            effect.initialize({"statblock": StatblockSubEffectWrapper(statblock, effect)})
            if effect.has_function("get_abilities"):
                for effect_ability in effect.run("get_abilities"):
                    self.emit(EventType.EFFECT_GRANTED_ABILITY, effect_ability, effect._script, "run")
            for condition in effect._conditions:
                derived_condition = self._condition_manager.new_condition(condition, effect._name)
                derived_condition._derived = True
                self.add(derived_condition, -1)
            if effect.has_function("on_apply"):
                effect.run("on_apply")
        elif type(effect) is str:
            self.add(Effect("temp_name", effect), duration)
        
    def remove(self, name):
        if name not in self._effects:
            raise ValueError(f"Effect {name} not found in index.")
        to_remove = [name]
        # Prevent removal if effect is a derived condition
        if isinstance(self._effects[name], Condition):
            if self._effects[name]._derived:
                raise ValueError(f"Effect {name} is derived from effect {name[:name.index('%')]} and cannot be removed directly.")
        else:
            # Determine if any derived conditions also need to be removed
            for _, effect in self._effects.items():
                if isinstance(effect, Condition) and effect._name.startswith(name + "%"):
                    to_remove.append(effect._name)
        # Remove effect, along with any derived conditions
        for remove_name in to_remove:
            removed_effect = self._effects.pop(remove_name)
            removed_effect.initialize()
            if removed_effect.has_function("on_removal"):
                removed_effect.run("on_removal")
            if removed_effect.has_function("get_abilities"):
                for effect_ability in removed_effect.run("get_abilities"):
                    self.emit(EventType.EFFECT_REMOVED_ABILITY, effect_ability)
    
    def get_function_results(self, function_name, statblock, *args):
        results = []
        # Creating a copy list so that mid-execution dictionary editing does not throw an error
        keys = list(self.effect_names)
        for effect_name in keys:
            effect = self._effects[effect_name]
            effect.initialize({"statblock": StatblockSubEffectWrapper(statblock, effect)})
            if effect.has_function(function_name):
                result = effect.run(function_name, *args)
                if result is not None:
                    results.append(result)
        return results

    def tick_timers(self, statblock):
        # Creating a copy list so that mid-execution dictionary editing does not throw an error
        keys = list(self.effect_names)
        for effect_name in keys:
            effect = self._effects[effect_name]
            effect.tick_timer()
            if effect.duration == 0:
                effect.initialize({"statblock": StatblockSubEffectWrapper(statblock, effect)})
                if effect.has_function("on_expire"):
                    effect.run("on_expire")
                self.remove(effect_name)