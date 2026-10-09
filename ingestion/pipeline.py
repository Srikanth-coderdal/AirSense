import os
import sys
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Any, List

import requests
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("AirSensePipeline")

# 1. Setup & Connection: Load environment variables
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

from backend.cpcb_aqi import calculate_cpcb_aqi, calculate_rolling_average

DB_NAME = os.getenv("POSTGRES_DB", "airquality_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres_secure_pass")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")


def get_db_connection():
    """Establish and return a connection to PostgreSQL."""
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )


# 2. Station Seeding
STATIONS: Dict[str, Dict[str, Any]] = {
    "delhi": {
        "station_id": "delhi",
        "name": "Delhi Central Monitoring Station",
        "city": "Delhi",
        "state": "Delhi",
        "lat": 28.6139,
        "lon": 77.2090,
        "source": "Open-Meteo"
    },
    "mumbai": {
        "station_id": "mumbai",
        "name": "Mumbai Coastal Monitoring Station",
        "city": "Mumbai",
        "state": "Maharashtra",
        "lat": 19.0760,
        "lon": 72.8777,
        "source": "Open-Meteo"
    },
    "bengaluru": {
        "station_id": "bengaluru",
        "name": "Bengaluru Urban Monitoring Station",
        "city": "Bengaluru",
        "state": "Karnataka",
        "lat": 12.9716,
        "lon": 77.5946,
        "source": "Open-Meteo"
    },
    "chennai": {
        "station_id": "chennai",
        "name": "Chennai City Monitoring Station",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "lat": 13.0827,
        "lon": 80.2707,
        "source": "Open-Meteo"
    },
    "kolkata": {
        "station_id": "kolkata",
        "name": "Kolkata Central Monitoring Station",
        "city": "Kolkata",
        "state": "West Bengal",
        "lat": 22.5726,
        "lon": 88.3639,
        "source": "Open-Meteo"
    }
}


def insert_stations(conn):
    """
    Seed initial stations into the stations table using PostGIS geometry.
    Uses ON CONFLICT (station_id) DO NOTHING for idempotency.
    """
    query = """
        INSERT INTO stations (station_id, name, city, state, source, geom)
        VALUES (%s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
        ON CONFLICT (station_id) DO NOTHING;
    """
    with conn.cursor() as cur:
        for s in STATIONS.values():
            cur.execute(query, (
                s["station_id"],
                s["name"],
                s["city"],
                s["state"],
                s["source"],
                s["lon"],
                s["lat"]
            ))
        conn.commit()
    logger.info("Stations verified/seeded successfully.")


# 4. Idempotent Inserts
def upsert_measurements(conn, data: List[Dict[str, Any]]):
    """
    Bulk insert/update time-series measurements into the measurements table.
    Uses psycopg2.extras.execute_values with ON CONFLICT DO UPDATE.
    """
    if not data:
        logger.info("No measurements provided to upsert.")
        return

    query = """
        INSERT INTO measurements (
            time, station_id, pm25, pm10, no2, so2, co, o3, temperature, humidity, wind_speed, aqi, aqi_cpcb
        )
        VALUES %s
        ON CONFLICT (time, station_id) DO UPDATE SET
            pm25 = EXCLUDED.pm25,
            pm10 = EXCLUDED.pm10,
            no2 = EXCLUDED.no2,
            so2 = EXCLUDED.so2,
            co = EXCLUDED.co,
            o3 = EXCLUDED.o3,
            temperature = EXCLUDED.temperature,
            humidity = EXCLUDED.humidity,
            wind_speed = EXCLUDED.wind_speed,
            aqi = EXCLUDED.aqi,
            aqi_cpcb = COALESCE(EXCLUDED.aqi_cpcb, measurements.aqi_cpcb);
    """

    records = [
        (
            d.get("time"),
            d.get("station_id"),
            d.get("pm25"),
            d.get("pm10"),
            d.get("no2"),
            d.get("so2"),
            d.get("co"),
            d.get("o3"),
            d.get("temperature"),
            d.get("humidity"),
            d.get("wind_speed"),
            d.get("aqi"),
            d.get("aqi_cpcb"),
        )
        for d in data
    ]

    with conn.cursor() as cur:
        execute_values(cur, query, records, template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", page_size=1000)
        conn.commit()
    logger.info(f"Successfully upserted {len(records)} measurements.")


# 3. Historical Backfill (Open-Meteo)
def fetch_open_meteo_historical(lat: float, lon: float, start_date: str, end_date: str) -> Dict[str, Dict[str, Any]]:
    """
    Fetch historical weather and air quality from Open-Meteo archive APIs and merge by ISO timestamp.
    """
    weather_url = "https://archive-api.open-meteo.com/v1/archive"
    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "timezone": "UTC"
    }

    aq_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    aq_params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "pm2_5,pm10,nitrogen_dioxide,sulphur_dioxide,carbon_monoxide,ozone,us_aqi",
        "timezone": "UTC"
    }

    merged_by_time: Dict[str, Dict[str, Any]] = {}

    try:
        w_res = requests.get(weather_url, params=weather_params, timeout=30)
        w_res.raise_for_status()
        w_json = w_res.json()
        w_hourly = w_json.get("hourly", {})
        w_times = w_hourly.get("time", [])
        w_temp = w_hourly.get("temperature_2m", [])
        w_hum = w_hourly.get("relative_humidity_2m", [])
        w_wind = w_hourly.get("wind_speed_10m", [])

        for idx, t in enumerate(w_times):
            merged_by_time[t] = {
                "time": t,
                "temperature": w_temp[idx] if idx < len(w_temp) else None,
                "humidity": w_hum[idx] if idx < len(w_hum) else None,
                "wind_speed": w_wind[idx] if idx < len(w_wind) else None,
            }
    except Exception as e:
        logger.error(f"Failed to fetch historical weather data for ({lat}, {lon}): {e}")

    try:
        aq_res = requests.get(aq_url, params=aq_params, timeout=30)
        aq_res.raise_for_status()
        aq_json = aq_res.json()
        aq_hourly = aq_json.get("hourly", {})
        aq_times = aq_hourly.get("time", [])
        aq_pm25 = aq_hourly.get("pm2_5", [])
        aq_pm10 = aq_hourly.get("pm10", [])
        aq_no2 = aq_hourly.get("nitrogen_dioxide", [])
        aq_so2 = aq_hourly.get("sulphur_dioxide", [])
        aq_co = aq_hourly.get("carbon_monoxide", [])
        aq_o3 = aq_hourly.get("ozone", [])
        aq_val = aq_hourly.get("us_aqi", [])

        for idx, t in enumerate(aq_times):
            entry = merged_by_time.setdefault(t, {"time": t})
            entry["pm25"] = aq_pm25[idx] if idx < len(aq_pm25) else None
            entry["pm10"] = aq_pm10[idx] if idx < len(aq_pm10) else None
            entry["no2"] = aq_no2[idx] if idx < len(aq_no2) else None
            entry["so2"] = aq_so2[idx] if idx < len(aq_so2) else None
            entry["co"] = aq_co[idx] if idx < len(aq_co) else None
            entry["o3"] = aq_o3[idx] if idx < len(aq_o3) else None
            entry["aqi"] = int(aq_val[idx]) if idx < len(aq_val) and aq_val[idx] is not None else None
    except Exception as e:
        logger.error(f"Failed to fetch historical air quality data for ({lat}, {lon}): {e}")

    return merged_by_time


def backfill_historical_data(conn, days: int = 180):
    """
    Backfill historical weather and air quality for each station for the given number of days.
    """
    now = datetime.now(timezone.utc)
    end_date = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    start_date = (now - timedelta(days=days)).strftime("%Y-%m-%d")

    logger.info(f"Starting historical backfill from {start_date} to {end_date} ({days} days)...")

    for station_id, info in STATIONS.items():
        logger.info(f"Backfilling station {station_id} ({info['city']})...")
        merged = fetch_open_meteo_historical(info["lat"], info["lon"], start_date, end_date)

        measurements = []
        for t, values in merged.items():
            dt = datetime.fromisoformat(t).replace(tzinfo=timezone.utc) if "T" in t else datetime.strptime(t, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            values["time"] = dt
            values["station_id"] = station_id
            measurements.append(values)

        if measurements:
            upsert_measurements(conn, measurements)
            logger.info(f"Backfilled {len(measurements)} records for {station_id}.")
        else:
            logger.warning(f"No records fetched for station {station_id}.")


# 5. Real-Time Fetch & Scheduler
def fetch_latest_data(conn=None):
    """
    Fetch real-time weather and air quality data from Open-Meteo for all stations and upsert into the DB.
    """
    close_conn = False
    if conn is None:
        try:
            conn = get_db_connection()
            close_conn = True
        except Exception as e:
            logger.error(f"Scheduler failed to connect to database: {e}")
            return

    try:
        all_measurements = []
        for station_id, info in STATIONS.items():
            weather_url = "https://api.open-meteo.com/v1/forecast"
            weather_params = {
                "latitude": info["lat"],
                "longitude": info["lon"],
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
                "timezone": "UTC"
            }

            aq_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
            aq_params = {
                "latitude": info["lat"],
                "longitude": info["lon"],
                "current": "pm2_5,pm10,nitrogen_dioxide,sulphur_dioxide,carbon_monoxide,ozone,us_aqi",
                "timezone": "UTC"
            }

            weather_current = {}
            try:
                w_res = requests.get(weather_url, params=weather_params, timeout=15)
                w_res.raise_for_status()
                weather_current = w_res.json().get("current", {})
            except Exception as e:
                logger.error(f"Error fetching current weather for {station_id}: {e}")

            aq_current = {}
            try:
                aq_res = requests.get(aq_url, params=aq_params, timeout=15)
                aq_res.raise_for_status()
                aq_current = aq_res.json().get("current", {})
            except Exception as e:
                logger.error(f"Error fetching current air quality for {station_id}: {e}")

            time_str = aq_current.get("time") or weather_current.get("time")
            if time_str:
                dt = datetime.fromisoformat(time_str).replace(tzinfo=timezone.utc)
            else:
                dt = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)

            aqi_val = aq_current.get("us_aqi")

            # Calculate CPCB AQI using recent rolling window from database
            past_pm25, past_pm10, past_no2, past_so2 = [], [], [], []
            past_co, past_o3 = [], []
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT pm25, pm10, no2, so2, co, o3
                        FROM measurements
                        WHERE station_id = %s AND time >= %s - INTERVAL '24 hours' AND time < %s
                        ORDER BY time ASC;
                        """,
                        (station_id, dt, dt),
                    )
                    recent_rows = cur.fetchall()
                    for r in recent_rows:
                        past_pm25.append(r[0])
                        past_pm10.append(r[1])
                        past_no2.append(r[2])
                        past_so2.append(r[3])
                        past_co.append(r[4] / 1000.0 if r[4] is not None else None)
                        past_o3.append(r[5])
            except Exception as e:
                logger.warning(f"Could not load recent historical data for {station_id}: {e}")

            # Append current observation
            curr_pm25 = aq_current.get("pm2_5")
            curr_pm10 = aq_current.get("pm10")
            curr_no2 = aq_current.get("nitrogen_dioxide")
            curr_so2 = aq_current.get("sulphur_dioxide")
            curr_co = aq_current.get("carbon_monoxide")
            curr_co_mg = curr_co / 1000.0 if curr_co is not None else None
            curr_o3 = aq_current.get("ozone")

            past_pm25.append(curr_pm25)
            past_pm10.append(curr_pm10)
            past_no2.append(curr_no2)
            past_so2.append(curr_so2)
            past_co.append(curr_co_mg)
            past_o3.append(curr_o3)

            # Rolling averages: 24h (min 16) and 8h (min 6)
            avg_pm25 = calculate_rolling_average(past_pm25[-24:], min_count=16)
            avg_pm10 = calculate_rolling_average(past_pm10[-24:], min_count=16)
            avg_no2 = calculate_rolling_average(past_no2[-24:], min_count=16)
            avg_so2 = calculate_rolling_average(past_so2[-24:], min_count=16)
            avg_co = calculate_rolling_average(past_co[-8:], min_count=6)
            avg_o3 = calculate_rolling_average(past_o3[-8:], min_count=6)

            aqi_cpcb_val = calculate_cpcb_aqi(
                pm25=avg_pm25,
                pm10=avg_pm10,
                no2=avg_no2,
                so2=avg_so2,
                co=avg_co,
                o3=avg_o3,
            )

            record = {
                "time": dt,
                "station_id": station_id,
                "pm25": curr_pm25,
                "pm10": curr_pm10,
                "no2": curr_no2,
                "so2": curr_so2,
                "co": curr_co,
                "o3": curr_o3,
                "temperature": weather_current.get("temperature_2m"),
                "humidity": weather_current.get("relative_humidity_2m"),
                "wind_speed": weather_current.get("wind_speed_10m"),
                "aqi": int(aqi_val) if aqi_val is not None else None,
                "aqi_cpcb": aqi_cpcb_val,
            }
            all_measurements.append(record)

        if all_measurements:
            upsert_measurements(conn, all_measurements)
            logger.info(f"Hourly fetch completed. Upserted {len(all_measurements)} current station records.")
    except Exception as e:
        logger.error(f"Error in fetch_latest_data: {e}")
    finally:
        if close_conn and conn:
            conn.close()


if __name__ == "__main__":
    logger.info("Initializing AirSense Ingestion Pipeline...")
    try:
        db_conn = get_db_connection()
    except Exception as err:
        logger.error(f"Failed to connect to database: {err}")
        sys.exit(1)

    try:
        # Step 1: Insert seed stations
        insert_stations(db_conn)

        # Step 2: Backfill historical data (180 days)
        backfill_historical_data(db_conn, days=180)
    finally:
        db_conn.close()

    # Step 3: Run scheduler every hour
    scheduler = BlockingScheduler()
    scheduler.add_job(fetch_latest_data, "interval", hours=1, next_run_time=datetime.now())
    logger.info("Starting scheduler to fetch real-time data every hour. Press Ctrl+C to exit.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
