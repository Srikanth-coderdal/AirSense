import React from 'react';
import { HeartPulse, AlertCircle, CheckCircle2, Shield, Thermometer, Droplets, Wind } from 'lucide-react';
import { getCpcbColorInfo } from '../utils/cpcbColors';

// 6 active criteria pollutants to display in live breakdown grid
const POLLUTANTS = [
  { label: 'PM2.5', key: 'pm25', unit: 'µg/m³' },
  { label: 'PM10', key: 'pm10', unit: 'µg/m³' },
  { label: 'NO2', key: 'no2', unit: 'µg/m³' },
  { label: 'SO2', key: 'so2', unit: 'µg/m³' },
  { label: 'CO', key: 'co', unit: 'µg/m³' },
  { label: 'O3', key: 'o3', unit: 'µg/m³' },
];

// Renders CPCB health recommendation hero card with 6-pollutant concentration breakdown
export default function RecommendationCard({
  recommendation,
  aqiCpcb,
  latestMeasurement,
  isLoading,
  error,
}) {
  const colorInfo = getCpcbColorInfo(aqiCpcb);

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between min-h-[520px]">
      <div>
        {/* Header with AQI count and CPCB Category Pill */}
        <div className="flex items-start justify-between gap-3 pb-3.5 border-b border-slate-100">
          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">
              Current Air Quality Index
            </span>
            <div className="flex items-baseline gap-3 mt-1">
              <span className="text-4xl font-extrabold font-mono tracking-tight text-slate-900">
                {aqiCpcb !== null && aqiCpcb !== undefined ? aqiCpcb : '--'}
              </span>
              <span className="text-xs text-slate-500 font-medium">
                aqi_cpcb standard
              </span>
            </div>
          </div>

          <div className="text-right">
            <span
              className={`inline-block px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide border shadow-xs ${colorInfo.bgColor} ${colorInfo.textColor} ${colorInfo.borderColor}`}
            >
              {colorInfo.category}
            </span>
            {latestMeasurement && latestMeasurement.time && (
              <span className="text-[11px] text-slate-400 block mt-1.5 font-medium">
                Observed: {new Date(latestMeasurement.time).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
              </span>
            )}
          </div>
        </div>

        {/* Environmental conditions metric tiles */}
        {latestMeasurement && (
          <div className="grid grid-cols-3 gap-2 py-2.5 border-b border-slate-100 text-xs">
            <div className="bg-slate-50 border border-slate-200/80 rounded-lg p-2 flex items-center gap-2 text-slate-600">
              <Thermometer className="w-4 h-4 text-rose-500 shrink-0" />
              <div>
                <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-semibold leading-tight">
                  Temp
                </span>
                <span className="font-mono font-bold text-slate-900 text-xs">
                  {latestMeasurement.temperature !== null ? `${latestMeasurement.temperature}°C` : 'N/A'}
                </span>
              </div>
            </div>

            <div className="bg-slate-50 border border-slate-200/80 rounded-lg p-2 flex items-center gap-2 text-slate-600">
              <Droplets className="w-4 h-4 text-sky-500 shrink-0" />
              <div>
                <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-semibold leading-tight">
                  Humidity
                </span>
                <span className="font-mono font-bold text-slate-900 text-xs">
                  {latestMeasurement.humidity !== null ? `${latestMeasurement.humidity}%` : 'N/A'}
                </span>
              </div>
            </div>

            <div className="bg-slate-50 border border-slate-200/80 rounded-lg p-2 flex items-center gap-2 text-slate-600">
              <Wind className="w-4 h-4 text-emerald-500 shrink-0" />
              <div>
                <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-semibold leading-tight">
                  Wind
                </span>
                <span className="font-mono font-bold text-slate-900 text-xs">
                  {latestMeasurement.wind_speed !== null ? `${latestMeasurement.wind_speed} m/s` : 'N/A'}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Live 6-Pollutant Breakdown Grid */}
        <div className="py-2.5 border-b border-slate-100">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-1.5">
            Real-Time Pollutant Concentrations
          </span>
          <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
            {POLLUTANTS.map((p) => {
              const rawVal = latestMeasurement ? latestMeasurement[p.key] : null;
              const valDisplay = rawVal !== null && rawVal !== undefined ? rawVal : '--';
              return (
                <div
                  key={p.key}
                  className="bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-center shadow-xs"
                >
                  <div className="text-xs font-semibold text-slate-500">{p.label}</div>
                  <div className="text-base font-bold text-slate-900 font-mono my-0.5">
                    {valDisplay}
                  </div>
                  <div className="text-[10px] text-slate-400">{p.unit}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Advisory content section */}
        <div className="mt-3 space-y-2.5 overflow-y-auto max-h-[175px] pr-1">
          {isLoading ? (
            <div className="py-6 text-center text-slate-500 text-xs animate-pulse">
              Retrieving health advisories for CPCB AQI...
            </div>
          ) : error ? (
            <div className="py-3 text-rose-500 text-xs text-center">{error}</div>
          ) : recommendation ? (
            <>
              {/* Health Impact */}
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-2.5">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-900 mb-1">
                  <HeartPulse className="w-3.5 h-3.5 text-rose-500 shrink-0" />
                  Health Impact
                </div>
                <p className="text-xs text-slate-600 leading-relaxed font-normal">
                  {recommendation.health_impact}
                </p>
              </div>

              {/* Cautionary Advice */}
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-2.5">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-900 mb-1">
                  <AlertCircle className="w-3.5 h-3.5 text-amber-500 shrink-0" />
                  Cautionary Advice
                </div>
                <p className="text-xs text-slate-600 leading-relaxed font-normal">
                  {recommendation.cautionary_advice}
                </p>
              </div>

              {/* Recommended Action Steps */}
              {recommendation.action_steps && recommendation.action_steps.length > 0 && (
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-2.5">
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-900 mb-1.5">
                    <Shield className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    CPCB Mitigation Steps
                  </div>
                  <ul className="space-y-1">
                    {recommendation.action_steps.map((step, idx) => (
                      <li key={idx} className="flex items-start gap-1.5 text-xs text-slate-600">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600 shrink-0 mt-0.5" />
                        <span>{step}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          ) : null}
        </div>
      </div>

      {/* Card Footer */}
      <div className="mt-2.5 pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <span className="font-medium">Central Pollution Control Board (CPCB)</span>
        <span className="font-mono text-slate-400 text-[11px]">NAAQI Standards</span>
      </div>
    </div>
  );
}
