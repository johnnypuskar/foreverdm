import json
import os
from src.api.api_wrapper import GeminiAPIWrapper
from src.stats.statblock import Statblock
from src.map.battlemap import Map, MapProp
from src.map.instance import Instance
from src.map.token import Token

test_system = "You are an AI D&D 5e assistant, and will answer any questions about the system as close to the rules as possible."

API_KEY = json.load(open("foreverdm/config/api_config.json", "r"))["GEMINI_API_KEY"]

api = GeminiAPIWrapper(API_KEY)

map = Map(5,3)
prop = MapProp("Box", "A wooden box")
map.add_prop(prop, (4, 2))

instance = Instance(map)

token = Token(Statblock("Fighter", "A level 1 fighter"))
instance.add_token(token, (1, 1))

prompt = f"What is in the room? ROOM: [{instance.get_context()}]"

print("> ",prompt,"\n",api.send_request(prompt))