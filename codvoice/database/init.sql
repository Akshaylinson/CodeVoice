CREATE TABLE voices (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    language VARCHAR(10) NOT NULL,
    model_path VARCHAR(500) NOT NULL,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tts_requests (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    voice VARCHAR(255) NOT NULL,
    latency INTEGER NOT NULL,
    text_length INTEGER NOT NULL,
    audio_length INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL
);

CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    client_name VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    rate_limit INTEGER DEFAULT 1000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO voices (name, language, model_path) VALUES 
('en_US-lessac-medium', 'en_US', '/app/models/en_US-lessac-medium.onnx');

INSERT INTO api_keys (client_name, api_key) VALUES 
('default', 'codvoice-default-key-123');