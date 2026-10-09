const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Handles API response parsing and throws structured errors when requests fail
async function handleResponse(response, endpointName) {
  if (!response.ok) {
    const errorText = await response.text();
    let message = `Failed to load ${endpointName} (${response.status}): ${errorText}`;
    try {
      const parsed = JSON.parse(errorText);
      if (parsed.detail) {
        message = parsed.detail;
      }
    } catch (_) {}
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }
  return response.json();
}

// Retrieves monitoring stations, optionally filtered by bounding box
export async function fetchStations(bbox = null) {
  const url = new URL(`${API_BASE}/api/stations`);
  if (bbox) {
    url.searchParams.set('bbox', bbox);
  }
  const response = await fetch(url);
  return handleResponse(response, 'stations');
}

// Retrieves historical measurements for a station within an optional time range
export async function fetchMeasurements(stationId = null, start = null, end = null) {
  const url = new URL(`${API_BASE}/api/measurements`);
  if (stationId) {
    url.searchParams.set('station_id', stationId);
  }
  if (start) {
    url.searchParams.set('start', typeof start === 'string' ? start : start.toISOString());
  }
  if (end) {
    url.searchParams.set('end', typeof end === 'string' ? end : end.toISOString());
  }
  const response = await fetch(url);
  return handleResponse(response, 'measurements');
}

// Retrieves aggregated pollution trends for a target station by time bucket
export async function fetchTrends(stationId, interval = '1 day') {
  const url = new URL(`${API_BASE}/api/trends`);
  url.searchParams.set('station_id', stationId);
  url.searchParams.set('interval', interval);
  const response = await fetch(url);
  return handleResponse(response, 'trends');
}

// Retrieves spatial compliance violation records within a radius of given coordinates
export async function fetchCompliance(lat, lon, radiusKm = 50) {
  const url = new URL(`${API_BASE}/api/compliance`);
  url.searchParams.set('lat', lat);
  url.searchParams.set('lon', lon);
  url.searchParams.set('radius_km', radiusKm);
  const response = await fetch(url);
  return handleResponse(response, 'compliance');
}

// Retrieves CPCB health advisory recommendations for an AQI value
export async function fetchRecommendations(aqi) {
  const url = new URL(`${API_BASE}/api/recommendations`);
  url.searchParams.set('aqi', Math.max(0, Math.round(aqi)));
  const response = await fetch(url);
  return handleResponse(response, 'recommendations');
}

// Retrieves ML forecast predictions for a station
export async function fetchForecast(stationId = 'delhi', hours = 24) {
  const url = new URL(`${API_BASE}/api/forecast`);
  url.searchParams.set('station_id', stationId);
  url.searchParams.set('hours', hours);
  const response = await fetch(url);
  return handleResponse(response, 'forecast');
}

export const getForecast = fetchForecast;

export const airSenseApi = {
  fetchStations,
  fetchMeasurements,
  fetchTrends,
  fetchCompliance,
  fetchRecommendations,
  fetchForecast,
  getForecast,
};

export default airSenseApi;
