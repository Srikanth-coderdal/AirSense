import React from 'react';
import { Wind, MapPin, Activity, RefreshCw } from 'lucide-react';

// Renders top application header bar in crisp white with Signal Blue accents
export default function Header({ selectedStation, clickedCoords, isRefreshing, onRefresh }) {
  return (
    <header className="bg-white/95 backdrop-blur-sm border-b border-slate-200 shadow-sm sticky top-0 z-30 px-6 py-3.5">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 max-w-7xl mx-auto">
        {/* Brand identity */}
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-blue-50 border border-blue-200 rounded-xl text-[#0057FF] shadow-xs">
            <Wind className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-slate-900">AirSense</h1>
              <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-[#0057FF] border border-blue-200">
                National Platform
              </span>
            </div>
            <p className="text-xs text-slate-500 font-normal">
              Continuous Air Quality Monitoring, Spatial Compliance & ML Forecast
            </p>
          </div>
        </div>

        {/* Status pills & action */}
        <div className="flex items-center gap-3 flex-wrap">
          {selectedStation && (
            <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 px-3.5 py-1.5 rounded-lg text-sm shadow-xs">
              <MapPin className="w-4 h-4 text-[#0057FF] shrink-0" />
              <div>
                <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold block leading-none">
                  Station
                </span>
                <span className="font-semibold text-slate-900 text-xs">
                  {selectedStation.name}
                </span>
              </div>
            </div>
          )}

          {clickedCoords && (
            <div className="hidden lg:flex items-center gap-2 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-lg text-xs text-slate-600 shadow-xs">
              <Activity className="w-3.5 h-3.5 text-slate-400 shrink-0" />
              <span className="font-mono text-slate-700">
                {clickedCoords.lat.toFixed(4)}°N, {clickedCoords.lon.toFixed(4)}°E
              </span>
            </div>
          )}

          <button
            type="button"
            onClick={onRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-white hover:bg-slate-50 active:bg-slate-100 text-slate-700 rounded-lg text-xs font-medium border border-slate-300 shadow-xs transition-colors disabled:opacity-50 cursor-pointer"
            title="Reload dashboard data"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-[#0057FF]' : 'text-slate-500'}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>
    </header>
  );
}
