from src.events.observer import Emitter, Observer
from src.stats.effects.conditions.condition import Condition
from src.stats.effects.conditions.condition_manager import ConditionManager
from src.stats.effects.effect import Effect
from src.stats.effects.sub_effect import SubEffect
from src.stats.wrappers.statblock_effect_wrapper import StatblockEffectWrapper
from src.util.constants import EventType
from server.backend.database.util.data_storer import DataStorer

class EffectIndex(Observer, Emitter, DataStorer):
    def __init__(self):
        Observer.__init__(self)
        Emitter.__init__(self)
        DataStorer.__init__(self)
        
        self._effects = {}
        self._condition_manager = ConditionManager()

        self.map_data_property("_effects", "effects")
    
    def signal(self, event: str, *data):
        if event == EventType.ABILITY_APPLIED_EFFECT:
            # [data] = [effect_name, script, duration, ability_uuid, statblock]
            ability_effect = SubEffect(data[0], data[1], data[3])
            self.add(ability_effect, data[2], data[4])
        elif event == EventType.ABILITY_REMOVED_EFFECT:
            # [data] = [effect_name, statblock]
            self.remove(data[0], data[1])
        elif event == EventType.ABILITY_CONCENTRATION_ENDED:
            # [data] = [ability_uuid, statblock]
            keys = list(self.effect_names)
            for effect_name in keys:
                effect = self._effects[effect_name]
                if isinstance(effect, SubEffect) and effect._ability_uuid == data[0]:
                    self.remove(effect_name, data[1])
        elif event == EventType.ITEM_APPLIED_EFFECT:
            # [data] = [item_name, item_effects, statblock]
            for effect_name, effect_script in data[1].items():
                effect = Effect(f"{data[0]}%{effect_name}", effect_script)
                self.add(effect, -1, data[2])
        elif event == EventType.ITEM_REMOVED_EFFECT:
            # [data] = [item_name, item_effects, statblock]
            for effect_name in data[1].keys():
                self.remove(f"{data[0]}%{effect_name}")

    @property
    def effect_names(self):
        return self._effects.keys()

    def has_effect(self, name):
        return name in self.effect_names

    def add(self, effect, duration, statblock = None):
        if isinstance(effect, Effect):
            if effect._name in self._effects:
                raise ValueError(f"Effect {effect._name} already exists in index.")
            effect.duration = duration
            self._effects[effect._name] = effect
            if effect.has_function("get_abilities"):
                effect.initialize({"statblock": StatblockEffectWrapper(statblock, effect)})
                for effect_ability in effect.run("get_abilities"):
                    self.emit(EventType.EFFECT_GRANTED_ABILITY, effect_ability, effect._script, "run")
            for condition in effect._conditions:
                derived_condition = self._condition_manager.new_condition(condition, effect._name)
                derived_condition._derived = True
                self.add(derived_condition, -1)
            if effect.has_function("on_apply"):
                effect.initialize({"statblock": StatblockEffectWrapper(statblock, effect)})
                effect.run("on_apply")
        elif type(effect) is str:
            self.add(Effect("temp_name", effect), duration)
        
    def remove(self, name, statblock = None):
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
            removed_effect.initialize({"statblock": StatblockEffectWrapper(statblock, removed_effect)})
            if removed_effect.has_function("on_removal"):
                removed_effect.run("on_removal")
            if removed_effect.has_function("get_abilities"):
                for effect_ability in removed_effect.run("get_abilities"):
                    self.emit(EventType.EFFECT_REMOVED_ABILITY, effect_ability)

    def _wrap_args(self, *args):
        args = [arg.wrap(StatblockEffectWrapper) if hasattr(arg, "wrap") else arg for arg in args]
        return args

    def get_function_results(self, function_name, statblock, *args):
        results = []
        # Creating a copy list so that mid-execution dictionary editing does not throw an error
        keys = list(self.effect_names)
        for effect_name in keys:
            effect = self._effects[effect_name]
            if effect.has_function(function_name):
                effect.initialize({"statblock": StatblockEffectWrapper(statblock, effect)})
                result = effect.run(function_name, *self._wrap_args(*args))
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
                if effect.has_function("on_expire"):
                    effect.initialize({"statblock": StatblockEffectWrapper(statblock, effect)})
                    effect.run("on_expire")
                self.remove(effect_name, statblock)