from flask_socketio import emit, disconnect
from server.backend.app import socketio

from server.backend.errors.error import Error
from server.backend.instances.instance_manager import InstanceManager

instance_manager = InstanceManager()

@socketio.on('connect')
def handle_connect(auth):
    try:
        response = instance_manager.connect_user(
            auth.get('session_key', None),
            auth.get('campaign_id', None)
        )
        
        emit(response.signal, response.data)
        if response.disconnect:
            pass # disconnect()

    except Error as e:
        # Handle other errors
        emit('error', {'message': str(e)})
        disconnect()

@socketio.on('get_instance_data')
def handle_get_instance_data(data):
    try:
        response = instance_manager.get_instance_data(
            data.get('session_key', None), 
            data.get('campaign_id', None),
            data.get('statblock_id', None)
        )
        emit(response.signal, response.data)
        if response.disconnect:
            disconnect()
    except Error as e:
        # Handle other errors
        emit('error', {'message': str(e)})
        disconnect()