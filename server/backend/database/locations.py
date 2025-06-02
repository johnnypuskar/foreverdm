from server.backend.errors.error_index import Errors
from server.backend.database.table import Table

class LocationsTable(Table):

    @staticmethod
    def validate_location_in_campaign(location_id, campaign_id):
        with Table.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM locations WHERE id = %s AND campaign_id = %s", (location_id, campaign_id))
            result = cur.fetchone()
            if result[0] > 0:
                return True
            
            raise Errors.InvalidLocation()
        raise Errors.DataAccessError()

    @staticmethod
    def get_paused_instance_act_details(location_id, campaign_id):
        with Table.cursor() as cur:
            cur.execute("SELECT act_type, act_data FROM paused_instances WHERE location_id = %s AND campaign_id = %s", (location_id, campaign_id))
            result = cur.fetchone()
            if result is not None:
                return (result[0], result[1])
            return (None, None)
        raise Errors.DataAccessError()

    @staticmethod
    def get_statblocks_at_location(location_id, campaign_id):
        with Table.cursor() as cur:
            cur.execute("SELECT id FROM statblocks WHERE location_id = %s AND campaign_id = %s", (location_id, campaign_id))
            results = cur.fetchall()
            return [result[0] for result in results] if results else []
        raise Errors.DataAccessError()

    @staticmethod
    def get_location_details(location_id, campaign_id):
        with Table.cursor() as cur:
            cur.execute("SELECT name, description FROM locations WHERE id = %s AND campaign_id = %s", (location_id, campaign_id))
            result = cur.fetchone()
            name = result[0] if result else None
            description = result[1] if result else None

            cur.execute("""
                SELECT l.id, l.name
                FROM location_adjacencies la
                INNER JOIN locations l ON la.second_location_id = l.id
                WHERE la.first_location_id = %s AND la.campaign_id = %s AND l.campaign_id = %s
                UNION
                SELECT l.id, l.name
                FROM location_adjacencies la
                INNER JOIN locations l ON la.first_location_id = l.id
                WHERE la.second_location_id = %s AND la.campaign_id = %s AND l.campaign_id = %s
            """, (location_id, campaign_id, campaign_id, location_id, campaign_id, campaign_id,))
            results = cur.fetchall()
            adjacent = [(result[0], result[1]) for result in results] if results else []

            return (name, description, adjacent)
        raise Errors.DataAccessError()

    @staticmethod
    def is_statblock_adjacent(statblock_id, location_id, campaign_id):
        with Table.cursor() as cur:
            cur.execute("""
                SELECT SUM(adjacent)
                FROM (
                    SELECT COUNT(*) AS adjacent
                    FROM location_adjacencies la
                    INNER JOIN statblocks s ON s.location_id = la.first_location_id
                    WHERE s.id = %s AND la.second_location_id = %s AND s.campaign_id = %s AND la.campaign_id = %s
                    UNION ALL
                    SELECT COUNT(*) AS adjacent
                    FROM location_adjacencies la
                    INNER JOIN statblocks s ON s.location_id = la.second_location_id
                    WHERE s.id = %s AND la.first_location_id = %s AND s.campaign_id = %s AND la.campaign_id = %s
                ) AS sq;
            """, (statblock_id, location_id, campaign_id, campaign_id, statblock_id, location_id, campaign_id, campaign_id))
            result = cur.fetchone()
            return result[0] > 0 if result else False
        raise Errors.DataAccessError()

    @staticmethod
    def insert_location(location_id, campaign_id, name, desc, map_data):
        with Table.cursor() as cur:
            cur.execute("""
                INSERT INTO locations (id, campaign_id, name, description, map_data)
                VALUES (%s, %s, %s, %s, %s)
            """, (location_id, campaign_id, name, desc, map_data))
            return
        raise Errors.DataAccessError()
    
    @staticmethod
    def make_location_adjacent(location_id_1, location_id_2, campaign_id):
        with Table.cursor() as cur:
            cur.execute("""
                INSERT INTO location_adjacencies (first_location_id, second_location_id, campaign_id)
                VALUES (%s, %s, %s)
            """, (location_id_1, location_id_2, campaign_id))
            return
        raise Errors.DataAccessError()