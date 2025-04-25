-- PostgreSQL schema for manga connector management

-- Drop tables if they exist
DROP TABLE IF EXISTS connector_api_urls CASCADE;
DROP TABLE IF EXISTS connector_status_history CASCADE;
DROP TABLE IF EXISTS connectors CASCADE;

-- Connectors table
CREATE TABLE connectors (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    base_url TEXT NOT NULL,
    tags TEXT[] NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (name)
);

-- Connector status history
CREATE TABLE connector_status_history (
    id SERIAL PRIMARY KEY,
    connector_id INTEGER REFERENCES connectors(id),
    status_code INTEGER,
    response_time FLOAT,
    error_message TEXT,
    successful BOOLEAN NOT NULL,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API URLs for connectors
CREATE TABLE connector_api_urls (
    id SERIAL PRIMARY KEY,
    connector_id INTEGER REFERENCES connectors(id),
    api_url TEXT NOT NULL,
    api_type TEXT NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
