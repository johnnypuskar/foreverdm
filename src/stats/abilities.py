from src.util.resettable_value import ResettableValue

class Ability:
    def __init__(self, name, description):
        self._name = name
        self._description = description

    def __str__(self):
        return str(self._name) + "(" + str(self._description) + ")"

class UseLimitedAbility(Ability):
    def __init__(self, name, description, charges):
        super.__init__(name, description)
        self._charges = ResettableValue(charges)

    @property
    def charges(self):
        return self._charges.value

    @charges.setter
    def charges(self, new_value):
        self._charges.value = new_value

    def regain(self, additional_charges):
        if self._charges.value + additional_charges > self._charges.initial:
            self._charges.reset()
        else:
            self._charges.value += additional_charges

    def __str__(self):
        return f"{self._name}({self._charges}/{self._charges.initial} uses| {self._description})"

class SpellcastingAbility(Ability):
    def __init__(self, spellcasting_class, spell_attack_bonus, spell_save_dc, focus_items):
        self._spellcasting_class = spellcasting_class
        self._spell_attack_bonus = spell_attack_bonus
        self._spell_save_dc = spell_save_dc
        self._focus_items = focus_items
        super().__init__("Spellcasting", f"Spellcasting for {spellcasting_class}")
    
    def __str__(self):
        return f"{self._spellcasting_class} spellcasting[spell attack bonus({self._spell_attack_bonus}) spell save DC({self._spell_save_dc}) focus items({self._focus_items})]"