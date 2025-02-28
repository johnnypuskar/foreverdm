from src.stats.statblock import Statblock
from src.combat.map.positioned import Positioned

class Token(Statblock, Positioned):
    def __init__(self, statblock, position = (-1, -1, -1), map = None):
        Positioned.__init__(self, position, map)
        self._statblock = statblock

        self._extensions = {}
        for ext_x in range(0, int(statblock.get_size().radius/5)):
            for ext_y in range(0, int(statblock.get_size().radius/5)):
                if ext_x + ext_y == 0: # Check if both are 0
                    continue
                self._extensions[(ext_x, ext_y)] = TokenExtension(self, (ext_x, ext_y))

    
    def get_position(self):
        return super().get_position()
    
    def set_position(self, position):
        super().set_position(position)
        for offset, extension in self._extensions.items():
            # Currently ignoring height for tokens, assuming all tokens are 1 tile (5 feet) tall
            extension._position3D = (position[0] + offset[0], position[1] + offset[1], position[2])

    def get_name(self):
        return self._statblock.get_name()
    
    def get_size(self):
        return self._statblock.get_size()
    
    def get_speed(self):
        return self._statblock.get_speed()
    
    def get_initiative_modifier(self):
        return self._statblock.get_initiative_modifier()
    
    def get_armor_class(self):
        return self._statblock.get_armor_class()
    
    def get_proficiency_bonus(self):
        return self._statblock.get_proficiency_bonus()
    
    def tick(self):
        return self._statblock.tick()

    def wrap(self, wrapper):
        return self._statblock.wrap(wrapper)
    
    @property
    def _dice_roller(self):
        return self._statblock._dice_roller
    
    @property
    def _hit_points(self):
        return self._statblock._hit_points
    
    @property
    def _ability_scores(self):
        return self._statblock._ability_scores
    
    @property
    def _level(self):
        return self._statblock._level
    
    @property
    def _abilities(self):
        return self._statblock._abilities
    
    @property
    def _effects(self):
        return self._statblock._effects
    
    @property
    def _turn_resources(self):
        return self._statblock._turn_resources
    
    @property
    def _inventory(self):
        return self._statblock._inventory
    
    @property
    def _controller(self):
        return self._statblock._controller

class TokenExtension(Token):
    def __init__(self, parent, offset = (0, 0)):
        x, y, height = parent.get_position()
        Positioned.__init__(self, (x + offset[0], y + offset[1], height), parent._map) 
        self._parent = parent
    
    ## Positioned Overrides ##
    def set_position(self, position):
        self._parent.set_position(position)

    ## Token Overrides ##
    def get_name(self):
        return self._parent.get_name()
    
    def get_size(self):
        return self._parent.get_size()
    
    def get_speed(self):
        return self._parent.get_speed()
    
    def get_initiative_modifier(self):
        return self._parent.get_initiative_modifier()
    
    def get_armor_class(self):
        return self._parent.get_armor_class()
    
    def get_proficiency_bonus(self):
        return self._parent.get_proficiency_bonus()
    
    def tick(self):
        return self._parent.tick()

    def wrap(self, wrapper):
        return self._parent.wrap(wrapper)
    
    @property
    def _dice_roller(self):
        return self._parent._dice_roller

    @property
    def _hit_points(self):
        return self._parent._hit_points
    
    @property
    def _ability_scores(self):
        return self._parent._ability_scores
    
    @property
    def _level(self):
        return self._parent._level
    
    @property
    def _abilities(self):
        return self._parent._abilities
    
    @property
    def _effects(self):
        return self._parent._effects
    
    @property
    def _turn_resources(self):
        return self._parent._turn_resources
    
    @property
    def _inventory(self):
        return self._parent._inventory

    @property
    def _controller(self):
        return self._parent._controller