from server.backend.errors.error_index import Errors
from server.backend.database.table import Table 

class StatblocksTable(Table):
    
    @staticmethod
    def get_statblock_data(statblock_id, campaign_id):
        with Table.cursor() as cur:
            cur.execute("SELECT data FROM statblocks WHERE id = %s AND campaign_id = %s", (statblock_id, campaign_id))
            result = cur.fetchone()
            if result is None:
                raise Errors.StatblockNotFound()
            return result[0]
        raise Errors.DataAccessError()

    @staticmethod
    def get_statblock_location_id(statblock_id, campaign_id):
        with Table.cursor() as cur:
            cur.execute("SELECT location_id FROM statblocks WHERE id = %s AND campaign_id = %s", (statblock_id, campaign_id))
            result = cur.fetchone()
            if result is None:
                raise Errors.StatblockNotFound()
            return result[0]
        raise Errors.DataAccessError()

    @staticmethod
    def get_statblocks_at_location_id(location_id, campaign_id):
        with Table.cursor() as cur:
            cur.execute("SELECT id FROM statblocks WHERE location_id = %s AND campaign_id = %s", (location_id, campaign_id))
            results = cur.fetchall()
            return [result[0] for result in results] if results else []
        raise Errors.DataAccessError()

    @staticmethod
    def is_user_in_campaign(user_id, campaign_id):
        with Table.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM campaign_users WHERE user_id = %s AND campaign_id = %s", (user_id, campaign_id))
            result = cur.fetchone()
            return result[0] > 0 if result else False
        raise Errors.DataAccessError()
            
    @staticmethod
    def validate_user_statblock_ownership(user_id, statblock_id, campaign_id):
        with Table.cursor() as cur:
            cur.execute("""
                SELECT location_id FROM statblocks WHERE
                user_id = %s AND campaign_id = %s AND id = %s
            """, (user_id, campaign_id, statblock_id))
            result = cur.fetchone()
            if result is not None:
                return result[0]
            
            cur.execute("SELECT COUNT(*) FROM statblocks WHERE id = %s AND campaign_id = %s", (statblock_id, campaign_id))
            statblock_in_campaign = cur.fetchone()
            if not statblock_in_campaign or statblock_in_campaign[0] == 0:
                raise Errors.StatblockNotInCampaign()
            
            # Assume via process of elimination
            raise Errors.UserNotOwnStatblock()
        raise Errors.DataAccessError()
    
    @staticmethod
    def get_user_statblocks(user_id, campaign_id):
        with Table.cursor() as cur:
            cur.execute("SELECT id, name FROM statblocks WHERE user_id = %s AND campaign_id = %", (user_id, campaign_id))
            result = cur.fetchall()
            return [(statblock_id, name) for statblock_id, name in result] if result else []