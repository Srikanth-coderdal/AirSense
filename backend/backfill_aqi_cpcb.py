import logging
import sys
from collections import deque
from pathlib import Path
from typing import List, Tuple

# Ensure root AirSense is on path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend.database import get_db_cursor
from backend.cpcb_aqi import calculate_cpcb_aqi, calculate_rolling_average

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AQIBackfill")


def backfill_station(station_id: str):
    logger.info(f"Starting backfill for station: {station_id}")

    # Fetch all records for station ordered by time
    select_query = """
        SELECT time, pm25, pm10, no2, so2, co, o3
        FROM measurements
        WHERE station_id = %s
        ORDER BY time ASC;
    """

    with get_db_cursor() as cur:
        cur.execute(select_query, (station_id,))
        rows = cur.fetchall()

    logger.info(f"Loaded {len(rows)} records for {station_id}.")

    # 24-hour window deques (min 16 observations)
    win_pm25 = deque(maxlen=24)
    win_pm10 = deque(maxlen=24)
    win_no2 = deque(maxlen=24)
    win_so2 = deque(maxlen=24)

    # 8-hour window deques (min 6 observations)
    win_co = deque(maxlen=8)
    win_o3 = deque(maxlen=8)

    updates: List[Tuple[int, object, str]] = []

    for r in rows:
        row_time = r["time"]
        pm25_val = r["pm25"]
        pm10_val = r["pm10"]
        no2_val = r["no2"]
        so2_val = r["so2"]
        co_val = r["co"] / 1000.0 if r["co"] is not None else None  # ug/m3 to mg/m3
        o3_val = r["o3"]

        win_pm25.append(pm25_val)
        win_pm10.append(pm10_val)
        win_no2.append(no2_val)
        win_so2.append(so2_val)
        win_co.append(co_val)
        win_o3.append(o3_val)

        # 24h rolling averages (min 16)
        avg_pm25 = calculate_rolling_average(list(win_pm25), min_count=16)
        avg_pm10 = calculate_rolling_average(list(win_pm10), min_count=16)
        avg_no2 = calculate_rolling_average(list(win_no2), min_count=16)
        avg_so2 = calculate_rolling_average(list(win_so2), min_count=16)

        # 8h rolling averages (min 6)
        avg_co = calculate_rolling_average(list(win_co), min_count=6)
        avg_o3 = calculate_rolling_average(list(win_o3), min_count=6)

        aqi_cpcb = calculate_cpcb_aqi(
            pm25=avg_pm25,
            pm10=avg_pm10,
            no2=avg_no2,
            so2=avg_so2,
            co=avg_co,
            o3=avg_o3,
        )

        updates.append((aqi_cpcb, row_time, station_id))

    logger.info(f"Computed {len(updates)} AQI values for {station_id}. Updating database...")

    # Batch update in chunks of 1000
    batch_size = 1000
    update_sql = """
        UPDATE measurements AS m
        SET aqi_cpcb = u.aqi_cpcb
        FROM (VALUES %s) AS u(aqi_cpcb, time, station_id)
        WHERE m.time = u.time AND m.station_id = u.station_id;
    """

    from psycopg2.extras import execute_values

    with get_db_cursor(commit=True) as cur:
        for i in range(0, len(updates), batch_size):
            chunk = updates[i:i + batch_size]
            execute_values(
                cur,
                """
                UPDATE measurements AS m
                SET aqi_cpcb = v.aqi_cpcb
                FROM (VALUES %s) AS v(aqi_cpcb, time, station_id)
                WHERE m.time = v.time AND m.station_id = v.station_id
                """,
                chunk,
                template="(%s, %s, %s)",
            )

    logger.info(f"Finished backfill for {station_id}.")


def run_backfill():
    with get_db_cursor() as cur:
        cur.execute("SELECT station_id FROM stations ORDER BY station_id ASC;")
        stations = [r["station_id"] for r in cur.fetchall()]

    logger.info(f"Found stations: {stations}")
    for sid in stations:
        backfill_station(sid)
    logger.info("All stations backfilled successfully.")


if __name__ == "__main__":
    run_backfill()
