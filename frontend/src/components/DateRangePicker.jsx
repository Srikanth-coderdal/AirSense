import React from 'react';
import { Calendar } from 'lucide-react';

// Renders redesigned DateRangePicker with high-contrast inputs and Signal Blue active pills
export default function DateRangePicker({ startDate, endDate, onRangeChange }) {
  // Evaluates which quick preset matches the current range selection
  const getActivePreset = () => {
    if (startDate === '2026-10-01' && endDate === '2026-10-08') return '7';
    if (startDate === '2026-09-08' && endDate === '2026-10-08') return '30';
    if (startDate === '2026-04-11' && (endDate === '2026-10-08' || endDate === '2026-10-09')) return 'all';
    return null;
  };

  const activePreset = getActivePreset();

  // Handles clicking a quick interval preset button
  const handlePreset = (presetKey) => {
    const anchor = new Date('2026-10-08T23:59:59');
    if (presetKey === 'all') {
      onRangeChange('2026-04-11', '2026-10-08');
      return;
    }
    const days = presetKey === '7' ? 7 : 30;
    const start = new Date(anchor);
    start.setDate(anchor.getDate() - days);
    onRangeChange(
      start.toISOString().split('T')[0],
      anchor.toISOString().split('T')[0]
    );
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow flex flex-col lg:flex-row lg:items-center justify-between gap-4">
      {/* Title & icon header */}
      <div className="flex items-center gap-3">
        <div className="p-2 bg-blue-50 border border-blue-100 rounded-lg text-[#0057FF]">
          <Calendar className="w-5 h-5 shrink-0" />
        </div>
        <div>
          <span className="text-sm font-semibold text-slate-900 block tracking-tight">
            Analysis Window
          </span>
          <span className="text-xs text-slate-500 font-normal">
            Filter historical trends and aggregated metrics across India stations
          </span>
        </div>
      </div>

      {/* Date controls container */}
      <div className="flex flex-wrap items-center gap-3">
        {/* High-contrast Date inputs */}
        <div className="flex items-center gap-2">
          {/* FROM field */}
          <div className="flex items-center gap-2 bg-white border border-slate-300 rounded-md px-2.5 py-1 focus-within:ring-2 focus-within:ring-[#0057FF] focus-within:border-[#0057FF] transition-all">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              FROM
            </span>
            <input
              type="date"
              value={startDate}
              min="2026-04-11"
              max="2026-10-09"
              style={{ colorScheme: 'light' }}
              onChange={(e) => onRangeChange(e.target.value, endDate)}
              className="text-sm font-medium text-slate-800 bg-transparent outline-none cursor-pointer"
            />
          </div>

          {/* TO field */}
          <div className="flex items-center gap-2 bg-white border border-slate-300 rounded-md px-2.5 py-1 focus-within:ring-2 focus-within:ring-[#0057FF] focus-within:border-[#0057FF] transition-all">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              TO
            </span>
            <input
              type="date"
              value={endDate}
              min="2026-04-11"
              max="2026-10-09"
              style={{ colorScheme: 'light' }}
              onChange={(e) => onRangeChange(startDate, e.target.value)}
              className="text-sm font-medium text-slate-800 bg-transparent outline-none cursor-pointer"
            />
          </div>
        </div>

        {/* Visual separation label & explicit quick buttons */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-slate-500 whitespace-nowrap">
            Time Range:
          </span>
          <div className="flex items-center gap-1.5">
            <button
              type="button"
              onClick={() => handlePreset('7')}
              className={
                activePreset === '7'
                  ? 'bg-[#0057FF] text-white font-medium text-xs px-3 py-1.5 rounded-md shadow-sm'
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs px-3 py-1.5 rounded-md transition-colors border border-slate-200'
              }
            >
              Last 7 Days
            </button>
            <button
              type="button"
              onClick={() => handlePreset('30')}
              className={
                activePreset === '30'
                  ? 'bg-[#0057FF] text-white font-medium text-xs px-3 py-1.5 rounded-md shadow-sm'
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs px-3 py-1.5 rounded-md transition-colors border border-slate-200'
              }
            >
              Last 30 Days
            </button>
            <button
              type="button"
              onClick={() => handlePreset('all')}
              className={
                activePreset === 'all'
                  ? 'bg-[#0057FF] text-white font-medium text-xs px-3 py-1.5 rounded-md shadow-sm'
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs px-3 py-1.5 rounded-md transition-colors border border-slate-200'
              }
            >
              All (6 Months)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
