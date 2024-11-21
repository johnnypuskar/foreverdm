
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
    TRUE = "true"

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

class Abilities:
    STRENGTH = "str"
    DEXTERITY = "dex"
    CONSTITUTION = "con"
    INTELLIGENCE = "int"
    WISDOM = "wis"
    CHARISMA = "cha"

class Skills:
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
    SLEIGHT_OF_HAND = "sleight_of_hand"
    STEALTH = "stealth"
    SURVIVAL = "survival"

class ScriptData:
    ROLL_RESULT = '''
    function RollResult(modifiers)
        roll_mod = {
            advantage = false,
            disadvantage = false,
            bonus = 0,
            auto_succeed = false,
            auto_fail = false
        }
        for key, value in pairs(modifiers) do
            roll_mod[key] = value
        end
        return roll_mod
    end
    '''

    ADD_VALUE = '''
    function AddValue(value)
        return {operation = "add", value = value}
    end
    '''

    SET_VALUE = '''
    function SetValue(value)
        return {operation = "set", value = value}
    end
    '''

    MULTIPLY_VALUE = '''
    function MultiplyValue(value)
        return {operation = "multiply", value = value}
    end
    '''
    
    USE_TIME = '''
    function UseTime(unit, value)
        value = value or 1
        if unit ~= "action" and unit ~= "bonus_action" and unit ~= "reaction" and unit ~= "minute" and unit ~= "hour" then
            error("Invalid unit for UseTime")
        end
        if (unit == "action" or unit == "bonus_action" or unit == "reaction") and value > 1 then
            error("Action use time cannot require more than 1 action")
        end
        if value <= 0 then
            error("UseTime value must be greater than 0")
        end
        return {unit = unit, value = value}
    end
    '''

    ABILITY_VALIDATE = '''
    function validate(parameter)
        return true, nil
    end
    '''

    DURATION = '''
    function Duration(unit, value)
        value = value or 1
        if unit ~= "round" and unit ~= "minute" and unit ~= "hour" then
            error("Invalid unit for Duration")
        end
        if value <= 0 then
        end
        return {unit = unit, value = value}
    end
    '''

    SPEED = '''
    function SpeedModifier(modifiers)
        speed_mod = {
            walk = {operation = "add", value = 0},
            fly = {operation = "add", value = 0},
            swim = {operation = "add", value = 0},
            climb = {operation = "add", value = 0},
            burrow = {operation = "add", value = 0},
            hover = nil
        }
        for key, value in pairs(modifiers) do
            speed_mod[key] = value
        end
        return speed_mod
    end
    '''

class EventType:
    EFFECT_GRANTED_ABILITY = "effect_granted_ability"
    EFFECT_REMOVED_ABILITY = "effect_removed_ability"
    ABILITY_APPLIED_EFFECT = "ability_applied_effect"
    ABILITY_REMOVED_EFFECT = "ability_removed_effect"
    ABILITY_CONCENTRATION_ENDED = "ability_concentration_ended"


    TRIGGER_ABILITY_CHECK_ROLL = "trigger_roll_ability_check"
    TRIGGER_ABILITY_CHECK_SUCCEED = "trigger_ability_check_succeed"
    TRIGGER_ABILITY_CHECK_FAIL = "trigger_ability_check_fail"

    TRIGGER_SKILL_CHECK_ROLL = "trigger_roll_skill_check"
    TRIGGER_SKILL_CHECK_SUCCEED = "trigger_skill_check_succeed"
    TRIGGER_SKILL_CHECK_FAIL = "trigger_skill_check_fail"

    TRIGGER_SAVING_THROW_ROLL = "trigger_roll_saving_throw"
    TRIGGER_SAVING_THROW_SUCCEED = "trigger_saving_throw_succeed"
    TRIGGER_SAVING_THROW_FAIL = "trigger_saving_throw_fail"
    TRIGGER_CONCENTRATION_SAVING_THROW_ROLL = "trigger_roll_concentration_saving_throw"
    TRIGGER_CONCENTRATION_SAVING_THROW_SUCCEED = "trigger_concentration_saving_throw_succeed"
    TRIGGER_CONCENTRATION_SAVING_THROW_FAIL = "trigger_concentration_saving_throw_fail"

    TRIGGER_ROLL_DAMAGE = "trigger_roll_damage"
    TRIGGER_TAKE_DAMAGE = "trigger_take_damage"
    TRIGGER_HIT_BY_ATTACK = "trigger_hit_by_attack"
    TRIGGER_ZERO_HP = "trigger_zero_hp"
    TRIGGER_DEATH = "trigger_death"

    TRIGGER_ATTACK_ROLL = "trigger_roll_attack"
    TRIGGER_ATTACK_ROLL_MELEE = "trigger_roll_attack_melee"
    TRIGGER_ATTACK_ROLL_RANGED = "trigger_roll_attack_ranged"
    TRIGGER_ATTACK_ROLL_SUCCEED = "trigger_attack_roll_succeed"
    TRIGGER_ATTACK_ROLL_CRITICAL = "trigger_attack_roll_critical"
    TRIGGER_ATTACK_ROLL_FAIL = "trigger_attack_roll_fail"

class AbilityHeaderControlFlag:
    NEW_USE = "new_use_flag",
    CONTINUE = "continue_flag",