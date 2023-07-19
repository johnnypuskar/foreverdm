
class CreatureType:
    ABBERATION = "abberation"
    BEAST = "beast"
    CELESTIAL = "celestial"
    CONSTRUCT = "construct"
    DRAGON = "dragon"
    ELEMENTAL = "elemental"
    FEY = "fey"
    FIEND = "fiend"
    GIANT = "giant"
    HUMANOID = "humanoid"
    MONSTROSITY = "monstrosity"
    OOZE = "ooze"
    PLANT = "plant"
    UNDEAD = "undead"

class DamageType:
    ACID = "acid"
    BLUDGEONING = "bludgeoning"
    COLD = "cold"
    FIRE = "fire"
    FORCE = "force"
    LIGHTNING = "lightning"
    NECROTIC = "necrotic"
    PIERCING = "piercing"
    POISON = "poison"
    PSYCHIC = "psychic"
    RADIANT = "radiant"
    SLASHING = "slashing"
    THUNDER = "thunder"

class Languages:
    COMMON = "common"
    DWARVISH = "dwarvish"
    ELVISH = "elvish"
    GIANT = "giant"
    GNOMISH = "gnomish"
    GOBLIN = "goblin"
    HALFLING = "halfling"
    ORC = "orc"
    ABYSSAL = "abyssal"
    CELESTIAL = "celestial"
    DRACONIC = "draconic"
    DEEP_SPEECH = "deep speech"
    INFERNAL = "infernal"
    PRIMORDIAL = "primordial"
    SYLVAN = "sylvan"
    UNDERCOMMON = "undercommon"

class Size:
    TINY = 2.5
    SMALL = 5
    MEDIUM = 5
    LARGE = 10
    HUGE = 15
    GARGANTUAN = 20

    GRID_SIZE = 5

    @staticmethod
    def next_size(size):
        sizes = [Size.TINY, Size.MEDIUM, Size.LARGE, Size.HUGE, Size.GARGANTUAN]
        return sizes[min(5, sizes.index(size) + 1)]