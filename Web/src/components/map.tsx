// components/GoogleMapComponent.tsx
import React, { useCallback } from "react";
import { GoogleMap, useLoadScript, Marker } from "@react-google-maps/api";

type Props = {
  onSelectRegion: (region: string) => void;
};

const containerStyle = {
  width: "100%",
  height: "200px",
};

// Centered on Tanzania
const center = {
  lat: -6.369028,
  lng: 34.888822,
};

const regions = [
  { name: "Dodoma", lat: -6.1630, lng: 35.7516 },
  { name: "Arusha", lat: -3.3869, lng: 36.6829 },
  { name: "Mbeya", lat: -8.9016, lng: 33.4608 },
  { name: "Mwanza", lat: -2.5164, lng: 32.9175 },
  { name: "Dar es Salaam", lat: -6.7924, lng: 39.2083 },
];

const GoogleMapComponent: React.FC<Props> = ({ onSelectRegion }) => {
  const { isLoaded, loadError } = useLoadScript({
    googleMapsApiKey: "AIzaSyA1LgMoAuAn72cs0wXatbVn3WI9WxqoKFM",
  });

  const handleMarkerClick = useCallback(
    (regionName: string) => {
      onSelectRegion(regionName);
    },
    [onSelectRegion]
  );

  if (loadError) return <p>Error loading map</p>;
  if (!isLoaded) return <p>Loading map...</p>;

  return (
    <GoogleMap mapContainerStyle={containerStyle} center={center} zoom={6}>
      {regions.map((region) => (
        <Marker
          key={region.name}
          position={{ lat: region.lat, lng: region.lng }}
          onClick={() => handleMarkerClick(region.name)}
        />
      ))}
    </GoogleMap>
  );
};

export default GoogleMapComponent;
