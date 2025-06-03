from flask import request, jsonify
from flask_socketio import emit, disconnect, join_room
from server.backend.app import socketio
from server.backend.blueprints.main import main

from server.backend.errors.error_index import Errors
from server.backend.errors.error import Error
from server.backend.database.users import UsersTable
from server.backend.instances.instance_manager import InstanceManager

instance_manager = InstanceManager()

@main.route('/instances/data', methods=['GET'])
def get_instance_data():
    instance_data = {}
    for campaign_id, instances in instance_manager.instances.items():
        instance_data[campaign_id] = {}
        for location_id, instance in instances.items():
            instance_data[campaign_id][location_id] = instance.serialize()
    return jsonify({
        'instances': instance_data,
        'active_statblocks': instance_manager.active_statblocks
    })

def full_disconnect():
    instance_manager.remove_active_statblock(request.sid)
    disconnect()

@socketio.on('set_instance_act_type')
def handle_set_instance_act_type(data):
    try:
        response = instance_manager.set_instance_act_type(
            data.get('session_key'), 
            data.get('campaign_id'),
            data.get('statblock_id'),
            data.get('act_type'),
        )

        emit(response.signal, response.data)
        if response.disconnect:
            full_disconnect()
    except Error as e:
        # Handle other errors
        print("set_instance_act_type:", e)
        emit('error', {'message': str(e)})
        full_disconnect()

@socketio.on('connect')
def handle_connect(auth):
    try:
        UsersTable.get_user_id(auth.get('session_key', None))
        join_room(auth.get('campaign_id'))
        emit('connect_response', {'success': True})
    except Error as e:
        # Handle other errors
        print("connect:", e)
        emit('error', {'message': str(e)})
        full_disconnect()

@socketio.on('disconnect')
def handle_disconnect():
    instance_manager.remove_active_statblock(request.sid)

@socketio.on('get_instance_data')
def handle_get_instance_data(data):
    try:
        response = instance_manager.get_instance_data(
            data.get('session_key'), 
            data.get('campaign_id'),
            data.get('statblock_id')
        )

        if data.get('statblock_id') is not None:
            instance_manager.add_active_statblock(
                request.sid,
                data.get('campaign_id'),
                data.get('statblock_id')
            )

        emit(response.signal, response.data)
        if response.disconnect:
            full_disconnect()
    except Error as e:
        # Handle other errors
        print("get_instance_data:", e)
        emit('error', {'message': str(e)})
        full_disconnect()

@socketio.on('send_command')
def handle_send_command(data):
    try:
        response = instance_manager.send_command(
            data.get('session_key', None), 
            data.get('campaign_id', None),
            data.get('statblock_id', None),
            data.get('command', None),
            data.get('args', [])
        )
        emit(response.signal, response.data)
        if response.disconnect:
            full_disconnect()
    except Error as e:
        # Handle other errors
        print("send_command:", e)
        emit('error', {'message': str(e)})
        full_disconnect()