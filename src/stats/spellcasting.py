from src.stats.abilities import Ability
from src.util.lua_manager import LuaManager
from src.util.resettable_value import ResettableValue

# Deprecated
class SpellManager():
    def __init__(self, statblock):
        self._statblock = statblock
        self._spell_slots = [ResettableValue(0) for i in range(9)]
        self._spell_sources = {}

    def get_available_spells():
        pass

    def get_spell_slots(self, level):
        return self._spell_slots[level].value
    
    def use_spell_slot(self, level):
        if self._spell_slots[level].value <= 0:
            raise ValueError(f"No level {level} spell slots available.")
        self._spell_slots[level].value -= 1
        return (True, f"Used level {level} spell slot.")

    def reset_spell_slots(self):
        for slot in self._spell_slots:
            slot.reset()

    def add_spell_source(self, name, ability_score, spell_slot_table, caster_weight = 1, prepared = False, level = 1):
        self._spell_sources[name] = SpellcastingAbility(ability_score, self._statblock.proficiency_bonus, spell_slot_table, caster_weight, prepared, level)

    def add_spell(self, index_name, spell):
        if index_name not in self._spell_indices:
            raise ValueError("Spell index does not exist.")

class SpellcastingAbility():
    def __init__(self, ability_score_name, spell_slot_table, caster_weight, prepared):
        self._ability_score_name = ability_score_name
        self._spell_slot_table = spell_slot_table

        # If the caster weight is less than or equal to 0, this spellcasting ability is ignored when Multiclassing is considered.
        # This is useful in cases where a character has some inherent ability or feat that allows them to cast a spell.
        if caster_weight <= 0:
            self._caster_scale = None
        else:
            self._caster_scale = float(1 / caster_weight)
        
        self._spells = SpellIndex(self._ability_score) if not prepared else PreparedSpellIndex(self._ability_score_name)
    
    def spell_save_dc(self, statblock):
        return 8 + statblock.proficiency_bonus + statblock.get_ability_score(self._ability_score_name)
    
    def spell_attack_bonus(self, statblock):
        return statblock.proficiency_bonus + statblock.get_ability_score(self._ability_score_name)

    def cast_spell(self, statblock, spell_name, *args):
        return self._spells.get(spell_name).run(statblock, *args)

class SpellIndex():
    def __init__(self, ability_score):
        self._ability_score = ability_score
        self._spells = {}
    
    def get(self, name):
        return self._spells[name]
    
    def add(self, spell):
        if spell.name in self._spells:
            raise ValueError("Spell already exists in index.")
        self._spells[spell.name] = spell
    
    def remove(self, name):
        if name not in self._spells:
            raise ValueError("Spell does not exist in index.")
        del self._spells[name]

class PreparedSpellIndex(SpellIndex):
    def __init__(self, ability_score):
        super().__init__(ability_score)

class Spell(Ability):
    def __init__(self, name, script, level, school, casting_time, range, components, duration):
        super().__init__(name, script)
        self._level = level
        self._school = school
        self._casting_time = casting_time
        self._range = range
        self._components = components
        self._duration = duration

    @property
    def header(self):
        lua = LuaManager()
        lua.execute(self._script)
        return (f"cast_{self._name}[lvl {self._level}]", lua.get_function_header("run")[1])
    
    def run(self, statblock, *args):
        lua = LuaManager({
            "statblock": statblock,
            "spell_level": self._level,
            "spell_school": self._school,
            "spell_casting_time": self._casting_time,
            "spell_range": self._range,
            "spell_components": self._components,
            "spell_duration": self._duration
        })
        lua.execute(self._script)
        return lua.run("run", *args)
    
    