from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from server.backend.instances.instance_manager import InstanceManager
from server.backend.login.login_manager import LoginManager

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

instance_manager = InstanceManager()

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "status": "running",
        "version": "0.0.1"
    })

@app.route('/auth/google', methods=['POST'])
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

@socketio.on('connect')
def handle_connect(data):
    try:
        response = instance_manager.connect_user(
            data.get('session_id', None),
            data.get('campaign_id', None)
        )
        emit(response.signal, response.data)
        if response.disconnect:
            socketio.disconnect()
    except Exception as e:
        # Handle other errors
        emit('error', {'message': str(e)})
        socketio.disconnect()

@socketio.on('get_instance_data')
def handle_get_instance_data(data):
    try:
        response = instance_manager.get_instance_data(
            data.get('session_id', None), 
            data.get('campaign_id', None),
            data.get('statblock_id', None)
        )
        emit(response.signal, response.data)
        if response.disconnect:
            socketio.disconnect()
    except Exception as e:
        # Handle other errors
        emit('error', {'message': str(e)})
        socketio.disconnect()

if __name__ == '__main__':
    app.run(debug=True, port=5000)