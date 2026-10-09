import React, { useState, useEffect } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  ReferenceLine,
} from 'recharts';
import { Sparkles, Info, AlertTriangle, Loader2 } from 'lucide-react';
import airSenseApi from '../api/airSenseApi';

// Formats timestamp into compact time & date representation for forecast timeline
function formatForecastTime(timeStr) {
  if (!timeStr) return '';
  const d = new Date(timeStr);
  return `${d.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' })} ${d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: false })}`;
}

// Custom light tooltip renderer for forecast and observed air quality
function CustomForecastTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border border-slate-200 p-3 rounded-lg shadow-lg text-xs space-y-1.5 text-slate-800">
        <p className="font-semibold text-slate-900 border-b border-slate-100 pb-1 mb-1">
          {formatForecastTime(label)}
        </p>
        {payload.map((entry, index) => {
          if (entry.value === null || entry.value === undefined) return null;
          return (
            <div key={`entry-${index}`} className="flex items-center justify-between gap-4">
              <span style={{ color: entry.color }} className="flex items-center gap-1.5 font-medium">
                <span
                  className="w-2 h-2 rounded-full inline-block"
                  style={{ backgroundColor: entry.color }}
                ></span>
                {entry.name}:
              </span>
              <span className="font-mono font-bold text-slate-900">
                {entry.value}
              </span>
            </div>
          );
        })}
      </div>
    );
  }
  return null;
}

// Renders forecast chart combining observed history and ML predictions across any monitoring station
export default function ForecastChart({
  combinedData: propCombinedData = [],
  stationId,
  stationName,
  isLoading: propIsLoading,
  error: propError,
  cutoffTime,
}) {
  const [internalData, setInternalData] = useState([]);
  const [internalLoading, setInternalLoading] = useState(false);
  const [internalError, setInternalError] = useState(null);

  // Data-fetching hook calling airSenseApi.getForecast(stationId, 24) on stationId change
  useEffect(() => {
    if (!stationId) return;
    if (propCombinedData && propCombinedData.length > 0) return;

    let isMounted = true;
    setInternalLoading(true);
    setInternalError(null);

    airSenseApi.getForecast(stationId, 24)
      .then((items) => {
        if (isMounted) {
          const chartItems = items.map((item) => ({
            time: item.forecast_time,
            observedAqi: null,
            predictedAqi: item.predicted_aqi,
          }));
          setInternalData(chartItems);
          setInternalError(null);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setInternalError(err.message || `Forecast model for station '${stationId}' not found.`);
          setInternalData([]);
        }
      })
      .finally(() => {
        if (isMounted) {
          setInternalLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [stationId, propCombinedData]);

  const activeLoading = propIsLoading !== undefined ? propIsLoading : internalLoading;
  const activeError = propError !== undefined ? propError : internalError;
  const activeData = (propCombinedData && propCombinedData.length > 0) ? propCombinedData : internalData;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow flex flex-col h-[400px]">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-rose-50 text-rose-600 rounded-lg">
            <Sparkles className="w-4 h-4" />
          </div>
          <h3 className="text-base font-semibold text-slate-900 tracking-tight">
            24-Hour AQI Forecast — {stationName || 'Selected Station'}
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200 font-medium">
            CPCB AQI Metric
          </span>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="flex-1 w-full relative">
        {activeLoading ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 text-sm gap-2">
            <Loader2 className="w-8 h-8 text-rose-500 animate-spin" />
            <span className="text-xs text-slate-500 font-medium">Generating ML forecast roll-forward...</span>
          </div>
        ) : activeError ? (
          <div className="h-full flex flex-col items-center justify-center text-rose-500 text-xs px-6 text-center gap-2">
            <div className="p-2.5 bg-rose-50 text-rose-600 rounded-full border border-rose-100">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <p className="font-semibold text-slate-800 text-sm">Forecast Unavailable</p>
            <p className="text-slate-500 max-w-md">{activeError}</p>
          </div>
        ) : activeData.length === 0 ? (
          <div className="h-full flex items-center justify-center text-slate-400 text-sm">
            No forecast data available.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
              data={activeData}
              margin={{ top: 10, right: 20, left: 0, bottom: 20 }}
            >
              <defs>
                <linearGradient id="observedGradLight" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0284c7" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#0284c7" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="predictedGradLight" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#e11d48" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#e11d48" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis
                dataKey="time"
                tickFormatter={(val) => {
                  const d = new Date(val);
                  return `${d.getHours()}:00`;
                }}
                stroke="#64748B"
                tick={{ fontSize: 12, fill: '#64748B' }}
                tickLine={false}
              />
              <YAxis
                stroke="#64748B"
                tick={{ fontSize: 12, fill: '#64748B' }}
                tickLine={false}
                label={{
                  value: 'AQI (CPCB)',
                  angle: -90,
                  position: 'insideLeft',
                  fill: '#64748B',
                  fontSize: 11,
                  offset: 10,
                }}
              />
              <Tooltip content={<CustomForecastTooltip />} />
              <Legend
                wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }}
                iconType="circle"
              />
              {cutoffTime && (
                <ReferenceLine
                  x={cutoffTime}
                  stroke="#e11d48"
                  strokeDasharray="4 4"
                  label={{
                    value: 'Forecast Horizon →',
                    fill: '#e11d48',
                    fontSize: 11,
                    position: 'top',
                  }}
                />
              )}
              {/* Observed Part (Solid Cyan Line & Fill) */}
              <Area
                type="monotone"
                dataKey="observedAqi"
                name="Observed AQI (CPCB)"
                stroke="#0284c7"
                strokeWidth={2.2}
                fill="url(#observedGradLight)"
                dot={{ r: 2.5, fill: '#0284c7' }}
                activeDot={{ r: 4 }}
              />
              {/* Predicted Part (Dashed Rose Line & Fill) */}
              <Area
                type="monotone"
                dataKey="predictedAqi"
                name="Forecast AQI (CPCB)"
                stroke="#e11d48"
                strokeDasharray="5 5"
                strokeWidth={2.2}
                fill="url(#predictedGradLight)"
                dot={{ r: 2.5, fill: '#e11d48' }}
                activeDot={{ r: 4 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Footer labels */}
      <div className="mt-2 pt-2 border-t border-slate-100 flex flex-col sm:flex-row items-start sm:items-center justify-between text-xs text-slate-500 gap-1">
        <span className="flex items-center gap-1.5 font-medium">
          <Info className="w-3.5 h-3.5 text-slate-400 inline shrink-0" />
          Modeled data (Open-Meteo)
        </span>
        <span className="text-rose-600 font-medium">
          24h Recursive Roll-Forward Forecast (XGBoost)
        </span>
      </div>
    </div>
  );
}
