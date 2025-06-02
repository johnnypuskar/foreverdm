from server.backend.errors.error_index import Errors
from server.backend.database.table import Table 

class CampaignsTable(Table):

    @staticmethod
    def insert_campaign(campaign_id):
        with Table.cursor() as cur:
            cur.execute("INSERT INTO campaigns (id) VALUES (%s)", (campaign_id,))
            return
        raise Errors.DataAccessError()
            
    @staticmethod
    def add_user_to_campaign(user_id, campaign_id):
        with Table.cursor() as cur:
            cur.execute("INSERT INTO campaign_users (user_id, campaign_id) VALUES (%s, %s)", (user_id, campaign_id))
            return
        raise Errors.DataAccessError()