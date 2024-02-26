import json
import os
from src.api.api_wrapper import GeminiAPIWrapper
from src.map.battlemap import Map, MapProp
from src.map.instance import Instance

test_system = "You are an AI D&D 5e assistant, and will answer any questions about the system as close to the rules as possible."

API_KEY = json.load(open("foreverdm/config/api_config.json", "r"))["GEMINI_API_KEY"]

api = GeminiAPIWrapper(API_KEY)

# prompt = "Describe in 1-2 sentences a turn of D&D where a goblin attacks a fighter with a scimitar and deals 7 damage."
# print("> ",prompt,"\n",api.send_request(prompt))\

map = Map(5,3)
prop = MapProp("Box", "A wooden box")
map.add_prop(prop, (2, 2))

instance = Instance(map)
print(instance.get_context())
map.remove_prop(prop)

print(instance.get_context())