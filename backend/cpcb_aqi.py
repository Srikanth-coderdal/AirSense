import math
from typing import Optional, List, Dict, Tuple

# Contiguous breakpoints: (conc_lo, conc_hi, aqi_lo, aqi_hi)
# Top open-ended bands use an upper reference concentration and clamp at 500
BREAKPOINTS: Dict[str, List[Tuple[float, float, int, int]]] = {
    "pm25": [
        (0.0, 30.0, 0, 50),
        (30.0, 60.0, 51, 100),
        (60.0, 90.0, 101, 200),
        (90.0, 120.0, 201, 300),
        (120.0, 250.0, 301, 400),
        (250.0, 380.0, 401, 500),
    ],
    "pm10": [
        (0.0, 50.0, 0, 50),
        (50.0, 100.0, 51, 100),
        (100.0, 250.0, 101, 200),
        (250.0, 350.0, 201, 300),
        (350.0, 430.0, 301, 400),
        (430.0, 550.0, 401, 500),
    ],
    "no2": [
        (0.0, 40.0, 0, 50),
        (40.0, 80.0, 51, 100),
        (80.0, 180.0, 101, 200),
        (180.0, 280.0, 201, 300),
        (280.0, 400.0, 301, 400),
        (400.0, 500.0, 401, 500),
    ],
    "so2": [
        (0.0, 40.0, 0, 50),
        (40.0, 80.0, 51, 100),
        (80.0, 380.0, 101, 200),
        (380.0, 800.0, 201, 300),
        (800.0, 1600.0, 301, 400),
        (1600.0, 2000.0, 401, 500),
    ],
    "co": [
        (0.0, 1.0, 0, 50),
        (1.0, 2.0, 51, 100),
        (2.0, 10.0, 101, 200),
        (10.0, 17.0, 201, 300),
        (17.0, 34.0, 301, 400),
        (34.0, 50.0, 401, 500),
    ],
    "o3": [
        (0.0, 50.0, 0, 50),
        (50.0, 100.0, 51, 100),
        (100.0, 168.0, 101, 200),
        (168.0, 208.0, 201, 300),
        (208.0, 748.0, 301, 400),
        (748.0, 1000.0, 401, 500),
    ],
}


def calculate_sub_index(conc: Optional[float], pollutant: str) -> Optional[float]:
    """
    Calculate the sub-index for a single pollutant using linear interpolation.
    Caps sub-index at 500. Returns None if concentration is invalid.
    """
    if conc is None or conc < 0:
        return None

    bands = BREAKPOINTS.get(pollutant)
    if not bands:
        return None

    for conc_lo, conc_hi, aqi_lo, aqi_hi in bands:
        if conc_lo <= conc <= conc_hi:
            if conc_hi == conc_lo:
                return float(aqi_lo)
            sub = aqi_lo + ((aqi_hi - aqi_lo) / (conc_hi - conc_lo)) * (conc - conc_lo)
            return min(float(sub), 500.0)

    # Above highest band: cap at 500
    top_band = bands[-1]
    if conc > top_band[1]:
        return 500.0

    return None


def calculate_rolling_average(values: List[Optional[float]], min_count: int) -> Optional[float]:
    """
    Calculate the mean of valid (non-None) numbers in a rolling window.
    Returns None if fewer than min_count values exist.
    """
    valid = [v for v in values if v is not None]
    if len(valid) < min_count:
        return None
    return sum(valid) / len(valid)


def calculate_cpcb_aqi(
    pm25: Optional[float] = None,
    pm10: Optional[float] = None,
    no2: Optional[float] = None,
    so2: Optional[float] = None,
    co: Optional[float] = None,
    o3: Optional[float] = None,
) -> Optional[int]:
    """
    Calculate the final CPCB AQI from rolling average pollutant concentrations.
    Requirements:
      - At least 3 pollutants available.
      - At least one PM pollutant (pm25 or pm10) available.
      - CO concentration must be in mg/m3.
    Returns:
      Integer AQI capped at 500, or None if minimum requirements not met.
    """
    sub_indices: Dict[str, float] = {}

    for name, val in [
        ("pm25", pm25),
        ("pm10", pm10),
        ("no2", no2),
        ("so2", so2),
        ("co", co),
        ("o3", o3),
    ]:
        idx = calculate_sub_index(val, name)
        if idx is not None:
            sub_indices[name] = idx

    # Rule: Must have at least 3 pollutants
    if len(sub_indices) < 3:
        return None

    # Rule: Must have at least one PM pollutant
    if "pm25" not in sub_indices and "pm10" not in sub_indices:
        return None

    final_aqi = max(sub_indices.values())
    return min(int(round(final_aqi)), 500)
