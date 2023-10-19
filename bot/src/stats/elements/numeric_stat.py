
class StatModifier:
    def __init__(self, name, value):
        self._name = name
        self._value = value

    @property
    def name(self):
        return self._name
    
    @property
    def value(self):
        return self._value
    
    def __str__(self):
        return f"{self._name}({'+' if self._value >= 0 else ''}{self._value})"


class NumericStat:
    def __init__(self, name, value):
        self._name = name
        self._base_value = value
        self._modifiers = []
    
    @property
    def name(self):
        return self._name
    
    @property
    def value(self):
        return self._base_value + sum([modifier.value for modifier in self._modifiers])
    
    def add_modifier(self, modifier):
        self._modifiers.append(modifier)

    def remove_modifier(self, name):
        self._modifiers[:] = filter(lambda modifier: modifier.name != name, self._modifiers)
    
    def get_modifiers(self):
        return self._modifiers

    def reset(self):
        self._modifiers.clear()