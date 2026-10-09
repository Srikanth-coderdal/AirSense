import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import StationMap from './components/StationMap';
import DateRangePicker from './components/DateRangePicker';
import TrendChart from './components/TrendChart';
import ForecastChart from './components/ForecastChart';
import CompliancePanel from './components/CompliancePanel';
import RecommendationCard from './components/RecommendationCard';
import airSenseApi, {
  fetchStations,
  fetchMeasurements,
  fetchTrends,
  fetchCompliance,
  fetchRecommendations,
  fetchForecast,
  getForecast,
} from './api/airSenseApi';

// Root AirSense dashboard application managing state and coordinating API interactions
export default function App() {
  // Global selection state
  const [stations, setStations] = useState([]);
  const [selectedStation, setSelectedStation] = useState(null);
  const [clickedCoords, setClickedCoords] = useState(null);

  // Analysis window date range state
  const [startDate, setStartDate] = useState('2026-09-08');
  const [endDate, setEndDate] = useState('2026-10-08');

  // Trend data state
  const [trends, setTrends] = useState([]);
  const [isTrendsLoading, setIsTrendsLoading] = useState(false);
  const [trendsError, setTrendsError] = useState(null);

  // Measurements & AQI state (aqi_cpcb)
  const [latestMeasurement, setLatestMeasurement] = useState(null);
  const [currentAqiCpcb, setCurrentAqiCpcb] = useState(null);
  const [recentMeasurements, setRecentMeasurements] = useState([]);

  // Forecast state
  const [forecastItems, setForecastItems] = useState([]);
  const [isForecastLoading, setIsForecastLoading] = useState(false);
  const [forecastError, setForecastError] = useState(null);

  // Recommendation state
  const [recommendation, setRecommendation] = useState(null);
  const [isRecLoading, setIsRecLoading] = useState(false);
  const [recError, setRecError] = useState(null);

  // Compliance state
  const [complianceRecords, setComplianceRecords] = useState([]);
  const [complianceRadius, setComplianceRadius] = useState(50);
  const [isComplianceLoading, setIsComplianceLoading] = useState(false);
  const [complianceError, setComplianceError] = useState(null);

  // Refresh status
  const [isRefreshing, setIsRefreshing] = useState(false);

  // 1. Initial stations load
  useEffect(() => {
    async function loadStations() {
      try {
        const data = await fetchStations();
        setStations(data);
        if (data.length > 0) {
          // Default to Delhi or first station
          const defaultStation = data.find((s) => s.station_id === 'delhi') || data[0];
          setSelectedStation(defaultStation);
          setClickedCoords({ lat: defaultStation.lat, lon: defaultStation.lon });
        }
      } catch (err) {
        console.error('Error fetching stations:', err);
      }
    }
    loadStations();
  }, []);

  // 2. Load measurements with start parameter to obtain aqi_cpcb and recent history
  const loadMeasurementsAndAdvisory = useCallback(async (stationId) => {
    if (!stationId) return;
    setIsRecLoading(true);
    setRecError(null);
    try {
      // Fetch recent 48 hours history with a start parameter
      // Anchor matches available measurements dataset
      const startTime = new Date('2026-10-06T00:00:00Z');
      const data = await fetchMeasurements(stationId, startTime.toISOString());
      setRecentMeasurements(data);

      if (data && data.length > 0) {
        // Read the most recent record with aqi_cpcb
        const validCpcbRecords = data.filter((m) => m.aqi_cpcb !== null && m.aqi_cpcb !== undefined);
        const latest = validCpcbRecords.length > 0
          ? validCpcbRecords[validCpcbRecords.length - 1]
          : data[data.length - 1];

        setLatestMeasurement(latest);
        const aqiValue = latest.aqi_cpcb !== null && latest.aqi_cpcb !== undefined ? latest.aqi_cpcb : 100;
        setCurrentAqiCpcb(aqiValue);

        // Fetch CPCB recommendation for this specific aqi_cpcb value
        const recData = await fetchRecommendations(aqiValue);
        setRecommendation(recData);
      } else {
        setLatestMeasurement(null);
        setCurrentAqiCpcb(null);
        setRecommendation(null);
      }
    } catch (err) {
      console.error('Error loading measurements:', err);
      setRecError(err.message);
    } finally {
      setIsRecLoading(false);
    }
  }, []);

  // 3. Load trends data from /api/trends for selected station
  const loadTrends = useCallback(async (stationId) => {
    if (!stationId) return;
    setIsTrendsLoading(true);
    setTrendsError(null);
    try {
      const data = await fetchTrends(stationId, '1 day');
      setTrends(data);
    } catch (err) {
      console.error('Error loading trends:', err);
      setTrendsError(err.message);
    } finally {
      setIsTrendsLoading(false);
    }
  }, []);

  // 4. Load forecast data from /api/forecast
  const loadForecast = useCallback(async (stationId) => {
    if (!stationId) return;
    setIsForecastLoading(true);
    setForecastError(null);
    try {
      const data = await airSenseApi.getForecast(stationId, 24);
      setForecastItems(data);
    } catch (err) {
      console.error('Error loading forecast:', err);
      setForecastError(err.message);
      setForecastItems([]);
    } finally {
      setIsForecastLoading(false);
    }
  }, []);

  // 5. Load compliance records from /api/compliance using clicked lat/lon
  const loadCompliance = useCallback(async (coords, radius) => {
    if (!coords) return;
    setIsComplianceLoading(true);
    setComplianceError(null);
    try {
      const data = await fetchCompliance(coords.lat, coords.lon, radius);
      setComplianceRecords(data);
    } catch (err) {
      console.error('Error loading compliance:', err);
      setComplianceError(err.message);
    } finally {
      setIsComplianceLoading(false);
    }
  }, []);

  // Trigger data updates when selectedStation changes
  useEffect(() => {
    if (selectedStation) {
      loadMeasurementsAndAdvisory(selectedStation.station_id);
      loadTrends(selectedStation.station_id);
      loadForecast(selectedStation.station_id);
    }
  }, [selectedStation, loadMeasurementsAndAdvisory, loadTrends, loadForecast]);

  // Trigger compliance reload when clickedCoords or radius changes
  useEffect(() => {
    if (clickedCoords) {
      loadCompliance(clickedCoords, complianceRadius);
    }
  }, [clickedCoords, complianceRadius, loadCompliance]);

  // Handle map selection event (clicks on marker or anywhere on map)
  const handleLocationSelect = ({ coords, station }) => {
    setClickedCoords(coords);
    if (station) {
      setSelectedStation(station);
    }
  };

  // Full manual refresh
  const handleRefresh = async () => {
    setIsRefreshing(true);
    if (selectedStation) {
      await Promise.all([
        loadMeasurementsAndAdvisory(selectedStation.station_id),
        loadTrends(selectedStation.station_id),
        loadForecast(selectedStation.station_id),
        clickedCoords ? loadCompliance(clickedCoords, complianceRadius) : Promise.resolve(),
      ]);
    }
    setIsRefreshing(false);
  };

  // Filter trends within chosen analysis window
  const filteredTrends = trends.filter((item) => {
    if (!item.bucket) return false;
    const bucketDate = item.bucket.split('T')[0];
    return bucketDate >= startDate && bucketDate <= endDate;
  });

  // Combine observed recent measurements and forecast items into continuous timeline
  const combinedForecastData = (() => {
    const list = [];
    let lastObservedTime = null;
    let lastObservedAqi = null;

    // Last 24 observed measurements
    const last24Observed = (recentMeasurements || [])
      .filter((m) => m.aqi_cpcb !== null && m.aqi_cpcb !== undefined)
      .slice(-24);

    last24Observed.forEach((m) => {
      list.push({
        time: m.time,
        observedAqi: m.aqi_cpcb,
        predictedAqi: null,
      });
      lastObservedTime = m.time;
      lastObservedAqi = m.aqi_cpcb;
    });

    // Bridge the gap at the cutoff point
    if (list.length > 0 && forecastItems.length > 0 && lastObservedAqi !== null) {
      list[list.length - 1].predictedAqi = lastObservedAqi;
    }

    // Add forecast predictions
    forecastItems.forEach((f) => {
      list.push({
        time: f.forecast_time,
        observedAqi: null,
        predictedAqi: f.predicted_aqi,
      });
    });

    return {
      data: list,
      cutoffTime: lastObservedTime,
    };
  })();

  return (
    <div className="min-h-screen bg-[#F8F7F4] text-slate-900 flex flex-col font-sans selection:bg-[#0057FF] selection:text-white">
      <Header
        selectedStation={selectedStation}
        clickedCoords={clickedCoords}
        isRefreshing={isRefreshing}
        onRefresh={handleRefresh}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 space-y-6">
        {/* Top Control Bar: Redesigned Date Range Picker */}
        <DateRangePicker
          startDate={startDate}
          endDate={endDate}
          onRangeChange={(start, end) => {
            setStartDate(start);
            setEndDate(end);
          }}
        />

        {/* Section 1: Map & CPCB Recommendation Hero Card */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-7">
            <StationMap
              stations={stations}
              selectedStation={selectedStation}
              clickedCoords={clickedCoords}
              onSelectLocation={handleLocationSelect}
            />
          </div>
          <div className="lg:col-span-5">
            <RecommendationCard
              recommendation={recommendation}
              aqiCpcb={currentAqiCpcb}
              latestMeasurement={latestMeasurement}
              isLoading={isRecLoading}
              error={recError}
            />
          </div>
        </div>

        {/* Section 2: Trend Chart & Forecast Chart */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <TrendChart
              trends={filteredTrends}
              stationName={selectedStation ? selectedStation.name : ''}
              isLoading={isTrendsLoading}
              error={trendsError}
            />
          </div>
          <div>
            <ForecastChart
              combinedData={combinedForecastData.data}
              cutoffTime={combinedForecastData.cutoffTime}
              stationId={selectedStation ? selectedStation.station_id : ''}
              stationName={selectedStation ? selectedStation.name : ''}
              isLoading={isForecastLoading}
              error={forecastError}
            />
          </div>
        </div>

        {/* Section 3: Spatial Compliance & Violations Panel */}
        <div className="w-full">
          <CompliancePanel
            records={complianceRecords}
            locationCoords={clickedCoords}
            radiusKm={complianceRadius}
            onRadiusChange={setComplianceRadius}
            isLoading={isComplianceLoading}
            error={complianceError}
          />
        </div>
      </main>

      <footer className="border-t border-slate-200 bg-white py-4 px-6 text-center text-xs text-slate-500">
        <p>
          AirSense Monitoring Platform • Open-Meteo & Central Pollution Control Board (CPCB) Standard
        </p>
      </footer>
    </div>
  );
}
