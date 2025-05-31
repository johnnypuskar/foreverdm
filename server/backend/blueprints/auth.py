from flask import request, jsonify
from server.backend.blueprints.main import main

from server.backend.login.login_manager import LoginManager

@main.route("/auth/google", methods=["POST"])
def auth_google():
    data = request.get_json()
    credential = data.get('credential')
    login = LoginManager()
    
    session_key = login.login_google(credential)
    if session_key is not None:
        return jsonify({
            "status": "success",
            "session_key": session_key
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "Invalid credentials"
        }), 401