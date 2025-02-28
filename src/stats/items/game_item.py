class GameItem:
    def __init__(self, name, description, weight, size, tags: list):
        self._name = name
        self._description = description
        self._size = size
        self._weight = weight
        self._tags = tags
    
    @property
    def name(self):
        return self._name

    @property
    def melee_damage(self):
        return "1d4 bludgeoning"
    
    @property
    def ranged_damage(self):
        return "1d4 bludgeoning"
    
    @property
    def normal_range(self):
        return 20

    @property
    def long_range(self):
        return 60

    def has_tag(self, tag):
        return tag in self._tags