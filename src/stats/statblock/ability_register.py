
class Ability:
    CATEGORIES = [
        "move",
        "attack_roll",
        "deal_damage",
        "attacked",
        "take_damage",
        "strength_check",
        "dexterity_check",
        "constitution_check",
        "intelligence_check",
        "wisdom_check",
        "charisma_check",
        "strength_save",
        "dexterity_save",
        "constitution_save",
        "intelligence_save",
        "wisdom_save",
        "charisma_save",
        "acrobatics",
        "animal_handling",
        "arcana",
        "athletics",
        "deception",
        "history",
        "insight",
        "intimidation",
        "investigation",
        "medicine",
        "nature",
        "perception",
        "performance",
        "persuasion",
        "religion",
        "slight_of_hand",
        "stealth",
        "survival",
        "equipment",
        "condition",
        "hit_dice",
        "spellcasting",
        "direct_use"
    ]

    def __init__(self, name, description):
        self._name = name
        self._description = description
        self._categories = []
    
    def add_category(self, category):
        if isinstance(category, str):
            self._categories.append(category)
        elif isinstance(category, list) and all(isinstance(x, str) for x in category):
            self._categories.extend(category)
        else:
            raise TypeError("New ability category must be a string or a list of strings")
            
    def remove_category(self, category):
        self._categories[:] = filter(lambda x: x != category, self._categories)

class AbilityCategory:
    def __init__(self):
        self._contents = []
    
    @property
    def contents(self):
        return self._contents

    def add_ability(self, ability):
        self._contents.append(ability)
    
    def remove_ability(self, name):
        self._contents[:] = filter(lambda x: x.name != name, self._contents)

class AbilityRegister:
    def __init__(self):
        self._register = {key: AbilityCategory() for key in Ability.CATEGORIES}

    def add_ability(self, ability, category):
        if category in self._register:
            self._register[category].add_ability(ability)
        else:
            raise KeyError(f"Ability category '{category}' not found")
    
    def remove_ability(self, name):
        for category in self._register.values():
            category.remove_ability(name)

    def __getitem__(self, key):
        return self._register[key].contents
    
    def __iter__(self):
        return iter(self._register)