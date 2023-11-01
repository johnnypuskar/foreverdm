import json
import psycopg2

class DatabaseAccess:
    def __init__(self, config):
        config = json.load(open("database/config/db_config.json", "r"))[config]
        self.conn = psycopg2.connect(**config)
    
    # Note: This function is for early testing only and will be replaced with actual DB API functions later
    def query(self, query):
        cur = self.conn.cursor()
        cur.execute(query)
        self.conn.commit()
        cur.close()