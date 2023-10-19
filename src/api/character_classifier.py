import json
from src.api.api_wrapper import APIWrapper
from src.stats.abilities import Ability

class CharacterClassifier:
    CONFIG_PATH = "config/character_classifier_config.json"

    def __init__(self, key):
        config = json.load(open(self.CONFIG_PATH, "r"))
        self._api = APIWrapper(key, config["api"], config["system"])
    
    def classify_ability(self, ability):
        return self._api.send_request(ability)