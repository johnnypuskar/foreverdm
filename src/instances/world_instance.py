import secrets
from src.instances.instance import Instance

class WorldInstance(Instance):
    def __init__(self):
        super().__init__()
        self.type = 'WORLD'
    
    @staticmethod
    def from_data(data):
        return WorldInstance()