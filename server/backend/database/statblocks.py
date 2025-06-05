from server.backend.errors.error_index import Errors
from server.backend.database.table import Table 

class StatblocksTable(Table):
    
    @staticmethod
    def validate_location_from_credentials(session_id, campaign_id, statblock_id):
        if session_id is None:
            raise Errors.SessionNotFound()
        
        if campaign_id is None:
            raise Errors.UserNotInCampaign()

        with Table.cursor() as cur:
            cur.execute("SELECT user_id FROM sessions WHERE session_key = %s", (session_id,))
            user_id = cur.fetchone()
            if user_id is None:
                raise Errors.SessionNotFound()
            user_id = user_id[0]

            cur.execute("SELECT COUNT(*) FROM campaign_users WHERE user_id = %s AND campaign_id = %s", (user_id, campaign_id))
            campaign_users = cur.fetchone()
            if campaign_users is None or campaign_users[0] == 0:
                raise Errors.UserNotInCampaign()
            
            if statblock_id is None:
                raise Errors.StatblockNotFound()
            
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
    def validate_user_statblocks_in_campaign(session_id, campaign_id):
        if session_id is None:
            raise Errors.SessionNotFound()
        
        if campaign_id is None:
            raise Errors.UserNotInCampaign()

        with Table.cursor() as cur:
            cur.execute("SELECT user_id FROM sessions WHERE session_key = %s", (session_id,))
            user_id = cur.fetchone()
            if user_id is None:
                raise Errors.SessionNotFound()
            user_id = user_id[0]

            cur.execute("SELECT id, name FROM statblocks WHERE user_id = %s AND campaign_id = %s", (user_id, campaign_id))
            result = cur.fetchall()
            return [(statblock_id, name) for statblock_id, name in result] if result else []
        raise Errors.DataAccessError()
    
    @staticmethod
    def get_users_statblocks(user_id, campaign_id):
        with Table.cursor() as cur:
            cur.execute("SELECT id FROM statblocks WHERE user_id = %s AND campaign_id = %s", (user_id, campaign_id))
            result = cur.fetchall()
            return [statblock_id for statblock_id, in result] if result else []
        raise Errors.DataAccessError()
    
    @staticmethod
    def get_statblock_data(statblock_id, campaign_id):
        with Table.cursor() as cur:
            cur.execute("SELECT data FROM statblocks WHERE id = %s AND campaign_id = %s", (statblock_id, campaign_id))
            result = cur.fetchone()
            if result is not None:
                return result[0]
            raise Errors.StatblockNotFound()
        raise Errors.DataAccessError()

    @staticmethod
    def get_location(statblock_id, campaign_id):
        with Table.cursor() as cur:
            cur.execute("SELECT location_id FROM statblocks WHERE id = %s AND campaign_id = %s", (statblock_id, campaign_id))
            result = cur.fetchone()
            if result is not None:
                return result[0]
            raise Errors.StatblockNotFound()
        raise Errors.DataAccessError()

    @staticmethod
    def update_location(statblock_id, campaign_id, location_id):
        with Table.cursor() as cur:
            cur.execute("UPDATE statblocks SET location_id = %s WHERE id = %s AND campaign_id = %s", (location_id, statblock_id, campaign_id))
            if cur.rowcount == 0:
                raise Errors.StatblockNotFound()
            return
        raise Errors.DataAccessError()

    @staticmethod
    def insert_statblock(statblock_id, name, campaign_id, user_id, location_id, data):
        with Table.cursor() as cur:
            cur.execute("""
                INSERT INTO statblocks (id, name, campaign_id, user_id, location_id, data)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (statblock_id, name, campaign_id, user_id, location_id, data))
            return
        raise Errors.DataAccessError()