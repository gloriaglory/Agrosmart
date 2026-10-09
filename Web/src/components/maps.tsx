import React from "react";
import { MapContainer, TileLayer, CircleMarker, Tooltip } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { tanzaniaRegions } from "./regions";
import type { RegionSummary } from "../market";

type Props = {
  summaries: RegionSummary[];
  onSelectRegion: (region: string) => void;
  selectedRegion?: string | null;
};

// Centered on Tanzania
const center: [number, number] = [-6.369028, 34.888822];

// Regions with listings get larger green markers (sized by listing count);
// regions without listings get small grey ones.
const RegionMap: React.FC<Props> = ({ summaries, onSelectRegion, selectedRegion }) => {
  const counts = new Map(summaries.map((s) => [s.region, s.listings]));

  return (
    <MapContainer
      center={center}
      zoom={5}
      scrollWheelZoom={false}
      className="isolate h-[260px] w-full rounded-lg"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {tanzaniaRegions.map((region) => {
        const count = counts.get(region.name) ?? 0;
        const active = region.name === selectedRegion;
        const radius = count ? 7 + Math.min(count, 8) : 4;
        return (
          <CircleMarker
            key={region.name}
            center={[region.latitude, region.longitude]}
            radius={active ? radius + 2 : radius}
            pathOptions={{
              color: "#ffffff",
              weight: 2,
              fillColor: active ? "#14532d" : count ? "#16a34a" : "#a8a29e",
              fillOpacity: count ? 0.95 : 0.8,
            }}
            eventHandlers={{ click: () => onSelectRegion(region.name) }}
          >
            <Tooltip direction="top" offset={[0, -6]}>
              {region.name}: {count ? `${count} listing${count === 1 ? "" : "s"}` : "no listings"}
            </Tooltip>
          </CircleMarker>
        );
      })}
    </MapContainer>
  );
};

export default RegionMap;
