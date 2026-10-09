-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Stations registry
CREATE TABLE IF NOT EXISTS stations (
    station_id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    source VARCHAR(100),
    geom GEOMETRY(Point, 4326),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stations_geom ON stations USING GIST (geom);

-- Air quality measurements time-series
CREATE TABLE IF NOT EXISTS measurements (
    time TIMESTAMPTZ NOT NULL,
    station_id VARCHAR(64) NOT NULL REFERENCES stations(station_id),
    pm25 DOUBLE PRECISION,
    pm10 DOUBLE PRECISION,
    no2 DOUBLE PRECISION,
    so2 DOUBLE PRECISION,
    co DOUBLE PRECISION,
    o3 DOUBLE PRECISION,
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    wind_speed DOUBLE PRECISION,
    aqi INTEGER,
    PRIMARY KEY (time, station_id)
);

-- Convert measurements to a Timescale hypertable partitioned by 7 days
SELECT create_hypertable('measurements', 'time', chunk_time_interval => INTERVAL '7 days', if_not_exists => TRUE);

-- Environmental compliance records
CREATE TABLE IF NOT EXISTS compliance_records (
    record_id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    authority VARCHAR(150) NOT NULL,
    category VARCHAR(100),
    details TEXT,
    penalty_inr NUMERIC(15, 2),
    status VARCHAR(50) NOT NULL,
    issue_date DATE NOT NULL,
    city VARCHAR(100) NOT NULL,
    geom GEOMETRY(Point, 4326),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_compliance_records_geom ON compliance_records USING GIST (geom);

-- Forecast records time-series
CREATE TABLE IF NOT EXISTS forecasts (
    forecast_time TIMESTAMPTZ NOT NULL,
    station_id VARCHAR(64) NOT NULL REFERENCES stations(station_id),
    model_name VARCHAR(100) NOT NULL,
    predicted_pm25 DOUBLE PRECISION,
    predicted_aqi INTEGER,
    lower_bound DOUBLE PRECISION,
    upper_bound DOUBLE PRECISION,
    generated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (forecast_time, station_id, model_name)
);

-- Convert forecasts to a Timescale hypertable partitioned by 7 days
SELECT create_hypertable('forecasts', 'forecast_time', chunk_time_interval => INTERVAL '7 days', if_not_exists => TRUE);
