from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'frontend/dist'))
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

last_message = "NULL"

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "status": "running",
        "version": "0.0.1"
    })

# Vue Frontend #
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and not path.startswith('api') and os.path.exists(os.path.join(app.static_folder, path)):
        # Returns the file from the static folder if it exists
        return send_from_directory(app.static_folder, path)
    else:
        # Otherwise, return the index.html file
        return send_from_directory(app.static_folder, 'index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('response', {'data': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(data):
    print(f"Received message: {data}")
    global last_message
    last_message = data
    emit('response', {'data': f"Message received: {data}"})

@socketio.on('ping')
def handle_ping():
    print(f"Last message: {last_message}")

if __name__ == '__main__':
    app.run(debug=True, port=5000)