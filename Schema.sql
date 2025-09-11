-- ===========================
-- Telematics Insurance Schema
-- ===========================

-- Drop existing tables if rerunning
DROP TABLE IF EXISTS telemetry;
DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS drivers;

-- ---------------------------
-- Driver table
-- ---------------------------
CREATE TABLE drivers (
    driver_id TEXT PRIMARY KEY,
    num_trips INTEGER,
    total_miles REAL,
    total_drive_time_min REAL,
    avg_trip_duration_min REAL,
    avg_trip_miles REAL,
    avg_speed_overall REAL,
    max_speed_overall REAL,
    total_harsh_brakes INTEGER,
    total_harsh_accels INTEGER,
    avg_num_harsh_brakes REAL,
    avg_num_harsh_accels REAL,
    night_trip_pct_overall REAL,
    idling_pct_overall REAL,
    urban_pct_overall REAL,
    highway_pct_overall REAL,
    years_driving INTEGER,
    num_claims INTEGER,
    num_violations INTEGER,
    vehicle_age INTEGER,
    vehicle_type TEXT,
    insurance_policy_length_years REAL,
    claims_weighted_score REAL
);

-- ---------------------------
-- Trips table
-- ---------------------------
CREATE TABLE trips (
    trip_id TEXT PRIMARY KEY,
    driver_id TEXT,
    trip_duration_min REAL,
    total_miles REAL,
    avg_speed REAL,
    max_speed REAL,
    num_harsh_brakes INTEGER,
    num_harsh_accels INTEGER,
    idling_pct REAL,
    night_trip_pct REAL,
    urban_pct REAL,
    highway_pct REAL,
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
);

-- ---------------------------
-- Telemetry table
-- ---------------------------
CREATE TABLE telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP,
    trip_id TEXT,
    driver_id TEXT,
    lat REAL,
    lon REAL,
    speed REAL,
    acceleration REAL,
    road_type TEXT,
    engine_on INTEGER,
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id),
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
);
