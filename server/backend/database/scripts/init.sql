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
    id VARCHAR() PRIMARY KEY NOT NULL
);

CREATE TABLE IF NOT EXISTS campaign_users (
    campaign_id VARCHAR(64) NOT NULL REFERENCES campaigns(id),
    user_id INTEGER NOT NULL REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS locations (
    id VARCHAR(64) NOT NULL,
    campaign_id VARCHAR(64) NOT NULL REFERENCES campaigns(id),
    name VARCHAR(255) NOT NULL,
    map_data JSONB,
    PRIMARY KEY (id, campaign_id)
);

CREATE TABLE IF NOT EXISTS statblocks (
    id VARCHAR(64) NOT NULL,
    name VARCHAR(255) NOT NULL,
    campaign_id VARCHAR(64) NOT NULL REFERENCES campaigns(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    location_id VARCHAR(64) NOT NULL REFERENCES locations(id),
    data JSONB NOT NULL,
    PRIMARY KEY (id, campaign_id)
);

CREATE TYPE instance_type AS ENUM (
    'COMBAT',
    'WORLD',
    'SCRIPTED'
);

CREATE TABLE IF NOT EXISTS paused_instances (
    location_id VARCHAR(64) NOT NULL REFERENCES locations(id),
    campaign_id VARCHAR(64) NOT NULL REFERENCES campaigns(id),
    type instance_type NOT NULL,
    UNIQUE (location_id, campaign_id)
);