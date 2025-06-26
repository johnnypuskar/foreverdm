CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS sessions (
    session_key VARCHAR(64) PRIMARY KEY NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id),
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires TIMESTAMP DEFAULT CURRENT_TIMESTAMP + INTERVAL '1 day'
);

CREATE TABLE IF NOT EXISTS campaigns (
    id VARCHAR(64) PRIMARY KEY NOT NULL
);

CREATE TABLE IF NOT EXISTS campaign_users (
    campaign_id VARCHAR(64) NOT NULL REFERENCES campaigns(id),
    user_id INTEGER NOT NULL REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS locations (
    id VARCHAR(64) NOT NULL,
    campaign_id VARCHAR(64) NOT NULL REFERENCES campaigns(id),
    name VARCHAR(255) NOT NULL,
    description TEXT DEFAULT NULL,
    map_data JSONB DEFAULT NULL,
    PRIMARY KEY (id, campaign_id)
);

CREATE TABLE IF NOT EXISTS location_adjacencies (
    campaign_id VARCHAR(64) NOT NULL REFERENCES campaigns(id),
    first_location_id VARCHAR(64) NOT NULL,
    second_location_id VARCHAR(64) NOT NULL,
    PRIMARY KEY (campaign_id, first_location_id, second_location_id),
    CONSTRAINT chk_different_locations CHECK (first_location_id <> second_location_id),
    CONSTRAINT fk_first_location FOREIGN KEY (first_location_id, campaign_id) REFERENCES locations (id, campaign_id),
    CONSTRAINT fk_second_location FOREIGN KEY (second_location_id, campaign_id) REFERENCES locations (id, campaign_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS uix_location_adjacencies_pairing ON location_adjacencies
(campaign_id, LEAST(first_location_id, second_location_id), GREATEST(first_location_id, second_location_id));

CREATE TABLE IF NOT EXISTS statblocks (
    id VARCHAR(64) NOT NULL,
    name VARCHAR(255) NOT NULL,
    campaign_id VARCHAR(64) NOT NULL REFERENCES campaigns(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    location_id VARCHAR(64) NOT NULL,
    data JSONB NOT NULL,
    PRIMARY KEY (id, campaign_id),
    CONSTRAINT fk_location_actual FOREIGN KEY (location_id, campaign_id) REFERENCES locations (id, campaign_id)
);

CREATE TYPE act_type AS ENUM (
    'WORLD',
    'COMBAT'
);

CREATE TABLE IF NOT EXISTS paused_instances (
    location_id VARCHAR(64) NOT NULL,
    campaign_id VARCHAR(64) NOT NULL REFERENCES campaigns(id),
    act_type act_type NOT NULL,
    act_data JSONB NOT NULL DEFAULT '{}',
    UNIQUE (location_id, campaign_id),
    CONSTRAINT fk_location_actual FOREIGN KEY (location_id, campaign_id) REFERENCES locations (id, campaign_id)
);

CREATE TABLE IF NOT EXISTS dynamic_room_region_configurations (
    fixed_hash BIGINT NOT NULL,
    relative_hash  BIGINT NOT NULL,
    dx INTEGER NOT NULL,
    dy INTEGER NOT NULL,
    adjacencies INTEGER NOT NULL
);