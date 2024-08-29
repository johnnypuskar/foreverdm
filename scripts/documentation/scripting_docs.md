# Statblock Function Documentation

A Statblock object represents a character and all of their statistics. It also contains many useful functions for performing operations as and involving their character. These are the only functions available on any `statblock`, `target`, or elements of the `targets` list parameter.

Here are all of the readable stat values of the statblock.
- hp : Statblock's current hit points
- temp_hp : Statblock's current temp HP
- level ; Statblock's current level
- base_speed : Statblock's maximum movement speed

Here is a list of all of the functions currently in the Statblock class:
- speed() : Returns their remaining unused movement
- is_proficient(item) : Returns true if character is proficient with an item, false if not
- attack_roll(target) : Returns true if an attack roll against the target hits, false if not
- attack_damage() : Returns the rolled damage for the characters currently held equipped weapon
- take_damage(damage) : Deals specified damage to the characters HP 
- add_temp_movement(bonus_speed) : Adds specified additional speed to the character for this turn
- set_temp_hp(temp_hp): Gives a statblock the specified amount of temp HP points
- distance_to(target) : Returns the distance in feet from the character to the target

# Ability Lua Script Format

An ability is any potential action a character could take, defined by a Lua script. It may use character resources, call functions or change values from a character's statblock, target other creatures or positions on the map, or influence the game state in many other ways. It is defined by a .lua file that implements a `use_cost` global value and `run()` function that returns two values, a boolean determining if the action was a success or not, and a short string detailing the result of the action. Abilities may also define an ability-specific effect.

## Function Definitions and Headers

An ability file will always define one of two functions: `run()` or `modify()`, but the parameters of the function may be one of several possibilities depending on the type of ability. An ability file may never define both functions. Within the both the `run()` and `modify()` functions, a global `statblock` object will be defined that is a reference to the statblock of the character that has used the ability.

### run()

The `run()` function is the most common, and is used for abilities which have an effect on the ability user or another target. In `run()`, the arguments must be defined using these names in order to determine their behavior. Logic must also be implemented in the function to determine if the given input is valid, such as not affecting too many creatures over a max limit or targeting a point that the character can see.

#### `run()`
- This definition of run is used when the only statblock or creature affected or involved is the character using the ability, and no other characters need to be referenced.

#### `run(target)`
- This definition of run is used when the ability affects or references one single other object or creature, such as a direct attack or heal. The `target` parameter is a statblock object of the target creature or object.

#### `run(targets)`
- This definition of run is used when a list of one or more targets is affected or referenced by the ability. The `targets` parameter is a list of statblocks of the targeted creatures or objects.

#### `run(position)`
- This definition of run is used when a point in space is the specified target of the ability, rather than a creature. The `position` parameter is an `(x, y)` tuple representing the map coordinates of the target position.

### modify()

The `modify()` function is used in special cases when an ability does not affect the user or some target, but changes how a different ability would act. In practice, this is done by running the code contained in `modify()` before the code in the subsequent abilitiu's `run()` function, to apply changes or temporary effects before it is used.

#### modify(...)
- The modify function can be defined with any number of arguments, or none at all if they are not required. Functions names should be self-explanatory, and use lowercase snake case for name formatting (ex. `spell_level` or `charges_used`).
**Returns:** Boolean
- The modify function returns true in the case that the ability was subsequently modified (i.e. any checks on if the ability was allowed to run passed, and the modification code was run to change the ability for this usage). Otherwise, it returns false to indicate failure, and the subsequent ability in the chain is not run.

## Global Variables

Abilities may sometimes define global variable values at the top level which will be used in the function. This is only used in cases where an ability is part of some larger system, such as a spell being within the spellcasting system. Unless otherwise specified, values should not be defined as globals.

### UseTime Helper Function and Global Variable

Abilities will often have a time cost to use them, primarily being actions, bonus actions, and reactions. To specify this, an ability script file will always define a global `use_time` value at the top level. Some abilities, such as Action Surge or Flexible Casting, do not have a use time - as their use time is either from having limited uses per rest, or from some other resource. In cases like these, where the ability does not cost any actions to use, `use_time` is set to nil. Abilities such as certain spells may also take more than an action to use, taking one or more full minutes. This value is also defined using the UseTime helper function:

While use time is defined in the ability script, it is assumed that the prerequisite time has been met when the ability function is run, so no checks ever need to be made against the `use_cost`.

#### `UseTime(unit, value = 1)`
Defines the action cost required to use the defined ability.
**Parameters:**
- `unit`: the cost or duration to use the ability, valid strings are `action`, `bonus_action`, `reaction`, `minute`, `hour`
- `value`: (optional) the integer value of how many of the units it takes to use the ability, defaults to 1, values greater than 1 are only applicable for use costs of multiple minutes or hours

#### UseTime Examples
```
-- Use time for an ability which uses an action
use_time = UseTime("action")

-- Use time for an ability which uses an action
use_time = UseTime("bonus_action")

-- Use time for an ability which uses a reaction
use_time = UseTime("reaction")

-- Use time for an ability which takes 10 minutes to use
use_time = UseTime("minute", 10)
```

### GameTime Helper Function

Some global variables must be defined with certain syntax in order to be evaluated correctly. In the case of defining an amount of time it takes to use an ability, as when casting a spell, or the duration of some ability or effect, the GameTime helper function is used to define the use time for that ability.

#### `GameTime(value, units)`
Creates the time value specified, in the amount of units specified.
**Parameters:**
- `value`: the integer value of how much time is being defined
- `units`: the unit of time, valid units are `round`, `minute` or `hour`

#### GameTime Examples
```
-- Defines a period of time which lasts for 3 rounds of combat.
GameTime(3, "round")

-- Defines a period of time which lasts for 10 minutes.
GameTime(10, "minute")

-- Defines a period of time which lasts for 12 hours.
GameTime(12, "hour")
```

### Spell Definitions

In the case of spells, there are 6 additional global values that must be defined in every spell ability script. The values are `spell_level`, `spell_school`, `spell_range`, `spell_components`, `spell_duration`, `spell_concentration`. A spell ability must also define `use_cost` like any other ability. Their values can be determined from the spell description, and must follow the syntax as defined below.

#### `spell_level`
- `spell_level` is defined with an integer value from 0 to 9 specifying the level of the spell. A level 0 spell represents a cantrip.

#### `spell_school`
- `spell_school` is defined with a string matching one of the following legal values: `abjuration`, `conjuration`, `divination`, `enchantment`, `evocation`, `illusion`, `necromancy`, `transmutation`

#### `use_cost`
- `use_cost` is defined with the UseCost() helper function by the casting time of the spell.

#### `spell_range`
- `spell_range` is defined with an integer value as low as zero specifying the range of the spell in feet. A value of 0 is used in the case of a spell with range 'Self', and a value of 1 is used in the case of a spell with range 'Touch'. Perform unit conversion if required.

#### `spell_components`
- `spell_components` is defined with a table that has 1 to 3 entries. The value entry keys for the table are 'V', 'S', and 'M' representing verbal, somatic, and material components. The values of these entries, in the case of 'V' and 'S', will be `true` boolean values in cases where a spell requires these component types. For entries with the 'M' key, the value will be a list of strings, defining each material object as it is said in the spell description. In cases of spells without verbal, somatic, and/or components, `spell_components` should not define the non-required entries in the table at all.

#### `spell_duration`
- `spell_duration` is defined with the GameTime() helper function. A value of nil is used in the case of a spell with duration 'Instantaneous'.

#### `spell_concentration`
- `spell_concentration` is defined with a boolean value indicating whether the spell requires concentration or not.

# Effect Lua Script Format

An effect is any status that alters how a character acts or behaves, by changing the properties of rolls or the characters statistics. It is defined by a .lua file that implements one or more of the following functions, returning a value that alters the corresponding function on the character statblock. Effects act as a form of Decorator pattern.

A effect .lua file will contain function definitions and implementations that handle how that effect should affect those function calls. Effects will only ever implement the functions listed in this documentation.

In cases where a function runs, but is determined to have no effect - such as an effect which only activates under certain conditions - returning `nil` is the correct behavior to speficy that no modifications should be made for that case. Otherwise, functions must always return the correct type of value specified in the function documentation definition.

## RollModifier Helper Function

Many effect functions return a table of values representing modifiers the specified die roll will recieve, such as advantage or disadvantage, adding or subtracting a bonus from the result, or automatically succeeding or failing. This table is constructed using a system-defined helper function `RollModifier(modifiers)`, which takes in a table of modifiers to add to the roll and returns the full table.

### `RollModifier(modifiers)`
Creates and returns the table to designate the proper modifiers of a die roll from the specified parameter table
**Parameters:**
- `modifiers`: A table with one or more of the following values set, undefined values will not be affected.
  - `advantage`: Boolean
    - `true` indicates advantage on the roll
  - `disadvantage`: Boolean
    - `true` indicates disadvantage on the roll
  - `bonus`: Number
    - The numeric bonus to be added to the roll, negative for subtracting
  - `auto_succeed`: Boolean
    - `true` if the roll auto-succeeds regardless of die result
  - `auto_fail`: Boolean
    - `true` if the roll auto-fails regardless of die result

#### RollModifier Examples

```
-- Return a Roll table which gives the roll advantage and adds 2 to the result
return RollModifier({"advantage": true, "bonus": 2})

-- Return a Roll table which automatically fails
return RollModifier({"auto_succeed": true})

-- Return a default Roll table which doesn't affect the roll
return RollModifier({})
```

## AddValue and SetValue Helper Functions

Some effect functions return an operative modifier to a numerical stat, to either add some value to the stat or to set it to some value. This is represented using a table constructed with either the `AddValue(value)` or `SetValue(value)` system-defined helper functuions, which take in the numerical integer value to either set or add to the statistic.

### `AddValue(value)`
Creates and returns the table to define an add operation of some value
**Parameters:**
- `value`: The integer value to be added to the statistic in question

### `SetValue(value)`
Creates and returns the table to define an set operation of some value
**Parameters:**
- `value`: The integer value to set the statistic in question to

#### AddValue and SetValue Examples

```
-- Return an Add operator table to add 5 to the statistic
return AddValue(5)

-- Return an Add operator table to subtract 3 from the statistic
return AddValue(-3)

-- Return a Set operator table to set the statistic value to 19
return SetValue(19)
```

## Global Parameters

Abilities may define global 

## Function Headers

### `start_turn()`
Used right at the beginning of a character with the effect's turn. Defines logic or effects that happens at the start of their turn.
**Returns:**
- `nil`: No return value

### `end_turn()`
Used right after the end of a charater with the effect's turn. Defines logic or effects that happens at the end of their turn.
**Returns:**
- `nil`: No return value

### `make_attack_roll(target)`
Used when the character with the effect makes an attack roll against a target
**Parameters:**
- `target`: The Statblock of the target of the attack
**Returns:**
- **RollResult**: Roll table created using the `RollResult()` helper function

### `recieve_attack_roll(attacker)`
Used when the character with the effect is targeted by an attacker, before the attack is determined to hit or not
**Parameters:**
- `attacker`: The Statblock of the attacker
**Returns:**
- **RollResult**: Roll table created using the `RollResult()` helper function

### `get_melee_attack_stat()`
Used when the character with the effect references the statistic with which to make a melee attack roll with
**Returns:**
- `list[string]`: A list of zero to five statistic names which could be potentially used to make a melee attack roll, valid statistics are `dex`, `con`, `int`, `wis`, `cha` (note: `str` is ignored as it is the default and always possible)

### `get_ranged_attack_stat()`
Used when the character with the effect references the statistic with which to make a ranged attack roll with
**Returns:**
- `list[string]`: A list of zero to five statistic names which could be potentially used to make a ranged attack roll, valid statistics are `str`, `con`, `int`, `wis`, `cha` (note: `dex` is ignored as it is the default and always possible)

### `damaged(amount, type, attacker)`
Used when the character with the effect takes any damage, whether from an attacker statblock or not.
**Parameters:**
- `amount`: The numerical value of the damage taken
- `type` : The type of damage taken, valid types are `acid`, `bludgeoning`, `cold`, `fire`, `force`, `lightning`, `necrotic`, `piercing`, `poison`, `psychic`, `radiant`, `slashing`, `thunder`
- `target` : If applicable, the Statblock of the creature who dealt the damage, defaults to nil for no attacker
**Returns:**
- `nil`: No return value

### `get_resistances()`
Used when the character with the effect references their damage resistances.
**Returns:**
- `list[string]`: A list of any additional damage types this effect grants resistance to, valid types are `acid`, `bludgeoning`, `cold`, `fire`, `force`, `lightning`, `necrotic`, `piercing`, `poison`, `psychic`, `radiant`, `slashing`, `thunder`

### `get_proficiencies()`
Used when the character with the effect references their skill, saving throw, tool, weapon, or armor proficiencies.
**Returns:**
- `list[string]`: A list of zero, one or more additional proficiencies this effect grants, valid proficiency names are: `acrobatics`, `animal_handling`, `arcana`, `athletics`, `deception`, `history`, `insight`, `intimidation`, `investigation`, `medicine`, `nature`, `perception`, `performance`, `religion`, `slight_of_hand`, `stealth`, `survival`, `strength_saving_throws`, `dexterity_saving_throws`, `constitution_saving_throws`, `intelligence_saving_throws`, `wisdom_saving_throws`, `charisma_saving_throws`, `light_armor`, `medium_armor`, `heavy_armor`, `shields`, `simple_weapons`, `martial_weapons`, `firearms`, `dice_gaming_sets`, `card_gaming_sets`, `bagpipes`, `drum`, `dulcimer`, `flute`, `lute`, `lyre`, `horn`, `pan_flute`, `shawm`, `viol`, `alchemists_supplies`, `brewers_supplies`, `calligraphers_supplies`, `carpenters_tools`, `cartographers_tools`, `cobblers_tools`, `cooks_utensils`, `glassblowers_tools`, `jewelers_tools`, `leatherworkers_tools`, `masons_tools`, `painters_supplies`, `potters_tools`, `smiths_tools`, `tinkers_tools`, `weavers_tools`, `woodcarvers_tools`, `navigators_tools`, `thieves_tools`, `land_vehicles`, `sea_vehicles`, `disguise_kit`, `forgery_kit`, `herbalism_kit`, `poisoners_kit`

### `saving_throw_make(type, target)`
Used when the character with the effect forces a target to make a saving throw
**Parameters:**
- `type`: The 3 letter key for the saving throw ability, valid keys are `str`, `dex`, `con`, `int`, `wis`, `cha`
- `target`: The Statblock of the target making the saving throw
**Returns:**
- **RollResult**: Roll table created using the `RollResult()` helper function

### `saving_throw_impose(type, trigger)`
Used when the character with the effect is forced to make a saving throw by a triggering creature
**Parameters:**
- `type`: The 3 letter key for the saving throw ability, valid keys are `str`, `dex`, `con`, `int`, `wis`, `cha`
- `trigger`: The Statblock of the triggering creature or object forcing the character with the effect to make the saving throw
**Returns:**
- **RollResult**: Roll table created using the `RollResult()` helper function

### `ability_check_make(type, target)`
Used when the character with the effect makes an ability check
**Parameters:**
- `type`: The 3 letter key for the ability check ability, valid keys are `str`, `dex`, `con`, `int`, `wis`, `cha`
- `target`: The Statblock of the target making the saving throw, may be nil in cases with no target creature
**Returns:**
- **RollResult**: Roll table created using the `RollResult()` helper function

### `ability_check_impose(type, trigger)`
Used when a triggering creature makes an ability check against the creature with the effect
**Parameters:**
- `type`: The 3 letter key for the saving throw ability, valid keys are `str`, `dex`, `con`, `int`, `wis`, `cha`
- `trigger`: The Statblock of the triggering creature making the ability check against the character with the effect 
**Returns:**
- **RollResult**: Roll table created using the `RollResult()` helper function

### `skill_check_make(skill, target)`
Used when the character with the effect makes an skill check
**Parameters:**
- `skill`: The skill for the check, valid skills are `acrobatics`, `animal_handling`, `arcana`, `athletics`, `deception`, `history`, `insight`, `intimidation`, `investigation`, `medicine`, `nature`, `perception`, `performance`, `persuasion`, `religion`, `sleight_of_hand`, `stealth`, `survival`
- `target`: The Statblock of the target of the skill check, may be nil in cases with no target creature
**Returns:**
- **RollResult**: Roll table created using the `RollResult()` helper function

### `skill_check_impose(type, trigger)`
Used when a triggering creature makes an skill check against the creature with the effect
**Parameters:**
- `skill`: The skill for the check, valid skills are `acrobatics`, `animal_handling`, `arcana`, `athletics`, `deception`, `history`, `insight`, `intimidation`, `investigation`, `medicine`, `nature`, `perception`, `performance`, `persuasion`, `religion`, `sleight_of_hand`, `stealth`, `survival`
- `trigger`: The Statblock of the triggering creature making the skill check against the character with the effect 
**Returns:**
- **RollResult**: Roll table created using the `RollResult()` helper function

### `modify_stat(stat)`
Used to change the numerical value of a given stat on the character with the effect's statsheet
**Parameters:**
- `stat`: The stat to be modified, valid stats are `str`, `dex`, `con`, `int`, `wis`, `cha`, `max_hp`, `speed_walk`, `speed_fly`, `speed_swim`, `speed_burrow`, `speed_climb`, `armor_class`
**Returns:**
- **AddValue** or **SetValue**: Add or Set table created using `AddValue()` or `SetValue()` helper function

### `modify_armor_class()`
Used to change the numerical value of the character with the effect's armor class
**Returns:**
- **AddValue** or **SetValue**: Add or Set table created using `AddValue()` or `SetValue()` helper function

### `roll_initiative()`
Used when the character with the effect rolls initiative
**Returns:**
- **RollResult**: Roll table created using the `RollResult()` helper function, note auto success and failure have no effect in this function.

### `move(old_position, new_position)`
Used whenever the character with the effect moves willingly from one position to the next.
**Parameters:**
- `old_position`: An (x, y) tuple of the position the character with the effect is moving from
- `new_position`: An (x, y) tuple of the position the character with the effect is moving to
**Returns:**
- **Boolean**:
  - `true` if the movement is allowed
  - `false` if the movement is not allowed

## Defining Ability-Specific Effects

Some effects are defined as a part of a related ability, such as the lingering effects of a spell or attack. These effects have their functions and parameters defined in a table format within the ability .lua file. The table can then be passed to the statblock to apply its effects.

#### Example Effect-applying Ability
This example defines an ability which applies a specially-created effect
```
function run(...)
  -- Effect definition
  effect = {
    caster = statblock,

    ability_check_give = function(type, trigger)
      -- Effect effect logic goes here, example gives advantage on any ability check
      return {advantage = true, disadvantage = false, bonus = 0, auto_succeed = false, auto_fail = false}
    end
  }
  -- Example application of effect
  statblock:add_effect(effect)
end
```
## Defining Effect-Dependent Abilities

Some effects may grant the bearer the use of one or more additional abilities, such as concentrating on a spell which allows for a special type of attack. These effects will define a table which contains the run() functions that define each ability, with the ability name as the key for it's function value. This table is called `abilities` and is defined at the top level in the effect script, and it's contents will be factored into the bearer's statblock abilities. If a condtion allows a bearer to perform any action beyond their normal capabilities, it should be defined in this way, even when it is a slightly modified or enhanced version of an existing ability they possess.

#### Example Ability-granting Effect
This example defines a effect which just grants a new ability called `example_attack`
```
abilities = {
  example_attack = function(target)
    -- Function definition for `example_attack` ability
  end
}
```