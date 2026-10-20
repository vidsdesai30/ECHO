-- ECHO PostgreSQL schema. Apply with a migration tool or psql after creating the database.
CREATE TABLE IF NOT EXISTS investigations (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS imported_events (
    id BIGSERIAL PRIMARY KEY,
    investigation_id VARCHAR(64) NOT NULL REFERENCES investigations(id) ON DELETE CASCADE,
    event_id VARCHAR(256) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_imported_events_investigation_id ON imported_events(investigation_id);
CREATE INDEX IF NOT EXISTS ix_imported_events_event_id ON imported_events(event_id);
CREATE TABLE IF NOT EXISTS experiments (
    id VARCHAR(64) PRIMARY KEY,
    scenario_id VARCHAR(256) NOT NULL,
    seed INTEGER NOT NULL,
    status VARCHAR(32) NOT NULL,
    configuration JSONB NOT NULL,
    metrics JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
