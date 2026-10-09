import os
import sys
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any

from dotenv import load_dotenv
import joblib
import numpy as np
import pandas as pd
import psycopg2
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
import xgboost as xgb

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MLTrainer")

# Load environment variables
ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

DB_NAME = os.getenv("POSTGRES_DB", "airquality_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres_secure_pass")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

ACTIVE_STATIONS = ["delhi", "mumbai", "bengaluru", "chennai", "kolkata"]

FEATURE_COLS = [
    "hour",
    "day_of_week",
    "month",
    "aqi_lag_1",
    "aqi_lag_24",
    "aqi_roll_24",
    "temperature",
    "humidity",
    "wind_speed",
]


def fetch_data(station_id: str) -> pd.DataFrame:
    """Connect to PostgreSQL using psycopg2 and load station measurements ordered by time."""
    logger.info(f"Connecting to database to fetch data for station: {station_id}")
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT,
    )
    try:
        query = """
            SELECT time, station_id, pm25, pm10, no2, so2, co, o3,
                   temperature, humidity, wind_speed, aqi, aqi_cpcb
            FROM measurements
            WHERE station_id = %s AND aqi_cpcb IS NOT NULL
            ORDER BY time ASC;
        """
        with conn.cursor() as cur:
            cur.execute(query, (station_id,))
            rows = cur.fetchall()
            col_names = [desc[0] for desc in cur.description]
            df = pd.DataFrame(rows, columns=col_names)
        logger.info(f"Successfully fetched {len(df)} records from database for {station_id}.")
        return df
    finally:
        conn.close()


def engineer_features(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Clean data and create temporal, lag, and rolling features without future data leakage."""
    df = raw_df.copy()

    # Drop rows where aqi_cpcb is null
    df = df.dropna(subset=["aqi_cpcb"]).copy()

    # Parse and ensure correct timestamp ordering
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)

    # Extract time features
    df["hour"] = df["time"].dt.hour
    df["day_of_week"] = df["time"].dt.dayofweek
    df["month"] = df["time"].dt.month

    # Create lag features strictly shifted by 1 or more to prevent leakage of target y_t
    df["aqi_lag_1"] = df["aqi_cpcb"].shift(1)
    df["aqi_lag_24"] = df["aqi_cpcb"].shift(24)

    # Rolling mean shifted by 1 so only past observations up to t-1 are included
    df["aqi_roll_24"] = df["aqi_cpcb"].shift(1).rolling(window=24).mean()

    # Drop rows with NaN values caused by initial shifting and rolling windows
    df = df.dropna(subset=["aqi_lag_1", "aqi_lag_24", "aqi_roll_24"]).reset_index(drop=True)
    logger.info(f"Engineered features successfully. Remaining dataset size: {len(df)} rows.")
    return df


def train_test_split_by_time(
    df: pd.DataFrame, test_days: int = 30
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Perform a strict chronological time-based split reserving the last test_days for testing."""
    max_time = df["time"].max()
    cutoff_time = max_time - pd.Timedelta(days=test_days)

    train_df = df[df["time"] < cutoff_time].copy().reset_index(drop=True)
    test_df = df[df["time"] >= cutoff_time].copy().reset_index(drop=True)

    logger.info(
        f"Chronological split (cutoff={cutoff_time}): Train={len(train_df)} rows, Test={len(test_df)} rows"
    )
    return train_df, test_df


def train_xgboost_model(
    train_df: pd.DataFrame, feature_cols: List[str]
) -> xgb.XGBRegressor:
    """Train XGBoost regressor predicting aqi_cpcb on the training partition."""
    logger.info("Training XGBoost regressor on training partition...")
    target_col = "aqi_cpcb"
    x_train = train_df[feature_cols]
    y_train = train_df[target_col]

    model = xgb.XGBRegressor(
        n_estimators=100,
        learning_rate=0.05,
        max_depth=6,
        random_state=42,
    )
    model.fit(x_train, y_train)
    return model


def save_model(
    model: xgb.XGBRegressor, feature_cols: List[str], output_path: Path
) -> None:
    """Save the trained model and feature names to disk using joblib."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "model": model,
        "features": feature_cols,
    }
    joblib.dump(payload, output_path)
    logger.info(f"Saved trained XGBoost model and feature names to {output_path}")


def print_summary_table(metrics: List[Dict[str, Any]]) -> None:
    """Print clean ASCII summary table of evaluation metrics for all stations."""
    print("\n" + "=" * 65)
    print("AirSense XGBoost Multi-Station Evaluation Summary (Test Set)")
    print("=" * 65)
    print(f"{'Station ID':<15} | {'Records (Train/Test)':<22} | {'MAE':<10} | {'RMSE':<10}")
    print("-" * 65)
    for row in metrics:
        records_str = f"{row['train_rows']}/{row['test_rows']}"
        print(
            f"{row['station_id']:<15} | {records_str:<22} | {row['mae']:<10.4f} | {row['rmse']:<10.4f}"
        )
    print("=" * 65 + "\n")


def main():
    """Iterate through all active stations, train XGBoost models, evaluate, and save artifacts."""
    models_dir = Path(__file__).resolve().parent / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    metrics_summary = []

    for station_id in ACTIVE_STATIONS:
        logger.info(f"\n==========================================")
        logger.info(f"Processing station: {station_id}")
        logger.info(f"==========================================")

        # 1. Fetch station data
        raw_df = fetch_data(station_id)
        if raw_df.empty:
            logger.warning(f"No records found for station: {station_id}. Skipping.")
            continue

        # 2. Leakage-free feature engineering
        df = engineer_features(raw_df)

        # 3. Chronological train-test split
        train_df, test_df = train_test_split_by_time(df, test_days=30)

        # 4. Fit XGBoost regressor
        xgb_model = train_xgboost_model(train_df, FEATURE_COLS)

        # 5. Evaluate on held-out test partition
        y_test = test_df["aqi_cpcb"]
        y_pred = xgb_model.predict(test_df[FEATURE_COLS])
        mae = float(mean_absolute_error(y_test, y_pred))
        rmse = float(root_mean_squared_error(y_test, y_pred))

        # 6. Save model artifact to backend/ml/models/xgboost_{station_id}.joblib
        output_path = models_dir / f"xgboost_{station_id}.joblib"
        save_model(xgb_model, FEATURE_COLS, output_path)

        metrics_summary.append({
            "station_id": station_id,
            "train_rows": len(train_df),
            "test_rows": len(test_df),
            "mae": mae,
            "rmse": rmse,
        })

    # Print summary table
    print_summary_table(metrics_summary)


if __name__ == "__main__":
    main()
