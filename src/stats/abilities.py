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
        return str(self._name) + "(" + str(self._charges) + " of " + str(self._max_charges) + " uses left, " + str(self._description)
