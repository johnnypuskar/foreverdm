class Condition:
    def __init__(self, name, description):
        self._name = name
        self._description = description

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __str__(self):
        return self._name + " [" + self._description + "]"

Condition.BLINDED = Condition("blinded", "auto fail ability checks that rely on sight, disadvantage when making attack rolls, attack rolls against this creature have advantage")
Condition.CHARMED = Condition("charmed", "cannot attack charmer or target charmer with harmful magic or abilities, charmer has advantage on ability checks to interact socially with this creature")
Condition.DEAFENED = Condition("deafened", "can't hear, auto fail ability checks that require hearing")
Condition.FRIGHTENED = Condition("frightened", "disadvantage on ability checks and attack rolls when in line of sight of fear source")
Condition.GRAPPLED = Condition("grappled", "cannot move")
Condition.INVISIBLE = Condition("invisible", "impossible to see without aid of magic or special senses, considered heavily obscured, location can be detected by noises or tracks left behind, advantage when making attack rolls, attack rolls against this creature have disadvantage")
Condition.PARALYZED = Condition("paralyzed", "cannot use any kind of action or reaction, cannot move or speak, auto fail strength and dexterity saving throws, attack rolls against this creature have advantage, attacks that hit the creature are critical hits if attacker is within 5 feet")
Condition.PETRIFIED = Condition("petrified", "transformed into stone along with all nonmagical items creature wears or carries, weight multiplied by 10, cannot use any kind of action or reaction, cannot move or speak, unaware of surroundings, attack rolls against this creature have advantage, auto fail strength and dexterity saving throws, resistance to all damage, immune to new poison and disease, existing poison or disease is suspended not removed, does not age")
Condition.POISONED = Condition("poisoned", "disavantage when making attack rolls and ability checks")
Condition.PRONE = Condition("prone", "can only crawl, disadvantage when making attack rolls, attack rolls against this creature have advantage if the attacker is within 5 feet, otherwise they have disadvantage")
Condition.RESTRAINED = Condition("restrained", "cannot move, disadvantage when making attack rolls, attack rolls against this creature have advantage, disadvantage on dexterity saving throws")
Condition.STUNNED = Condition("stunned", "cannot use any kind of action or reaction, cannot move, can only speak falteringly, auto fail strength and dexterity saving throws, attack rolls against this creature have advantage")
Condition.UNCONSCIOUS = Condition("unconscious", "cannot use any kind of action or reaction, cannot move or speak, unaware of surroundings, drops held items and gains prone condition, auto fail strength and dexterity saving throws, attack rolls against this creature have advantage, attacks that hit the creature are critical hits if attacker is within 5 feet")
Condition.EXHAUSTION = Condition("exhausion", "effects vary on how many counts (levels) of exhausion effect - disadvantage on ability checks (at 1+ level), speed halved (at 2+ levels), disadvantage on attack rolls and saving throws (at 3+ levels), hit point maximum halved (at 4+ levels), cannot move (at 5+ levels), causes instant death (at 6+ levels)")
