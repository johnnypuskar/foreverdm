from flask import jsonify, request
from server.backend.blueprints.main import main

import json
from server.backend.database.users import UsersTable
from server.backend.database.statblocks import StatblocksTable
from server.backend.database.locations import LocationsTable
from server.backend.database.campaigns import CampaignsTable
from server.backend.database.generation import MapGenerationTable
from src.combat.map.generator.dynamic_room_region import DynamicRoomRegion

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

@main.route('/admin/debug-generate-room', methods=['POST'])
def debug_generate_room():
    data = request.get_json()
    width_a = data.get('width_a')
    height_a = data.get('height_a')
    width_b = data.get('width_b')
    height_b = data.get('height_b')

    return jsonify({
        "status": "success",
        "message": "Room generated successfully",
        "room_data": DynamicRoomRegion.debug_generate_room(width_a, height_a, width_b, height_b)
    }), 200

@main.route('/admin/precompute-room-configs', methods=['POST'])
def precompute_room_configs():
    data = request.get_json()
    min_length = data.get('min_length')
    max_length = data.get('max_length')
    min_width = data.get('min_width')
    max_width = data.get('max_width')
    min_back_t_length = data.get('min_back_t_length')
    max_back_t_length = data.get('max_back_t_length')
    min_back_t_width = data.get('min_back_t_width')
    max_back_t_width = data.get('max_back_t_width')
    min_back_t_offset = data.get('min_back_t_offset')
    max_back_t_offset = data.get('max_back_t_offset')
    min_front_t_length = data.get('min_front_t_length')
    max_front_t_length = data.get('max_front_t_length')
    min_front_t_width = data.get('min_front_t_width')
    max_front_t_width = data.get('max_front_t_width')
    min_front_t_offset = data.get('min_front_t_offset')
    max_front_t_offset = data.get('max_front_t_offset')

    regions = []
    for length in range(min_length, max_length + 1):
        for width in range(min_width, max_width + 1):
            for back_t_length in range(min_back_t_length, max_back_t_length + 1):
                for back_t_width in range(min_back_t_width, max_back_t_width + 1):
                    for back_t_offset in range(min_back_t_offset, max_back_t_offset + 1):
                        for front_t_length in range(min_front_t_length, max_front_t_length + 1):
                            for front_t_width in range(min_front_t_width, max_front_t_width + 1):
                                for front_t_offset in range(min_front_t_offset, max_front_t_offset + 1):
                                    try:
                                        regions.append(DynamicRoomRegion(
                                            length, width, back_t_length, back_t_width, back_t_offset,
                                            front_t_length, front_t_width, front_t_offset
                                        ))
                                    except ValueError:
                                        continue
    
    map_generation_table = MapGenerationTable()
    map_generation_table.reset_room_region_configurations()
    remaining = len(regions)
    for i in range(remaining):
        region = regions[i]
        print(f"Processing region {region.hash} ({remaining} remaining)")
        for j in range(i, len(regions)):
            other = regions[j]
            offsets = region.compute_configuration_offsets(other)
            if len(offsets) > 0:
                map_generation_table.bulk_insert_room_region_config(region.hash, other.hash, offsets)
        remaining -= 1
    map_generation_table.commit()

    return jsonify({
        "status": "success",
        "message": f"Precomputed {len(regions)} room configurations"
    }), 200
                        