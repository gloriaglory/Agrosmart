import { useEffect } from "react";
import { MapContainer, TileLayer, CircleMarker, useMap, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";

type Props = {
  latitude: number | null;
  longitude: number | null;
  onPick: (lat: number, lng: number) => void;
  className?: string;
};

// Default view: Dodoma, central Tanzania
const DEFAULT_CENTER: [number, number] = [-6.163, 35.7516];

const ClickHandler = ({ onPick }: { onPick: Props["onPick"] }) => {
  useMapEvents({
    click: (e) => onPick(e.latlng.lat, e.latlng.lng),
  });
  return null;
};

// Smoothly moves the map when the selected point changes (e.g. from region search).
const FollowSelection = ({ position }: { position: [number, number] | null }) => {
  const map = useMap();
  useEffect(() => {
    if (position) map.flyTo(position, Math.max(map.getZoom(), 8), { duration: 0.8 });
  }, [map, position?.[0], position?.[1]]); // eslint-disable-line react-hooks/exhaustive-deps
  return null;
};

// Map for choosing a single location by clicking.
const LocationPicker = ({ latitude, longitude, onPick, className = "" }: Props) => {
  const position: [number, number] | null =
    latitude != null && longitude != null ? [latitude, longitude] : null;

  return (
    <MapContainer
      center={DEFAULT_CENTER}
      zoom={6}
      scrollWheelZoom
      className={`isolate cursor-crosshair ${className}`}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <ClickHandler onPick={onPick} />
      <FollowSelection position={position} />
      {position && (
        <CircleMarker
          center={position}
          radius={9}
          pathOptions={{ color: "#ffffff", weight: 3, fillColor: "#166534", fillOpacity: 1 }}
        />
      )}
    </MapContainer>
  );
};

export default LocationPicker;
