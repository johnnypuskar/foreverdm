import json
import os
from src.util.lua_manager import LuaManager
from src.stats.statblock import Statblock, ResourceIndex, AbilityIndex
from src.stats.abilities import Ability, CompositeAbility
from src.stats.item import Weapon
from src.util.dice import DiceSum, DiceParser
import copy
import lupa

import base64

attacker = Statblock("Attacker")
sword = Weapon("shortsword", DiceSum(d8=1))
attacker._equipped_weapon = sword

target = Statblock("Target")

attack_script = ''
dash_script = ''
fire_bolt_script = ''

# Use a context manager to open and read the file
with open("foreverdm/scripts/actions/attack.lua", 'r', encoding='utf-8') as file:
    attack_script = file.read()
with open("foreverdm/scripts/actions/dash.lua", 'r', encoding='utf-8') as file:
    dash_script = file.read()
with open("foreverdm/scripts/spells/fire_bolt.lua", 'r', encoding='utf-8') as file:
    fire_bolt_script = file.read()

index = AbilityIndex()

# ability = Ability("fire_bolt", fire_bolt_script)
# ability.initialize({})
# print(ability._lua.get_defined_functions())
# print(ability._lua.get_function_script(ability._lua._lua.globals()["run"]))

a = Ability("ability_a", "function run(parameter)\n    return true, parameter\n end")
b = Ability("ability_b", "function run()\n    return true, 'Ability B.'\n end")
c_script = '''
function run()
    return true, 'Ability C.'
end
'''
c = Ability("ability_c", c_script)
d = Ability("ability_d", "function run()\n    return true, 'Ability D.'\n end")

composite = CompositeAbility("composite", "")
composite.add(a)
composite.add(b)

mega_comp = CompositeAbility("mega_comp", "")
mega_comp.add(composite)

top_level = CompositeAbility("top_level", "")
top_level.add(mega_comp)

index.add(c)
index.add(d)
index.add(top_level)

print(index.get_all_keys())
print(index.run("top_level.mega_comp.composite.ability_a", attacker))

attack = Ability("attack", attack_script)
dash = Ability("dash", dash_script)
# modifier = Ability("modifier", modifier_script, "modify")

attacker._abilities.add(attack)
attacker._abilities.add(dash)
# attacker._abilities.add(modifier)
attacker._abilities.add(composite)

for header in attacker._abilities.get_headers():
    print(header)

# print(attacker.name, attacker._hp, attacker._speed, f"{attacker._armor_class} AC")
# print(target.name, target._hp, target._speed, f"{target._armor_class} AC")
# print("USING ABILITIES")
# print(attacker.use_abilities((("modifier", 15), ("attack", target))))
# print(attacker.name, attacker._hp, attacker._speed, f"{attacker._armor_class} AC")
# print(target.name, target._hp, target._speed, f"{target._armor_class} AC")

# print(attacker.use_ability("composite.ability_a", 4))

# print("DASHING")
# print(attacker.__dict__)
# print(attacker.use_ability("dash"))
# print(attacker.__dict__)

# print("\nATTACKING")
# print(target.__dict__)
# print(attacker.use_ability("attack", target))
# print(target.__dict__)

print(DiceParser.parse_string("1d4+2d6+3d8+4d10+5d12+6"))


