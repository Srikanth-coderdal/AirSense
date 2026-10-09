import logging
import os
from pathlib import Path
import re
from datetime import datetime, timedelta
from typing import List, Optional

import joblib
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from backend.database import get_db_cursor
from backend.schemas import (
    Station,
    Measurement,
    TrendRecord,
    ComplianceRecord,
    Recommendation,
    ForecastItem,
)


logger = logging.getLogger("AirSenseBackend.routes")
router = APIRouter(prefix="/api", tags=["Air Quality & Compliance"])

INTERVAL_REGEX = re.compile(r"^\d+\s+(second|seconds|minute|minutes|hour|hours|day|days|week|weeks|month|months|year|years)$", re.IGNORECASE)


@router.get("/stations", response_model=List[Station])
def get_stations(
    bbox: Optional[str] = Query(
        None,
        description="Bounding box filter in format 'min_lon,min_lat,max_lon,max_lat'",
        example="76.8,28.4,77.5,28.9",
    )
):
    """
    Retrieve stations with extracted longitude and latitude.
    Optionally filters by bounding box using PostGIS ST_Intersects.
    """
    query = """
        SELECT
            station_id,
            name,
            city,
            state,
            ST_Y(geom) AS lat,
            ST_X(geom) AS lon
        FROM stations
    """
    params = []

    if bbox:
        try:
            coords = [float(c.strip()) for c in bbox.split(",")]
            if len(coords) != 4:
                raise ValueError("BBox must contain 4 comma-separated values.")
            min_lon, min_lat, max_lon, max_lat = coords
            query += " WHERE ST_Intersects(geom, ST_MakeEnvelope(%s, %s, %s, %s, 4326))"
            params.extend([min_lon, min_lat, max_lon, max_lat])
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid bbox parameter. Must be min_lon,min_lat,max_lon,max_lat: {e}",
            )

    query += " ORDER BY name ASC;"

    with get_db_cursor() as cur:
        cur.execute(query, tuple(params) if params else None)
        rows = cur.fetchall()
        return [dict(row) for row in rows]


@router.get("/measurements", response_model=List[Measurement])
def get_measurements(
    station_id: Optional[str] = Query(None, description="Station identifier"),
    start: Optional[datetime] = Query(None, description="Start ISO timestamp"),
    end: Optional[datetime] = Query(None, description="End ISO timestamp"),
):
    """
    Retrieve historical measurements ordered by time ASC.
    """
    conditions = []
    params = []

    if station_id:
        conditions.append("station_id = %s")
        params.append(station_id)

    if start:
        conditions.append("time >= %s")
        params.append(start)

    if end:
        conditions.append("time <= %s")
        params.append(end)

    query = """
        SELECT
            time,
            station_id,
            pm25,
            pm10,
            no2,
            so2,
            co,
            o3,
            temperature,
            humidity,
            wind_speed,
            aqi,
            aqi_cpcb
        FROM measurements
    """

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY time ASC LIMIT 5000;"

    with get_db_cursor() as cur:
        cur.execute(query, tuple(params) if params else None)
        rows = cur.fetchall()
        return [dict(row) for row in rows]


@router.get("/trends", response_model=List[TrendRecord])
def get_trends(
    station_id: str = Query(..., description="Target station identifier"),
    interval: str = Query("1 day", description="TimescaleDB time bucket interval (e.g. '1 hour', '1 day', '7 days')"),
):
    """
    Retrieve aggregated measurements using TimescaleDB time_bucket.
    Aggregates CPCB AQI (aqi_cpcb).
    """
    clean_interval = interval.strip()
    if not INTERVAL_REGEX.match(clean_interval):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid interval parameter '{interval}'. Must be format like '1 hour', '1 day', '7 days'.",
        )

    query = """
        SELECT
            time_bucket(%s, time) AS bucket,
            ROUND(AVG(pm25)::numeric, 2) AS avg_pm25,
            ROUND(AVG(pm10)::numeric, 2) AS avg_pm10,
            ROUND(AVG(aqi_cpcb)::numeric, 2) AS avg_aqi,
            MIN(aqi_cpcb) AS min_aqi,
            MAX(aqi_cpcb) AS max_aqi
        FROM measurements
        WHERE station_id = %s
        GROUP BY bucket
        ORDER BY bucket ASC;
    """

    with get_db_cursor() as cur:
        cur.execute(query, (clean_interval, station_id))
        rows = cur.fetchall()
        return [dict(row) for row in rows]


@router.get("/compliance", response_model=List[ComplianceRecord])
def get_compliance_records(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius_km: float = Query(50.0, description="Search radius in kilometers", ge=0.1, le=1000.0),
):
    """
    Retrieve compliance records within a specified radius using PostGIS ST_DWithin.
    """
    query = """
        SELECT
            record_id,
            title,
            authority,
            category,
            details,
            penalty_inr::float AS penalty_inr,
            status,
            issue_date,
            city,
            ST_Y(geom) AS lat,
            ST_X(geom) AS lon
        FROM compliance_records
        WHERE ST_DWithin(
            geom::geography,
            ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
            %s * 1000
        )
        ORDER BY issue_date DESC;
    """

    with get_db_cursor() as cur:
        cur.execute(query, (lon, lat, radius_km))
        rows = cur.fetchall()
        return [dict(row) for row in rows]


@router.get("/recommendations", response_model=Recommendation)
def get_recommendations(
    aqi: int = Query(..., description="Air Quality Index value", ge=0),
):
    """
    Return CPCB categorized air quality health advisory and mitigation action steps.
    """
    if aqi <= 50:
        return Recommendation(
            aqi_category="Good",
            health_impact="Minimal impact. Air quality is considered satisfactory, and air pollution poses little or no risk.",
            cautionary_advice="Enjoy regular outdoor activities. Ideal conditions for exercise and ventilation.",
            action_steps=[
                "Maintain green spaces and urban plants.",
                "Promote walking and non-motorized transport.",
                "Continue standard clean air practices.",
            ],
        )
    elif aqi <= 100:
        return Recommendation(
            aqi_category="Satisfactory",
            health_impact="Minor breathing discomfort to sensitive people (asthmatics, elderly, children).",
            cautionary_advice="Unusually sensitive individuals should monitor symptoms and consider reducing prolonged heavy outdoor exertion.",
            action_steps=[
                "Encourage public transport and carpooling.",
                "Avoid open trash or biomass burning.",
                "Keep vehicle engines regularly tuned.",
            ],
        )
    elif aqi <= 200:
        return Recommendation(
            aqi_category="Moderate",
            health_impact="Breathing discomfort to people with lungs, asthma, and heart diseases.",
            cautionary_advice="Children, older adults, and people with respiratory illness should reduce prolonged or heavy outdoor exertion.",
            action_steps=[
                "Enforce dust suppression at local construction sites with water sprinkling.",
                "Sensitive groups should limit outdoor morning exercise during peak traffic hours.",
                "Avoid unnecessary idling of vehicles at signals.",
            ],
        )
    elif aqi <= 300:
        return Recommendation(
            aqi_category="Poor",
            health_impact="Breathing discomfort to most people on prolonged exposure.",
            cautionary_advice="Wear N95/FFP2 masks when outdoors. Reduce intense outdoor physical activities, particularly near heavy traffic corridors.",
            action_steps=[
                "Deploy mechanical road sweepers and intensive water sprinklers on main arterial roads.",
                "Strictly prohibit open burning of municipal solid waste and agricultural residue.",
                "Use indoor air purifiers in schools and senior care facilities.",
            ],
        )
    elif aqi <= 400:
        return Recommendation(
            aqi_category="Very Poor",
            health_impact="Respiratory illness to the people on prolonged exposure. Pronounced effect on people with lung and heart diseases.",
            cautionary_advice="Avoid morning and late evening outdoor activities. Keep windows closed during peak pollution hours. Vulnerable groups should remain indoors.",
            action_steps=[
                "Implement Graded Response Action Plan (GRAP) Stage-III measures (restrict non-essential construction and diesel generator sets).",
                "Enhance public transit frequency and parking fees to discourage private vehicular movement.",
                "Mandate wet vacuuming and continuous misting at construction sites.",
            ],
        )
    else:
        return Recommendation(
            aqi_category="Severe",
            health_impact="Affects healthy people and seriously impacts those with existing diseases.",
            cautionary_advice="Stay indoors and keep physical activity levels minimal. Seal indoor spaces and operate HEPA air purifiers. Wear certified N95/N99 masks if stepping outdoors is unavoidable.",
            action_steps=[
                "Enforce full emergency measures (halt non-essential industrial operations, ban entry of heavy diesel trucks).",
                "Promote remote work (Work From Home) for non-essential public and corporate offices.",
                "Conduct aerial or high-rise smog gun water atomization in critical hot spots.",
            ],
        )


@router.get("/forecast", response_model=List[ForecastItem])
def get_forecast(
    station_id: str = Query("delhi", description="Station identifier"),
    hours: int = Query(24, ge=1, le=168, description="Forecast horizon in hours"),
):
    """Generate multi-step AQI forecasts using trained XGBoost model and iterative roll-forward."""
    model_path = f"backend/ml/models/xgboost_{station_id.lower()}.joblib"
    if not os.path.exists(model_path):
        alt_path = os.path.join(os.path.dirname(__file__), "ml", "models", f"xgboost_{station_id.lower()}.joblib")
        if os.path.exists(alt_path):
            model_path = alt_path
        else:
            raise HTTPException(
                status_code=404,
                detail="Model not trained for this station",
            )

    try:
        saved_data = joblib.load(model_path)
    except Exception as e:
        logger.error(f"Failed to load model file {model_path}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error loading model for station '{station_id}'.",
        )

    if isinstance(saved_data, dict) and "model" in saved_data:
        model = saved_data["model"]
        feature_cols = saved_data.get(
            "features",
            [
                "hour",
                "day_of_week",
                "month",
                "aqi_lag_1",
                "aqi_lag_24",
                "aqi_roll_24",
                "temperature",
                "humidity",
                "wind_speed",
            ],
        )
    else:
        model = saved_data
        feature_cols = getattr(
            model,
            "feature_names_in_",
            [
                "hour",
                "day_of_week",
                "month",
                "aqi_lag_1",
                "aqi_lag_24",
                "aqi_roll_24",
                "temperature",
                "humidity",
                "wind_speed",
            ],
        )

    # 2. Retrieve most recent 48 hours of data where aqi_cpcb IS NOT NULL
    query = """
        SELECT time, temperature, humidity, wind_speed, aqi_cpcb
        FROM measurements
        WHERE station_id = %s AND aqi_cpcb IS NOT NULL
        ORDER BY time DESC
        LIMIT 48;
    """
    with get_db_cursor() as cur:
        cur.execute(query, (station_id.lower(),))
        rows = cur.fetchall()

    if len(rows) < 24:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient historical data for station '{station_id}' to generate forecast.",
        )

    # Sort chronologically (oldest to newest)
    recent_data = sorted(rows, key=lambda r: r["time"])
    last_row = recent_data[-1]
    last_time = last_row["time"]
    last_temp = last_row["temperature"] if last_row.get("temperature") is not None else 25.0
    last_humidity = last_row["humidity"] if last_row.get("humidity") is not None else 50.0
    last_wind_speed = last_row["wind_speed"] if last_row.get("wind_speed") is not None else 5.0

    aqi_history = [float(r["aqi_cpcb"]) for r in recent_data]
    forecast_results = []

    # 3. Iterative forecasting loop
    for h in range(1, hours + 1):
        next_time = last_time + timedelta(hours=h)

        step_features = {
            "hour": next_time.hour,
            "day_of_week": next_time.weekday(),
            "month": next_time.month,
            "aqi_lag_1": aqi_history[-1],
            "aqi_lag_24": aqi_history[-24],
            "aqi_roll_24": float(np.mean(aqi_history[-24:])),
            "temperature": last_temp,
            "humidity": last_humidity,
            "wind_speed": last_wind_speed,
        }

        input_df = pd.DataFrame([step_features])[feature_cols]
        pred_val = float(model.predict(input_df)[0])
        pred_aqi = max(0, int(round(pred_val)))

        # Append to context and update for subsequent steps
        aqi_history.append(pred_val)

        forecast_results.append({
            "forecast_time": next_time,
            "predicted_aqi": pred_aqi,
        })

    return forecast_results

