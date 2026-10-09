import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';
import { TrendingUp, Info } from 'lucide-react';

// Formats ISO bucket date into readable label for chart axes and tooltips
function formatBucketDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' });
}

// Custom light tooltip renderer for pollution trend chart
function CustomTrendTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border border-slate-200 p-3 rounded-lg shadow-lg text-xs space-y-1.5 text-slate-800">
        <p className="font-semibold text-slate-900 border-b border-slate-100 pb-1 mb-1">
          {formatBucketDate(label)}
        </p>
        {payload.map((entry, index) => (
          <div key={`item-${index}`} className="flex items-center justify-between gap-4">
            <span style={{ color: entry.color }} className="flex items-center gap-1.5 font-medium">
              <span
                className="w-2 h-2 rounded-full inline-block"
                style={{ backgroundColor: entry.color }}
              ></span>
              {entry.name}:
            </span>
            <span className="font-mono font-bold text-slate-900">
              {entry.value !== null && entry.value !== undefined ? entry.value : 'N/A'}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
}

// Renders pollution trend chart using Recharts in light theme with Open-Meteo label
export default function TrendChart({ trends = [], stationName, isLoading, error }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow flex flex-col h-[400px]">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-blue-50 text-[#0057FF] rounded-lg">
            <TrendingUp className="w-4 h-4" />
          </div>
          <h3 className="text-base font-semibold text-slate-900 tracking-tight">
            Pollution Trends — {stationName || 'Selected Station'}
          </h3>
        </div>
        <div className="text-xs text-slate-500 font-medium">
          Daily Aggregates (CPCB AQI, PM2.5, PM10)
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="flex-1 w-full relative">
        {isLoading ? (
          <div className="h-full flex items-center justify-center text-slate-500 text-sm">
            <div className="animate-pulse flex items-center gap-2">
              <span className="w-2 h-2 bg-[#0057FF] rounded-full animate-bounce"></span>
              Loading trends data...
            </div>
          </div>
        ) : error ? (
          <div className="h-full flex items-center justify-center text-rose-500 text-sm px-4 text-center">
            {error}
          </div>
        ) : trends.length === 0 ? (
          <div className="h-full flex items-center justify-center text-slate-400 text-sm">
            No trend data available for the selected station and time window.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
              data={trends}
              margin={{ top: 10, right: 20, left: 0, bottom: 20 }}
            >
              <defs>
                <linearGradient id="aqiBandLight" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0057FF" stopOpacity={0.16} />
                  <stop offset="95%" stopColor="#0057FF" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis
                dataKey="bucket"
                tickFormatter={formatBucketDate}
                stroke="#64748B"
                tick={{ fontSize: 12, fill: '#64748B' }}
                tickLine={false}
              />
              <YAxis
                stroke="#64748B"
                tick={{ fontSize: 12, fill: '#64748B' }}
                tickLine={false}
                label={{
                  value: 'AQI (CPCB) / µg/m³',
                  angle: -90,
                  position: 'insideLeft',
                  fill: '#64748B',
                  fontSize: 11,
                  offset: 10,
                }}
              />
              <Tooltip content={<CustomTrendTooltip />} />
              <Legend
                wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }}
                iconType="circle"
              />
              <Area
                type="monotone"
                dataKey="avg_aqi"
                name="Avg AQI (CPCB)"
                stroke="#0057FF"
                fill="url(#aqiBandLight)"
                strokeWidth={2.2}
              />
              <Line
                type="monotone"
                dataKey="avg_pm25"
                name="Avg PM2.5 (µg/m³)"
                stroke="#0284c7"
                strokeWidth={1.8}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="avg_pm10"
                name="Avg PM10 (µg/m³)"
                stroke="#059669"
                strokeWidth={1.8}
                dot={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Footer labels */}
      <div className="mt-2 pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <span className="flex items-center gap-1.5 font-medium">
          <Info className="w-3.5 h-3.5 text-slate-400 inline shrink-0" />
          Modeled data (Open-Meteo)
        </span>
        <span className="text-slate-400">Aggregated via TimescaleDB</span>
      </div>
    </div>
  );
}
