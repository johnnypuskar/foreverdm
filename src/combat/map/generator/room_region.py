from __future__ import annotations
import sys

class RoomRegion:
    def __init__(self):
        self._min_corner = (sys.maxsize, sys.maxsize)
        self._max_corner = (-sys.maxsize, -sys.maxsize)
        self._cells = set()
        self._border_cells = set()
        self._stale_border_cells = True
        
    @property
    def hash(self):
        hash_values = []
        bitcount = 0
        for x in range(self.min_corner[0], self.max_corner[0] + 1):
            for y in range(self.min_corner[1], self.max_corner[1] + 1):
                if bitcount % 32 == 0:
                    hash_values.append(1 if (x, y) in self._cells else 0)
                else:
                    hash_values[-1] = (hash_values[-1] << 1) | (1 if (x, y) in self._cells else 0)
                bitcount += 1
        hash_values.insert(0, self.min_corner)
        hash_values.insert(1, self.max_corner)
        return hash(tuple(hash_values))

    @property
    def min_corner(self):
        return self._min_corner if self._cells else (0, 0)

    @property
    def max_corner(self):
        return self._max_corner if self._cells else (0, 0)

    @property
    def border_cells(self):
        if self._stale_border_cells:
            self._border_cells.clear()
            for cell in self._cells:
                x, y = cell
                if (x + 1, y) not in self._cells:
                    self._border_cells.add(RoomRegion.BorderCell(x, y, (1, 0)))  # Right
                if (x - 1, y) not in self._cells:
                    self._border_cells.add(RoomRegion.BorderCell(x, y, (-1, 0))) # Left
                if (x, y + 1) not in self._cells:
                    self._border_cells.add(RoomRegion.BorderCell(x, y, (0, 1)))  # Up
                if (x, y - 1) not in self._cells:
                    self._border_cells.add(RoomRegion.BorderCell(x, y, (0, -1))) # Down
            self._stale_border_cells = False
        return self._border_cells

    def add_cell(self, x, y):
        self._cells.add((x, y))
        if x < self._min_corner[0] or y < self._min_corner[1]:
            self._min_corner = (min(self._min_corner[0], x), min(self._min_corner[1], y))
        if x > self._max_corner[0] or y > self._max_corner[1]:
            self._max_corner = (max(self._max_corner[0], x), max(self._max_corner[1], y))
        self._stale_border_cells = True
    
    def compute_configuration_offsets(self, other: RoomRegion):
        configuration_offsets = set()
        for self_border_cell in self.border_cells:
            for other_border_cell in other.border_cells:
                if not self_border_cell.opposes(other_border_cell):
                    continue
                

    class BorderCell:
        def __init__(self, x, y, dir):
            self.x = x
            self.y = y
            self.dir = dir
        
        def opposes(self, other: RoomRegion.BorderCell):
            return self.dir[0] + other.dir[0] == 0 and self.dir[1] + other.dir[1] == 0