from server.backend.database.table import Table

class LocationsTable(Table):

    @staticmethod
    def is_location_id_in_campaign(location_id, campaign_id):
        with Table.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM locations WHERE id = %s AND campaign_id = %s", (location_id, campaign_id))
            result = cur.fetchone()
            return result[0] > 0
    
    @staticmethod
    def get_paused_instance_type_at_location(location_id, campaign_id):
        with Table.cursor() as cur:
            cur.execute("SELECT instance_type FROM paused_instances WHERE location_id = %s AND campaign_id = %s", (location_id, campaign_id))
            result = cur.fetchone()
            return result[0] if result else None
    
    @staticmethod
    def get_statblocks_at_location(location_id, campaign_id):
        with Table.cursor() as cur:
            cur.execute("SELECT id FROM statblocks WHERE location_id = %s AND campaign_id = %s", (location_id, campaign_id))
            results = cur.fetchall()
            return [result[0] for result in results] if results else []