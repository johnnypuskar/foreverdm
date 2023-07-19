
class GridLine:
    WALL_CHARACTERS = {
        (True, True, True, True): '═╬═',
        (True, True, True, False): '═╣ ',
        (True, True, False, True): ' ╠═',
        (True, False, True, True): '═╩═',
        (False, True, True, True): '═╦═',
        (True, True, False, False): ' ║ ',
        (False, False, True, True): '═══',
        (True, False, True, False): '═╝ ',
        (True, False, False, True): ' ╚═',
        (False, True, True, False): '═╗ ',
        (False, True, False, True): ' ╔═',
        (True, False, False, False): ' ╨ ',
        (False, True, False, False): ' ╥ ',
        (False, False, True, False): '═╡ ',
        (False, False, False, True): ' ╞═'
    }
    
    WITHOUT_WALL_CHARACTERS = [' ┼ ', ' ┄ ', ' · ', '   ']

    CORNER = 0
    HORIZONTAL = 1
    VERTICAL = 2
    EMPTY = 3

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    @classmethod
    def with_wall(cls, up, down, left, right):
        return cls(cls.WALL_CHARACTERS[(up, down, left, right)])

    @classmethod
    def without_wall(cls, value):
        return cls(cls.WITHOUT_WALL_CHARACTERS[min(value, 3)])
