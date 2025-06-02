import secrets
from server.backend.errors.error_index import Errors
from server.backend.database.table import Table 

class UsersTable(Table):
    def __init__(self):
        pass
    
    @staticmethod
    def get_user_id_from_username(username):
        with Table.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            result = cur.fetchone()
            return result[0] if result else None
        raise Errors.DataAccessError()

    @staticmethod
    def new_user_session(user_id):
        with Table.cursor() as cur:
            session_key = secrets.token_hex(16)
            cur.execute("INSERT INTO sessions (session_key, user_id) VALUES (%s, %s)", (session_key, user_id))
            return session_key
        raise Errors.DataAccessError()
    
    @staticmethod
    def get_user_id(session_key):
        with Table.cursor() as cur:
            cur.execute("SELECT user_id FROM sessions WHERE session_key = %s", (session_key,))
            result = cur.fetchone()
            if result is not None:
                return result[0]
            
            raise Errors.SessionNotFound()
        raise Errors.DataAccessError()