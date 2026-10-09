from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class Station(BaseModel):
    station_id: str
    name: str
    city: str
    state: Optional[str] = None
    lat: float
    lon: float

    model_config = ConfigDict(from_attributes=True)


class Measurement(BaseModel):
    time: datetime
    station_id: str
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    no2: Optional[float] = None
    so2: Optional[float] = None
    co: Optional[float] = None
    o3: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    aqi: Optional[int] = None
    aqi_cpcb: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class TrendRecord(BaseModel):
    bucket: datetime
    avg_pm25: Optional[float] = None
    avg_pm10: Optional[float] = None
    avg_aqi: Optional[float] = None
    min_aqi: Optional[int] = None
    max_aqi: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ComplianceRecord(BaseModel):
    record_id: str
    title: str
    authority: str
    category: Optional[str] = None
    details: Optional[str] = None
    penalty_inr: Optional[float] = None
    status: str
    issue_date: date
    city: str
    lat: float
    lon: float

    model_config = ConfigDict(from_attributes=True)


class Recommendation(BaseModel):
    aqi_category: str
    health_impact: str
    cautionary_advice: str
    action_steps: List[str]

    model_config = ConfigDict(from_attributes=True)


class ForecastItem(BaseModel):
    forecast_time: datetime
    predicted_aqi: int

    model_config = ConfigDict(from_attributes=True)

