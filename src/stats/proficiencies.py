class Proficiencies:
    # Skills
    ACROBATICS = "acrobatics"
    ANIMAL_HANDLING = "animal_handling"
    ARCANA = "arcana"
    ATHLETICS = "athletics"
    DECEPTION = "deception"
    HISTORY = "history"
    INSIGHT = "insight"
    INTIMIDATION = "intimidation"
    INVESTIGATION = "investigation"
    MEDICINE = "medicine"
    NATURE = "nature"
    PERCEPTION = "perception"
    PERFORMANCE = "performance"
    PERSUASION = "persuasion"
    RELIGION = "religion"
    SLIGHT_OF_HAND = "slight_of_hand"
    STEALTH = "stealth"
    SURVIVAL = "survival"
    
    # Saving Throws
    SAVING_THROW_STRENGTH = "strength_saving_throws"
    SAVING_THROW_DEXTERITY = "dexterity_saving_throws"
    SAVING_THROW_CONSTITUTION = "constitution_saving_throws"
    SAVING_THROW_INTELLIGENCE = "intelligence_saving_throws"
    SAVING_THROW_WISDOM = "wisdom_saving_throws"
    SAVING_THROW_CHARISMA = "charisma_saving_throws"

    # Armor and Weaponry
    LIGHT_ARMOR = "light_armor"
    MEDIUM_ARMOR = "medium_armor"
    HEAVY_ARMOR = "heavy_armor"
    SHIELD = "shields"
    SIMPLE_WEAPONS = "simple_weapons"
    MARTIAL_WEAPONS = "martial_weapons"
    FIREARMS = "firearms"

    # Games
    DICE_GAMES = "dice_gaming_sets"
    CARD_GAMES = "card_gaming_sets"

    # Instruments
    INSTRUMENT_BAGPIPES = "bagpipes"
    INSTRUMENT_DRUM = "drum"
    INSTRUMENT_DULCIMER = "dulcimer"
    INSTRUMENT_FLUTE = "flute"
    INSTRUMENT_LUTE = "lute"
    INSTRUMENT_LYRE = "lyre"
    INSTRUMENT_HORN = "horn"
    INSTRUMENT_PAN_FLUTE = "pan_flute"
    INSTRUMENT_SHAWM = "shawm"
    INSTRUMENT_VIOL = "viol"

    # Tools
    TOOLS_ALCHEMIST = "alchemists_supplies"
    TOOLS_BREWER = "brewers_supplies"
    TOOLS_CALLIGRAPHER = "calligraphers_supplies"
    TOOLS_CARPENTER = "carpenters_tools"
    TOOLS_CARTOGRAPHER = "cartographers_tools"
    TOOLS_COBBLER = "cobblers_tools"
    TOOLS_COOK = "cooks_utensils"
    TOOLS_GLASSBLOWER = "glassblowers_tools"
    TOOLS_JEWELER = "jewelers_tools"
    TOOLS_LEATHERWORKER = "leatherworkers_tools"
    TOOLS_MASON = "masons_tools"
    TOOLS_PAINTER = "painters_supplies"
    TOOLS_POTTER = "potters_tools"
    TOOLS_SMITH = "smiths_tools"
    TOOLS_TINKER = "tinkers_tools"
    TOOLS_WEAVER = "weavers_tools"
    TOOLS_WOODCARVER = "woodcarvers_tools"
    TOOLS_NAVIGATOR = "navigators_tools"
    TOOLS_THIEVES = "thieves_tools"

    # Vehicles
    VEHICLES_LAND = "land_vehicles"
    VEHICLES_SEA = "sea_vehicles"

    # Miscellaneous
    DISGUISE_KIT = "disguise_kit"
    FORGERY_KIT = "forgery_kit"
    HERBALISM_KIT = "herbalism_kit"
    POISONERS_KIT = "poisoners_kit"

class ProficiencyIndex:
    def __init__(self):
        self._proficiencies = set()

    def add(self, proficiency):
        self._proficiencies.add(proficiency)
        return self

    def remove(self, proficiency):
        self._proficiencies.discard(proficiency)
        return self

    def has(self, proficiency):
        return proficiency in self._proficiencies