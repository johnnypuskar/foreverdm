from flask import jsonify, request
from server.backend.blueprints.main import main

import json
from server.backend.database.users import UsersTable
from server.backend.database.statblocks import StatblocksTable
from server.backend.database.locations import LocationsTable
from server.backend.database.campaigns import CampaignsTable

@main.route('/admin/add-location', methods=['POST'])
def add_location():
    data = request.get_json()
    
    location_id = data.get('location_id')
    campaign_id = data.get('campaign_id')
    name = data.get('location_name')
    desc = data.get('location_desc')

    LocationsTable.insert_location(location_id, campaign_id, name, desc, None)
    return jsonify({
        "status": "success",
        "message": "Location added successfully"
    }), 200

@main.route('/admin/add-adjacency', methods=['POST'])
def add_adjacency():
    data = request.get_json()
    
    first_location_id = data.get('first_location_id')
    second_location_id = data.get('second_location_id')
    campaign_id = data.get('campaign_id')

    LocationsTable.make_location_adjacent(first_location_id, second_location_id, campaign_id)
    return jsonify({
        "status": "success",
        "message": "Adjacency added successfully"
    }), 200

@main.route('/admin/add-statblock', methods=['POST'])
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

@main.route('/admin/add-campaign', methods=['POST'])
def add_campaign():
    data = request.get_json()
    
    campaign_id = data.get('campaign_id')

    CampaignsTable.insert_campaign(campaign_id)
    return jsonify({
        "status": "success",
        "message": "Campaign added successfully"
    }), 200

@main.route('/admin/join-campaign', methods=['POST'])
def join_campaign():
    data = request.get_json()
    session_key = data.get('session_key')
    campaign_id = data.get('campaign_id')

    user_id = UsersTable.get_user_id(session_key)
    CampaignsTable.add_user_to_campaign(user_id, campaign_id)
    
    return jsonify({
        "status": "success",
        "message": "User added to campaign successfully"
    }), 200
