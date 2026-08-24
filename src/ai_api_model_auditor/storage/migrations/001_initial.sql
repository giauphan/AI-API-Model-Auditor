-- Migration 001: Initial schema setup for AI API Model Auditor

-- Table to track applied migrations
CREATE TABLE IF NOT EXISTS _migrations (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Providers table
CREATE TABLE IF NOT EXISTS providers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    base_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Models table
CREATE TABLE IF NOT EXISTS models (
    id TEXT PRIMARY KEY,
    provider_id TEXT NOT NULL,
    model_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (provider_id) REFERENCES providers (id)
);

-- Audit runs table
CREATE TABLE IF NOT EXISTS audit_runs (
    id TEXT PRIMARY KEY,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status TEXT NOT NULL,
    configuration JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Test cases table
CREATE TABLE IF NOT EXISTS test_cases (
    id TEXT PRIMARY KEY,
    audit_run_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (audit_run_id) REFERENCES audit_runs (id)
);

-- Observations table
CREATE TABLE IF NOT EXISTS observations (
    id TEXT PRIMARY KEY,
    test_case_id TEXT NOT NULL,
    model_id TEXT NOT NULL,
    probe_type TEXT NOT NULL,
    evidence_data JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_case_id) REFERENCES test_cases (id),
    FOREIGN KEY (model_id) REFERENCES models (id)
);

-- Fingerprints table
CREATE TABLE IF NOT EXISTS fingerprints (
    id TEXT PRIMARY KEY,
    observation_id TEXT NOT NULL,
    feature_name TEXT NOT NULL,
    feature_value TEXT NOT NULL,
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (observation_id) REFERENCES observations (id)
);

-- Scores table
CREATE TABLE IF NOT EXISTS scores (
    id TEXT PRIMARY KEY,
    audit_run_id TEXT NOT NULL,
    model_id TEXT NOT NULL,
    dimension TEXT NOT NULL,
    score_value REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (audit_run_id) REFERENCES audit_runs (id),
    FOREIGN KEY (model_id) REFERENCES models (id)
);

-- Clusters table
CREATE TABLE IF NOT EXISTS clusters (
    id TEXT PRIMARY KEY,
    audit_run_id TEXT NOT NULL,
    cluster_name TEXT NOT NULL,
    members JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (audit_run_id) REFERENCES audit_runs (id)
);

-- Raw artifacts references table
CREATE TABLE IF NOT EXISTS raw_artifacts (
    id TEXT PRIMARY KEY,
    audit_run_id TEXT NOT NULL,
    artifact_type TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    hash_sha256 TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (audit_run_id) REFERENCES audit_runs (id)
);
