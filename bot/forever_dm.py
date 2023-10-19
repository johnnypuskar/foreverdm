import json
import os
from src.api.character_classifier import CharacterClassifier

test_system = "You are an AI D&D 5e assistant, and will answer any questions about the system as close to the rules as possible."

API_KEY = json.load(open("config/api_config.json", "r"))["API_KEY"]

api = CharacterClassifier(API_KEY)

mobile_feat = "Mobile: You are exceptionally speedy and agile. You gain the following benefits: Your speed increases by 10 feet. When you use the Dash action, difficult terrain doesn't cost extra movement on that turn. When you make a melee attack against a creature, you don't provoke opportunity attacks from that creature for the rest of the turn, whether you hit or not."
arcane_jolt = "Arcane Jolt: You've learn new ways to channel arcane energy to harm or heal. When either you hit a target with a magic weapon attack or your steel defender hits a target, you can channel magical energy through the strike to create one of the following effects: The target takes an extra 2d6 force damage. Choose one creature or object you can see within 30 feet of the target. Healing energy flows into the chosen recipient, restoring 2d6 hit points to it. You can use this energy a number of times equal to your Intelligence modifier (minimum of once), but you can do so no more than once on a turn. You regain all expended uses when you finish a long rest."
telekinetic = "Telekinetic: You learn to move things with your mind, granting you the following benefits. You learn the mage hand cantrip. You can cast it without verbal or somatic components, and you can make the spectral hand invisible. If you already know this spell, its range increases by 30 feet when you cast it. As a bonus action, you can try to telekinetically shove one creature you can see within 30 feet of you. When you do so, the target must succeed on a Strength saving throw (DC 8 + your proficiency bonus + the ability modifier of the score increased by this feat) or be moved 5 feet toward you or away from you. A creature can willingly fail this save."

print(api.classify_ability(telekinetic))