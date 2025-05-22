from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from server.backend.lobbies.lobby import Lobby

import sys
import os

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

active_lobbies = {}

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "status": "running",
        "version": "0.0.1"
    })

@socketio.on('join')
def handle_connect(lobby_id, player_id):
    if lobby_id not in active_lobbies.keys():
        active_lobbies[lobby_id] = Lobby(lobby_id)
    active_lobbies[lobby_id].player_join(player_id)
    emit('join_response', { 'status': 'success', 'lobby_id': lobby_id, 'player_id': player_id })

@socketio.on('leave')
def handle_disconnect(lobby_id, player_id):
    if lobby_id not in active_lobbies.keys():
        emit('leave_response', { 'status': 'error', 'message': 'Lobby not found' })
        return
    leave_status = active_lobbies[lobby_id].player_leave(player_id)
    if len(active_lobbies[lobby_id].players) == 0:
        del active_lobbies[lobby_id]
    if leave_status:
        emit('leave_response', { 'status': 'success', 'message': 'Player left successfully' })
    else:
        emit('leave_response', { 'status': 'error', 'message': 'Player not found in lobby' })

@socketio.on('debug_info')
def handle_debug_info():
    emit('debug_info_data', {
        'lobbies': list(active_lobbies.keys()),
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)