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
  { name: "Arusha", lat: -3.3869, lng: 36.6829 },
  { name: "Dar es Salaam", lat: -6.7924, lng: 39.2083 },
  { name: "Dodoma", lat: -6.163, lng: 35.7516 },
  { name: "Geita", lat: -2.8667, lng: 32.4 },
  { name: "Iringa", lat: -7.77, lng: 35.69 },
  { name: "Kagera", lat: -1.58, lng: 31.5 },
  { name: "Katavi", lat: -6.4167, lng: 31.225 },
  { name: "Kigoma", lat: -4.8829, lng: 29.6615 },
  { name: "Kilimanjaro", lat: -3.0674, lng: 37.3556 },
  { name: "Lindi", lat: -10.0, lng: 39.7167 },
  { name: "Manyara", lat: -4.0167, lng: 36.9667 },
  { name: "Mara", lat: -1.75, lng: 34.95 },
  { name: "Mbeya", lat: -8.9016, lng: 33.4608 },
  { name: "Morogoro", lat: -6.821, lng: 37.6591 },
  { name: "Mtwara", lat: -10.2667, lng: 40.1833 },
  { name: "Mwanza", lat: -2.5164, lng: 32.9175 },
  { name: "Njombe", lat: -9.3333, lng: 34.7667 },
  { name: "Pwani", lat: -7.0, lng: 38.0 },
  { name: "Rukwa", lat: -8.0, lng: 31.5 },
  { name: "Ruvuma", lat: -10.6667, lng: 35.65 },
  { name: "Shinyanga", lat: -3.6667, lng: 33.4333 },
  { name: "Simiyu", lat: -2.7833, lng: 34.8333 },
  { name: "Singida", lat: -4.8167, lng: 34.75 },
  { name: "Songwe", lat: -8.3667, lng: 32.9167 },
  { name: "Tabora", lat: -5.0167, lng: 32.8 },
  { name: "Tanga", lat: -5.0667, lng: 39.1 },
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
