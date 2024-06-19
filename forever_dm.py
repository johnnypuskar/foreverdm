import json
import os
from src.stats.item import Weapon
from src.stats.statblock import Statblock

sword_json = '''
{
    "item": {
        "name": "Shortsword",
        "cost": 10,
        "weight": 2,
        "properties": ["finesse", "light"]
    },
    "abilities": [{
        "type": "attack",
        "class": "melee",
        "target": {"type": "entity", "class": "input"},
        "damage": {"type": "dice", "dice": "1d6"},
        "type": "piercing"
    }]
}
'''

sword_data = json.loads(sword_json)
sword = Weapon(sword_data["item"]["name"], sword_data["item"]["properties"], sword_data["abilities"])


soldier = Statblock("Soldier")
print(soldier._abilities)
soldier.equip(sword)
print(soldier._abilities)
soldier.unequip(sword)
print(soldier._abilities)