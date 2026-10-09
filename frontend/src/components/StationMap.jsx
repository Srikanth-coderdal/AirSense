import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';
import { calculateDistance } from '../utils/cpcbColors';

// Leaflet default icon asset fix for Vite bundling
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

// Creates custom HTML marker icon for monitoring stations with Signal Blue accents
function createStationIcon(isSelected) {
  return L.divIcon({
    className: 'custom-station-pin',
    html: `
      <div style="
        display: flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        background: ${isSelected ? '#0057FF' : '#ffffff'};
        border: 2px solid ${isSelected ? '#ffffff' : '#0057FF'};
        border-radius: 50%;
        box-shadow: 0 4px 12px ${isSelected ? 'rgba(0, 87, 255, 0.45)' : 'rgba(15, 23, 42, 0.15)'};
        cursor: pointer;
        transition: transform 0.15s ease;
      ">
        <div style="
          width: 10px;
          height: 10px;
          background: ${isSelected ? '#ffffff' : '#0057FF'};
          border-radius: 50%;
        "></div>
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16],
  });
}

// Creates custom HTML marker icon for clicked spatial query point
function createClickIcon() {
  return L.divIcon({
    className: 'custom-click-pin',
    html: `
      <div style="
        display: flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        background: #ef4444;
        border: 2px solid #ffffff;
        border-radius: 50%;
        box-shadow: 0 4px 10px rgba(239, 68, 68, 0.4);
      ">
        <div style="width: 6px; height: 6px; background: #ffffff; border-radius: 50%;"></div>
      </div>
    `,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [0, -12],
  });
}

// Map event handler hook for handling user map clicks and finding nearest station
function MapEventsHandler({ stations, onSelectLocation }) {
  useMapEvents({
    click(e) {
      const { lat, lng } = e.latlng;
      if (!stations || stations.length === 0) return;

      // Find nearest station to clicked coordinates
      let nearestStation = stations[0];
      let minDistance = calculateDistance(lat, lng, stations[0].lat, stations[0].lon);

      for (let i = 1; i < stations.length; i++) {
        const dist = calculateDistance(lat, lng, stations[i].lat, stations[i].lon);
        if (dist < minDistance) {
          minDistance = dist;
          nearestStation = stations[i];
        }
      }

      onSelectLocation({
        coords: { lat, lon: lng },
        station: nearestStation,
        distanceKm: minDistance,
      });
    },
  });
  return null;
}

// Renders interactive Leaflet map of India in pure white container with subtle borders
export default function StationMap({
  stations = [],
  selectedStation,
  clickedCoords,
  onSelectLocation,
}) {
  const defaultCenter = [20.5937, 78.9629]; // Central India
  const defaultZoom = 5;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow flex flex-col min-h-[520px]">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h2 className="text-base font-semibold text-slate-900 tracking-tight">
            National Monitoring Stations
          </h2>
          <p className="text-xs text-slate-500 font-normal">
            Click any station marker or map coordinate to inspect local air quality and compliance
          </p>
        </div>
        <span className="text-xs px-2.5 py-1 rounded-md bg-slate-100 text-slate-700 border border-slate-200 font-mono font-medium">
          {stations.length} Active Stations
        </span>
      </div>

      <div className="w-full h-[450px] rounded-lg overflow-hidden border border-slate-200 relative">
        <MapContainer
          center={defaultCenter}
          zoom={defaultZoom}
          scrollWheelZoom={false}
          style={{ height: '100%', width: '100%', minHeight: '450px' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <MapEventsHandler
            stations={stations}
            onSelectLocation={onSelectLocation}
          />

          {/* Render all monitoring stations */}
          {stations.map((st) => {
            const isSelected = selectedStation && selectedStation.station_id === st.station_id;
            return (
              <Marker
                key={st.station_id}
                position={[st.lat, st.lon]}
                icon={createStationIcon(isSelected)}
                eventHandlers={{
                  click: () => {
                    onSelectLocation({
                      coords: { lat: st.lat, lon: st.lon },
                      station: st,
                      distanceKm: 0,
                    });
                  },
                }}
              >
                <Popup>
                  <div className="text-slate-800 text-xs leading-relaxed p-1">
                    <p className="font-bold text-sm text-[#0057FF] mb-1">{st.name}</p>
                    <p className="text-slate-600">
                      <span className="font-semibold text-slate-700">City:</span> {st.city}
                      {st.state ? `, ${st.state}` : ''}
                    </p>
                    <p className="text-slate-600 font-mono text-[11px] mt-0.5">
                      {st.lat.toFixed(4)}°N, {st.lon.toFixed(4)}°E
                    </p>
                    <p className="mt-2 text-[#0057FF] font-medium text-xs cursor-pointer">
                      Click to analyze station trends →
                    </p>
                  </div>
                </Popup>
              </Marker>
            );
          })}

          {/* Render custom clicked coordinate pin if outside exact station point */}
          {clickedCoords &&
            selectedStation &&
            (Math.abs(clickedCoords.lat - selectedStation.lat) > 0.001 ||
              Math.abs(clickedCoords.lon - selectedStation.lon) > 0.001) && (
              <Marker
                position={[clickedCoords.lat, clickedCoords.lon]}
                icon={createClickIcon()}
              >
                <Popup>
                  <div className="text-slate-800 text-xs p-1">
                    <p className="font-bold text-rose-600">Selected Location</p>
                    <p className="font-mono text-slate-600 text-[11px]">
                      {clickedCoords.lat.toFixed(4)}°N, {clickedCoords.lon.toFixed(4)}°E
                    </p>
                    <p className="text-slate-500 text-[11px] mt-1 border-t border-slate-100 pt-1">
                      Nearest station: <strong className="text-slate-700">{selectedStation.name}</strong>
                    </p>
                  </div>
                </Popup>
              </Marker>
            )}
        </MapContainer>
      </div>
    </div>
  );
}
