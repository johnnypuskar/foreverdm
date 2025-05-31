from flask import Blueprint, jsonify, request

import json
from server.backend.database.users import UsersTable
from server.backend.database.statblocks import StatblocksTable
from server.backend.database.locations import LocationsTable

admin_blueprint = Blueprint('admin', __name__, url_prefix='/admin')

@admin_blueprint.route('add-location', methods=['POST'])
def add_location():
    data = request.get_json()
    
    location_id = data.get('location_id')
    campaign_id = data.get('campaign_id')
    name = data.get('location_name')

    LocationsTable.insert_location(location_id, campaign_id, name, None)
    return jsonify({
        "status": "success",
        "message": "Location added successfully"
    }), 200

@admin_blueprint.route('add-statblock', methods=['POST'])
def add_statblock():
    data = request.get_json()
    session_key = data.get('session_key')
    user_id = UsersTable.get_user_id(session_key)
    
    statblock_id = data.get('statblock_id')
    campaign_id = data.get('campaign_id')
    name = data.get('statblock_name')
    location_id = data.get('location_id')
    statblock_data = json.dumps(data.get('statblock_data'))

    StatblocksTable.insert_statblock(statblock_id, name, campaign_id, user_id, location_id, statblock_data)
    return jsonify({
        "status": "success",
        "message": "Statblock added successfully"
    }), 200