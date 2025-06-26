from server.backend.errors.error_index import Errors
from server.backend.database.table import Table 

class MapGenerationTable(Table):
    def bulk_insert_room_region_config(self, fixed_hash, relative_hash, adjacency_set):
        self._cursor.execute("SELECT COUNT(*) FROM dynamic_room_region_configurations WHERE fixed_hash = %s AND relative_hash = %s", (fixed_hash, relative_hash))
        existing = self._cursor.fetchone()
        if existing and existing[0] > 0:
            return

        prepared_values = [(fixed_hash, relative_hash, dx, dy, adjacencies) for (dx, dy, adjacencies) in adjacency_set]
        self._cursor.executemany("INSERT INTO dynamic_room_region_configurations VALUES (%s, %s, %s, %s, %s)", prepared_values)
        
        if fixed_hash != relative_hash:
            prepared_inverse_values = [(relative_hash, fixed_hash, -dx, -dy, adjacencies) for (dx, dy, adjacencies) in adjacency_set]
            self._cursor.executemany("INSERT INTO dynamic_room_region_configurations VALUES (%s, %s, %s, %s, %s)", prepared_inverse_values)
    
    def reset_room_region_configurations(self):
        self._cursor.execute("DELETE FROM dynamic_room_region_configurations")