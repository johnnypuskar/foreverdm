from google.oauth2 import id_token
from google.auth.transport import requests
import os

from server.backend.database.users import UsersTable

GOOGLE_OAUTH_SECRET = os.getenv("GOOGLE_OAUTH_SECRET")
GOOGLE_OAUTH_CLIENT = os.getenv("GOOGLE_OAUTH_CLIENT")

class LoginManager:
    def __init__(self):
        pass

    def login_google(self, credential):
        try:
            idinfo = id_token.verify_oauth2_token(
                credential, requests.Request(), GOOGLE_OAUTH_CLIENT
            )
            user_id = UsersTable.get_user_id_from_username(idinfo.get("email"))
            if user_id is not None:
                session_key = UsersTable.new_user_session(user_id)
                return session_key
            return None
        except Exception as e:
            return None