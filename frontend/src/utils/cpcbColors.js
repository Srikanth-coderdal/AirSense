// Returns styling configurations for CPCB AQI categories
export function getCpcbColorInfo(aqi) {
  if (aqi === null || aqi === undefined) {
    return {
      category: 'Unknown',
      bgColor: 'bg-slate-700',
      textColor: 'text-slate-300',
      borderColor: 'border-slate-600',
      hex: '#64748b',
    };
  }
  if (aqi <= 50) {
    return {
      category: 'Good',
      bgColor: 'bg-emerald-600',
      textColor: 'text-emerald-100',
      borderColor: 'border-emerald-500',
      hex: '#16a34a',
    };
  }
  if (aqi <= 100) {
    return {
      category: 'Satisfactory',
      bgColor: 'bg-lime-600',
      textColor: 'text-lime-100',
      borderColor: 'border-lime-500',
      hex: '#84cc16',
    };
  }
  if (aqi <= 200) {
    return {
      category: 'Moderate',
      bgColor: 'bg-amber-500',
      textColor: 'text-amber-950',
      borderColor: 'border-amber-400',
      hex: '#eab308',
    };
  }
  if (aqi <= 300) {
    return {
      category: 'Poor',
      bgColor: 'bg-orange-600',
      textColor: 'text-orange-100',
      borderColor: 'border-orange-500',
      hex: '#f97316',
    };
  }
  if (aqi <= 400) {
    return {
      category: 'Very Poor',
      bgColor: 'bg-red-600',
      textColor: 'text-red-100',
      borderColor: 'border-red-500',
      hex: '#ef4444',
    };
  }
  return {
    category: 'Severe',
    bgColor: 'bg-rose-900',
    textColor: 'text-rose-100',
    borderColor: 'border-rose-700',
    hex: '#991b1b',
  };
}

// Calculates great-circle distance between two coordinates in kilometers using Haversine formula
export function calculateDistance(lat1, lon1, lat2, lon2) {
  const earthRadiusKm = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return earthRadiusKm * c;
}
