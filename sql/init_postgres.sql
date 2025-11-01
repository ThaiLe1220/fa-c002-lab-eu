-- PostgreSQL initialization for mid-course test demo
-- Minimal setup for Adjust realtime data landing

CREATE SCHEMA IF NOT EXISTS raw;

-- Simple table for Adjust realtime data (mirrors Snowflake structure)
CREATE TABLE IF NOT EXISTS raw.adjust_realtime (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL,
    day DATE NOT NULL,
    store_id VARCHAR(255) NOT NULL,
    country_code VARCHAR(50),
    os_name VARCHAR(50),
    installs INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    daus INTEGER DEFAULT 0,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA raw TO midtest_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA raw TO midtest_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA raw TO midtest_user;
