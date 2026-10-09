import React from 'react';
import { ShieldAlert, AlertCircle, FileText, CheckCircle, Clock } from 'lucide-react';

// Formats penalty amount into formatted Indian Rupee currency string
function formatInr(amount) {
  if (amount === null || amount === undefined) return 'N/A';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
}

// Returns badge color styling corresponding to compliance violation status in light theme
function getStatusBadge(status) {
  const normalized = (status || '').toLowerCase();
  if (normalized.includes('resolved') || normalized.includes('closed')) {
    return {
      bg: 'bg-emerald-50',
      text: 'text-emerald-700',
      border: 'border-emerald-200',
      icon: CheckCircle,
    };
  }
  if (normalized.includes('pending') || normalized.includes('appeal')) {
    return {
      bg: 'bg-amber-50',
      text: 'text-amber-700',
      border: 'border-amber-200',
      icon: Clock,
    };
  }
  return {
    bg: 'bg-rose-50',
    text: 'text-rose-700',
    border: 'border-rose-200',
    icon: AlertCircle,
  };
}

// Renders spatial regulatory compliance and enforcement records in light theme layout
export default function CompliancePanel({
  records = [],
  locationCoords,
  radiusKm = 50,
  onRadiusChange,
  isLoading,
  error,
}) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow flex flex-col h-[520px]">
      {/* Panel Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-amber-50 text-amber-600 rounded-lg border border-amber-100">
            <ShieldAlert className="w-5 h-5 shrink-0" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-slate-900 tracking-tight">
              Environmental Compliance & Violations
            </h3>
            <p className="text-xs text-slate-500 font-normal">
              Regulatory notices within {radiusKm} km of selected position
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <span className="text-xs font-medium text-slate-500">Radius:</span>
          <select
            value={radiusKm}
            onChange={(e) => onRadiusChange(Number(e.target.value))}
            className="bg-white border border-slate-300 rounded-md px-2.5 py-1 text-xs font-medium text-slate-800 outline-none focus:ring-2 focus:ring-[#0057FF] focus:border-[#0057FF] cursor-pointer"
          >
            <option value="25">25 km</option>
            <option value="50">50 km</option>
            <option value="100">100 km</option>
            <option value="250">250 km</option>
          </select>
        </div>
      </div>

      {/* Illustrative dataset notice banner */}
      <div className="bg-blue-50/70 border border-blue-200 rounded-lg px-3 py-2 mb-3 flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-[#0057FF] shrink-0" />
          <span className="text-blue-900 font-medium">Curated sample dataset (illustrative)</span>
        </div>
        <span className="text-xs text-blue-700 font-semibold font-mono">
          {records.length} {records.length === 1 ? 'Notice' : 'Notices'}
        </span>
      </div>

      {/* Compliance records scrollable list */}
      <div className="flex-1 overflow-y-auto pr-1 space-y-2.5">
        {isLoading ? (
          <div className="h-full flex items-center justify-center text-slate-500 text-sm">
            <div className="animate-pulse flex items-center gap-2">
              <span className="w-2 h-2 bg-[#0057FF] rounded-full animate-bounce"></span>
              Searching spatial compliance records...
            </div>
          </div>
        ) : error ? (
          <div className="h-full flex items-center justify-center text-rose-500 text-sm px-4 text-center">
            {error}
          </div>
        ) : records.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 text-xs text-center p-6 gap-2">
            <div className="p-3 bg-emerald-50 text-emerald-600 rounded-full">
              <CheckCircle className="w-6 h-6" />
            </div>
            <p className="font-semibold text-slate-800 text-sm">No Violations Found</p>
            <p className="text-slate-500 max-w-xs">
              No regulatory enforcement actions recorded within {radiusKm} km of coordinates (
              {locationCoords ? `${locationCoords.lat.toFixed(2)}°N, ${locationCoords.lon.toFixed(2)}°E` : ''}).
            </p>
          </div>
        ) : (
          records.map((rec) => {
            const badge = getStatusBadge(rec.status);
            const StatusIcon = badge.icon;
            return (
              <div
                key={rec.record_id}
                className="bg-slate-50 border border-slate-200 hover:border-slate-300 rounded-lg p-3.5 transition-colors text-xs space-y-2"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h4 className="font-semibold text-slate-900 text-sm tracking-tight">{rec.title}</h4>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="px-2 py-0.5 rounded-full bg-blue-50 text-[#0057FF] border border-blue-200 text-[10px] font-semibold">
                        {rec.authority}
                      </span>
                      <span className="text-slate-500 text-xs">
                        City: <strong className="text-slate-700 font-medium">{rec.city}</strong>
                      </span>
                    </div>
                  </div>
                  <span
                    className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${badge.bg} ${badge.text} ${badge.border} shrink-0`}
                  >
                    <StatusIcon className="w-3.5 h-3.5" />
                    {rec.status}
                  </span>
                </div>

                {rec.details && (
                  <p className="text-slate-700 text-xs bg-white p-2.5 rounded border border-slate-200 leading-relaxed">
                    {rec.details}
                  </p>
                )}

                <div className="flex items-center justify-between text-xs text-slate-500 pt-1 border-t border-slate-200">
                  <span>
                    Category: <span className="font-medium text-slate-700">{rec.category || 'General'}</span>
                  </span>
                  <span>
                    Penalty:{' '}
                    <span className="font-mono font-bold text-slate-900">
                      {formatInr(rec.penalty_inr)}
                    </span>
                  </span>
                  <span className="text-slate-400">Issued: {rec.issue_date}</span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
