from __future__ import annotations
from src.combat.map.generator.room_region import RoomRegion

class DynamicRoomRegion(RoomRegion):
    def __init__(self, length, width, back_t_length = 0, back_t_width = 0, back_t_offset = 0, front_t_length = 0, front_t_width = 0, front_t_offset = 0):
        super().__init__()
        self._length = length
        self._width = width
        self._back_t_length = back_t_length
        self._back_t_width = back_t_width
        self._front_t_length = front_t_length
        self._front_t_width = front_t_width
        if back_t_offset > length - back_t_length:
            raise ValueError(f"Back T offset exceeds maximum value: {length} (length) - {back_t_length} (back T length) > {back_t_offset}")
        if front_t_offset > length - front_t_length:
            raise ValueError(f"Front T offset exceeds maximum value: {length} (length) - {front_t_length} (front T length) > {front_t_offset}")
        self._back_t_offset = back_t_offset
        self._front_t_offset = front_t_offset

    @property
    def cells(self):
        if self._cells is None:
            self.compute_cells()
        return self._cells
    
    def compute_cells(self):
        self._cells = set()
        self._border_cells = set()
        for x in range(self._length):
            for y in range(self._width):
                self.add_cell(x, y)
                if (y == 0) or (y == self._width - 1) or \
                (x == 0 and (y < self._back_t_offset or y >= self._back_t_offset + self._back_t_width)) or \
                (x == self._length - 1 and (y < self._front_t_offset or y >= self._front_t_offset + self._front_t_width)):
                    self._border_cells.add((x, y))
        if self._back_t_length > 0 and self._back_t_width > 0:
            for x in range(self._back_t_length):
                for y in range(self._back_t_width):
                    cx, cy = -1 - x, y + self._back_t_offset
                    self.add_cell(cx, cy)
                    if (y == 0) or (y == self._back_t_width - 1) or (x == 0):
                        self._border_cells.add((cx, cy))
        if self._front_t_length > 0 and self._front_t_width > 0:
            for x in range(self._front_t_length):
                for y in range(self._front_t_width):
                    cx, cy = self._length + x, y + self._front_t_offset
                    self.add_cell(cx, cy)
                    if (y == 0) or (y == self._front_t_width - 1) or (x == self._front_t_length - 1):
                        self._border_cells.add((cx, cy))
        return self._cells

    def compute_configuration_offsets(self, other: DynamicRoomRegion):
        configuration_offsets = set()
        for dx in range(-(other._length + other._front_t_length), self._length + other._back_t_length + 1):
            for dy in range(-other._width, self._width + 1):
                adjacencies = 0
                for other_cell in other.cells:
                    cx, cy = other_cell[0] + dx, other_cell[1] + dy
                    if (cx, cy) in self.cells:
                        adjacencies = 0
                        break
                    if (cx + 1, cy) in self.border_cells:
                        adjacencies += 1
                    if (cx - 1, cy) in self.border_cells:
                        adjacencies += 1
                    if (cx, cy + 1) in self.border_cells:
                        adjacencies += 1
                    if (cx, cy - 1) in self.border_cells:
                        adjacencies += 1
                if adjacencies > 0:
                    configuration_offsets.add((dx, dy, adjacencies))
        return configuration_offsets
    
    def __str__(self):
        return f"""DynamicRoomRegion(
            length={self._length}, width={self._width}, 
            back_t_length={self._back_t_length}, back_t_width={self._back_t_width}, back_t_offset={self._back_t_offset}, 
            front_t_length={self._front_t_length}, front_t_width={self._front_t_width}, front_t_offset={self._front_t_offset}
        )
        """