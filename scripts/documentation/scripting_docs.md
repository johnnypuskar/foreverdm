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

An ability is any potential action a character could take, defined by a Lua script. It may use character resources, call functions or change values from a character's statblock, target other creatures or positions on the map, or influence the game state in many other ways. It is defined by a .lua file that implements a `use_time` global value and `run()` function that returns two values, a boolean determining if the action was a success or not, and a short string detailing the result of the action. Abilities may also define an ability-specific effect.

## Function Definitions and Headers

An ability file will always define one of two functions: `run()` or `modify()`, but the parameters of the function may be one of several possibilities depending on the type of ability. An ability file may never define both functions. Within the both the `run()` and `modify()` functions, as well as the possible `validate()` function, a global `statblock` object will be defined that is a reference to the statblock of the character that has used the ability.

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

The `modify()` function is used in special cases when an ability does not affect the user or some target, but changes how a different ability would act. In practice, this is done by running the code contained in `modify()` before the code in the subsequent abilitiy's `run()` function, to apply changes or temporary effects before it is used.

#### modify(...)
- The modify function can be defined with any number of arguments, or none at all if they are not required. Functions names should be self-explanatory, and use lowercase snake case for name formatting (ex. `spell_level` or `charges_used`).
**Returns:** Boolean
- The modify function returns true in the case that the ability was subsequently modified (i.e. any checks on if the ability was allowed to run passed, and the modification code was run to change the ability for this usage). Otherwise, it returns false to indicate failure, and the subsequent ability in the chain is not run.

### validate()

The `validate()` function is used to run any necessary checks to determine if the ability is able to be used at all, such as checking if the target is within a certain range or if the character using the ability has the required resources - like spell slots or ability charges. The header of the function will always have the same parameters as it's accompanying run or modify function, matching it perfectly as the same parameters are passed to both. If an ability is always able to be used, as in - there is no situation in which a character is unable to use it - there is no need to define a validate function, as validation defaults to always being true.

#### validate(...)
- The validate function should take in the exact same parameters as the abilities run or modify function. Character or object statistics, such as those of the character using the ability's statblock or a possible target, should never be changed or altered in a validate function, only referenced.
**Returns:** boolean, string
- The validate function returns two values: Firstly, a boolean success value which is true in the case that the ability is able to be used. If there is a case in which the ability used with the provided parameters is not possible to be used before even trying, such as targeting a creature out of range or out of sight for abilities that require it, it should return false. The second value is a string descriptor in the case of a false validation, describing why it failed the validation. If the first return value is true, the second return value is nil instead.

## Global Variables

Abilities may sometimes define global variable values at the top level which will be used in the function. This is only used in cases where an ability is part of some larger system, such as a spell being within the spellcasting system. Unless otherwise specified, values should not be defined as globals.

### UseTime Helper Function and Global Variable

Abilities will often have a time cost to use them, primarily being actions, bonus actions, and reactions. To specify this, an ability script file will always define a global `use_time` value at the top level. Some abilities, such as Action Surge or Flexible Casting, do not have a use time - as their use time is either from having limited uses per rest, or from some other resource. In cases like these, where the ability does not cost any actions to use, `use_time` is set to nil. Abilities such as certain spells may also take more than an action to use, taking one or more full minutes. This value is also defined using the UseTime helper function:

While use time is defined in the ability script, it is assumed that the prerequisite time has been met when the ability function is run, so no checks ever need to be made against the `use_time`.

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

### Duration Helper Function

Some global variables must be defined with certain syntax in order to be evaluated correctly. In the case of defining the duration of time it takes to use an ability, as when casting a spell, or the duration of some effect, the Duration helper function is used to define the size of that window of time.

#### `Duration(value, unit)`
Creates the time value specified, in the amount of units specified.
**Parameters:**
- `unit`: the unit of time, valid units are `round`, `minute` or `hour`
- `value`: the integer value of how much time is being defined, defaults to 1

#### Duration Examples
```
-- Defines a period of time which lasts for 3 rounds of combat.
Duration("round", 3)

-- Defines a period of time which lasts for 1 minute.
Duration("minute")

-- Defines a period of time which lasts for 10 minutes.
Duration("minute", 10)

-- Defines a period of time which lasts for 12 hours.
Duration("hour", 12)
```

### Spell Definitions

In the case of spells, there are 6 additional global values that must be defined in every spell ability script. The values are `spell_level`, `spell_school`, `spell_range`, `spell_components`, `spell_duration`, `spell_concentration`. A spell ability must also define `use_time` like any other ability. Their values can be determined from the spell description, and must follow the syntax as defined below.

#### `spell_level`
- `spell_level` is defined with an integer value from 0 to 9 specifying the level of the spell. A level 0 spell represents a cantrip.

#### `spell_school`
- `spell_school` is defined with a string matching one of the following legal values: `abjuration`, `conjuration`, `divination`, `enchantment`, `evocation`, `illusion`, `necromancy`, `transmutation`

#### `use_time`
- `use_time` is defined with the UseTime() helper function to store the casting time of the spell.

#### `spell_range`
- `spell_range` is defined with an integer value as low as zero specifying the range of the spell in feet. A value of 0 is used in the case of a spell with range 'Self', and a value of 1 is used in the case of a spell with range 'Touch'. Perform unit conversion if required.

#### `spell_components`
- `spell_components` is defined with a table that has 1 to 3 entries. The value entry keys for the table are 'V', 'S', and 'M' representing verbal, somatic, and material components. The values of these entries, in the case of 'V' and 'S', will be `true` boolean values in cases where a spell requires these component types. For entries with the 'M' key, the value will be a list of strings, defining each material object as it is said in the spell description. In cases of spells without verbal, somatic, and/or components, `spell_components` should not define the non-required entries in the table at all.

#### `spell_duration`
- `spell_duration` is defined with the Duration() helper function. A value of nil is used in the case of a spell with duration 'Instantaneous'.

#### `spell_concentration`
- `spell_concentration` is defined with a boolean value indicating whether the spell requires concentration or not.

## SetReference Helper Function

Certain abilities or effects may need to remember information or references across multiple uses. Whether it's a reference to the source of an effect, the last target statblock affected, a cumulative sum value, or any other variable, the `SetReference(name, value)` function allows storing and setting values to access them across subsequent uses or turns. Set references can then be used as normal global variables.
(Note: Effect duration is tracked internally and does not require manual handling via this method).

### `SetReference(name, value)`
Sets a global reference which is remained across subsequent uses of an ability or effect script.
**Parameters:**
- `name`: A string name to call the reference variable
- `value`: The value to store at the reference variable name

# Effect Lua Script Format

An effect is any status that alters how a character acts or behaves, by changing the properties of rolls or the characters statistics. It is defined by a .lua file that implements one or more of the following functions, returning a value that alters the corresponding function on the character statblock. Effects act as a form of Decorator pattern.

A effect .lua file will contain function definitions and implementations that handle how that effect should affect those function calls. Effects will only ever implement the functions listed in this documentation.

In cases where a function runs, but is determined to have no effect - such as an effect which only activates under certain conditions - returning `nil` is the correct behavior to speficy that no modifications should be made for that case. Otherwise, functions must always return the correct type of value specified in the function documentation definition.

## RemoveEffect Helper Function

The statblock object allows you to remove any effect by name, but any effect can easily remove itself without needing to pass it's name as a parameter with the `RemoveEffect()` helper function. The lua script will finish out whatever function called this helper function, so it is typical to return right after calling it.

### `RemoveEffect()`
Removes and ends the current effect on the statblock. No parameters, equivalent to running `statblock.remove_effect("<effect name>")`.

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
return RollModifier({advantage = true, bonus = 2})

-- Return a Roll table which automatically fails
return RollModifier({auto_succeed = true})

-- Return a default Roll table which doesn't affect the roll
return RollModifier({})
```

## AddValue, MultiplyValue, and SetValue Helper Functions

Some effect functions return an operative modifier to a numerical stat, to either add some value to the stat, multiply it by some factor, or to set it to some value. This is represented using a table constructed with either the `AddValue(value)`, `MultiplyValue(value)`, or  `SetValue(value)` system-defined helper functuions, which take in the numerical integer value to either set or add to the statistic.

### `AddValue(value)`
Creates and returns the table to define an add operation of some value
**Parameters:**
- `value`: The integer value to be added to the statistic in question

## `MultiplyValue(value)`
Creates and returns the table to define a multiply operation of some value
**Parameters:**
- `value`: The float value to multiply the statistic in question with

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

-- Return a Multiply operator table to double the statistic
return MultiplyValue(2.0)

-- Return a Multiply operator table to half the statistic
return MultiplyValue(0.5)

-- Return a Set operator table to set the statistic value to 19
return SetValue(19)
```

### SpeedModifier Helper Function

A statblock has a speed value defined by up to 5 different types of movement, being `walk`, `fly`, `swim`, `climb`, and `burrow` speed, plus an additional `hover` flag, each determining how many feet of each type of movement can be moved on a single turn. A statblock may have 30 feet of walking speed, but only 15 feet of fly speed. Effects that modify the speed of a statblock must do so by using the `SpeedModifier(modifiers)` system-defined helper function, which allows the effect to add, multiply, and directly set the speed value of any or all of the 5 movement types.

#### `SpeedModifier(modifiers)`
Creates and returns a SpeedModifier table to define how an effect should affect the speed statistic
**Parameters:**
- `modifiers`: A table with one or more of the following values set, undefined values will not be affected
  - `walk`: AddValue, MultiplyValue, or SetValue
    - Math operator function to add to, multiply, or set the walk speed
  - `fly`: AddValue, MultiplyValue, or SetValue
    - Math operator function to add to, multiply, or set the fly speed
  - `swim`: AddValue, MultiplyValue, or SetValue
    - Math operator function to add to, multiply, or set the swim speed
  - `climb`: AddValue, MultiplyValue, or SetValue
    - Math operator function to add to, multiply, or set the climb speed
  - `burrow`: AddValue, MultiplyValue, or SetValue
    - Math operator function to add to, multiply, or set the burrow speed
  - `hover`: Boolean
    - `true` if their movement should be granted hovering status, `false` if hovering should be prevented, defaults to `nil`
  
#### SpeedModifier Examples

```
-- Return a SpeedModifier table to add 10 walking speed
return SpeedModifier({walk = AddValue(10)})

-- Return a SpeedModifier table to remove 15 walking speed and give 30 fly speed
return SpeedModifier({walk = AddValue(-15), fly = SetValue(30)})

-- Return a SpeedModifier table which gives 60 fly (hover) speed
return SpeedModifier({fly = SetValue(60), hover = true})

-- Return a SpeedModifier table which prevents hovering
return SpeedModifier({hover = false})

-- Return a SpeedModifier table to double all movement speed
return SpeedModifier({walk = MultiplyValue(2.0), fly = MultiplyValue(2.0), swim = MultiplyValue(2.0), climb = MultiplyValue(2.0), burrow = MultiplyValue(2.0)})
```

## Function Headers

### `start_turn()`
Used right at the beginning of a character with the effect's turn. Defines logic or effects that happens at the start of their turn.
**Returns:**
- `nil`: No return value

### `end_turn()`
Used right after the end of a charater with the effect's turn. Defines logic or effects that happens at the end of their turn.
**Returns:**
- `nil`: No return value

## `on_apply()`
Used once when the effect has just been applied successfully to the character.
**Returns:**
- `nil`: No return value

## `on_expire()`
Used when the effect's remaining duration has reached 0 and it is about to be removed from the character. Not run when effect is manually removed. Function is run just before automatic removal, so no effect removal logic needs to be implemented.
**Returns:**
- `nil`: No return value

## `on_removal()`
Used once when the effect is about to be removed from the character. Function is run after expiry function.
**Returns:**
- `nil`: No return value

### `make_attack_roll(target)`
Used when the character with the effect makes an attack roll against a target
**Parameters:**
- `target`: The Statblock of the target of the attack
**Returns:**
- **RollModifier**: Roll table created using the `RollModifier()` helper function

### `recieve_attack_roll(attacker)`
Used when the character with the effect is targeted by an attacker, before the attack is determined to hit or not
**Parameters:**
- `attacker`: The Statblock of the attacker
**Returns:**
- **RollModifier**: Roll table created using the `RollModifier()` helper function

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

### `make_saving_throw(type, trigger)`
Used when the character with the effect is forced to make a saving throw by a triggering creature or object
**Parameters:**
- `type`: The 3 letter key for the saving throw ability, valid keys are `str`, `dex`, `con`, `int`, `wis`, `cha`
- `trigger`: The Statblock of the triggering creature or object forcing the character with the effect to make the saving throw
**Returns:**
- **RollModifier**: Roll table created using the `RollModifier()` helper function

### `force_saving_throw(type, target)`
Used when the character with the effect forces a target to make a saving throw
**Parameters:**
- `type`: The 3 letter key for the saving throw ability, valid keys are `str`, `dex`, `con`, `int`, `wis`, `cha`
- `target`: The Statblock of the target making the saving throw
**Returns:**
- **RollModifier**: Roll table created using the `RollModifier()` helper function

### `make_ability_check(type, target)`
Used when the character with the effect makes an ability check
**Parameters:**
- `type`: The 3 letter key for the ability check ability, valid keys are `str`, `dex`, `con`, `int`, `wis`, `cha`
- `target`: The Statblock of the target making the saving throw, may be nil in cases with no target creature
**Returns:**
- **RollModifier**: Roll table created using the `RollModifier()` helper function

### `recieve_ability_check(type, trigger)`
Used when a triggering creature makes an ability check against the creature with the effect
**Parameters:**
- `type`: The 3 letter key for the saving throw ability, valid keys are `str`, `dex`, `con`, `int`, `wis`, `cha`
- `trigger`: The Statblock of the triggering creature making the ability check against the character with the effect 
**Returns:**
- **RollModifier**: Roll table created using the `RollModifier()` helper function

### `make_skill_check(skill, target)`
Used when the character with the effect makes an skill check
**Parameters:**
- `skill`: The skill for the check, valid skills are `acrobatics`, `animal_handling`, `arcana`, `athletics`, `deception`, `history`, `insight`, `intimidation`, `investigation`, `medicine`, `nature`, `perception`, `performance`, `persuasion`, `religion`, `sleight_of_hand`, `stealth`, `survival`
- `target`: The Statblock of the target of the skill check, may be nil in cases with no target creature
**Returns:**
- **RollModifier**: Roll table created using the `RollModifier()` helper function

### `recieve_skill_check(type, trigger)`
Used when a triggering creature makes an skill check against the creature with the effect
**Parameters:**
- `skill`: The skill for the check, valid skills are `acrobatics`, `animal_handling`, `arcana`, `athletics`, `deception`, `history`, `insight`, `intimidation`, `investigation`, `medicine`, `nature`, `perception`, `performance`, `persuasion`, `religion`, `sleight_of_hand`, `stealth`, `survival`
- `trigger`: The Statblock of the triggering creature making the skill check against the character with the effect 
**Returns:**
- **RollModifier**: Roll table created using the `RollModifier()` helper function

### `modify_stat(stat)`
Used to change the numerical value of a given stat on the character with the effect's statsheet
**Parameters:**
- `stat`: The stat to be modified, valid stats are `str`, `dex`, `con`, `int`, `wis`, `cha`, `max_hp`
**Returns:**
- **AddValue**, **MultiplyValue**, or **SetValue**: Add, Multiple, or Set table created using `AddValue()`, `MultiplyValue()`, or `SetValue()` helper function

### `modify_speed()`
Used to change the numerical value of the character with the effect's base speed, i.e. what it resets to at the start of their turn
**Returns:**
- **SpeedModifier**: SpeedModifier table created using the `SpeedModifier()` helper function to define which speed type is modified, and in what way.

### `modify_armor_class()`
Used to change the numerical value of the character with the effect's armor class
**Returns:**
- **AddValue**, **MultiplyValue**, or **SetValue**: Add, Multiple, or Set table created using `AddValue()`, `MultiplyValue()`, or `SetValue()` helper function

### `roll_initiative()`
Used when the character with the effect rolls initiative
**Returns:**
- **RollModifier**: Roll table created using the `RollModifier()` helper function, note auto success and failure have no effect in this function.

### `allow_actions()`
Used to block the character with the effect from performing actions or bonus actions on their turn.
**Returns:**
- `boolean`: 
 - `true` if taking actions is allowed (default)
 - `false` if taking actions is not allowed

## `allow_reactions()`
Used to block the character with the effect from performing reactions on their turn.
**Returns:**
- `boolean`:
 - `true` if taking reactions is allowed (default)
 - `false` if taking reactions is not allowed

### `move(old_pos, new_pos)`
Used whenever the character with the effect moves willingly from one position to the next.
**Parameters:**
- `old_pos`: An (x, y) tuple of the position the character with the effect is moving from
- `new_pos`: An (x, y) tuple of the position the character with the effect is moving to
**Returns:**
- **Boolean**:
  - `true` if the movement is allowed
  - `false` if the movement is not allowed

### `get_abilities()`
Used to return a list of the additional abilities this effect grants.
**Returns:**
- `list[string]`: A list of ability names that correspond to the names of top-level tables in the script that the effect allows the use of. The table must be formatted in the correct format for an effect-dependent ability.

## Defining SubEffects

Some effects are defined as a part of a related ability or effect, such as a secondary effect applied after meeting certain conditions, or an effect applied by using ability. These SubEffects have their functions and parameters defined in a table format within the ability script at the top level. The table name can then be passed to the statblock to apply its effects. Specific global constant values for things such as statblock reference values may also be passed to the SubEffect through a table parameter in the `add_effect` function, which is optional and defaults to an empty table when not used, but SubEffects also have access to other top level variables defined in the script.

#### Example Ability Applying a SubEffect
This example defines an ability which applies a specially-created effect called `effect_name`
```
-- Effect definition, made at top level
effect_name = {
  ability_check_give = function(type, trigger)
    -- Effect effect logic goes here, example gives advantage on any ability check
    return {advantage = true, disadvantage = false, bonus = 0, auto_succeed = false, auto_fail = false}
  end
}

function run(...)
  -- Example application of effect
  statblock:add_effect("effect_name", Duration("round", 1), {"caster": statblock:get_name()})
end
```
## Defining SubAbilities

Similar to SubEffects, a SubAbility is an ability defined as a related part of some other ability or effect, such as a special action granted by having an effect. These SubAbilities have their use time and function defined in a table format within the ability script at the top level. The table name is then returned in a list of one or more granted SubAbility names by the top level effect function `get_abilities`.

#### Example Effect Granting a SubAbility
This example defines a effect which grants two new abilities called `ability_name` and `other_ability`.
```
ability_name = {
  use_time = UseTime("action", 1),
  run = function(target)
    -- Function definition for the `ability_name` ability
  end
}

other_ability = {
  use_time = UseTime("bonus_action", 1),
  can_modify = {"attack"},
  run = function(target)
    -- Function definition for the `other_ability` ability
  end
}

function get_abilities()
  return {"ability_name", "other_ability"}
end
```

## Nesting SubEffects and SubAbilities

SubEffects and SubAbility functionality can be nested, though they must always place their definition at the top level.

#### Example Nested Ability
This example defines an ability, which applies an effect to a target, that in-turn, grants them a secondary ability, that applies a second different effect to a target. Note that each SubEffect and SubAbility are defined at the top level, and referenced by the `add_effect` and `get_abilities` functions using their string names.
```
use_time = UseTime("action", 1)

applied_effect = {
  get_abilities = function()
    return ["secondary_ability"]
  end
}

secondary_ability = {
  use_time = UseTime("bonus_action", 1),
  run = function(target)
    target:add_effect("secondary_effect", Duration("round", 4))
  end
}

secondary_effect = {
  -- Secondary example effect kept empty for brevity
}

function run(target)
  target:add_effect("applied_effect", Duration("minute", 1))
end
```