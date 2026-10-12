import { API_URL } from "../config";
import PageHero from "../components/PageHero";
import recommendHeroImg from "../assets/images/farm.jpeg";
import React, { useState } from "react";
import farm from "../assets/images/farm.jpeg";
import { tanzaniaRegions } from "../components/regions";
import LocationPicker from "../components/LocationPicker";

type RecommendationResponse = {
  location: {
    latitude: number;
    longitude: number;
    address: string;
    region?: string;
  };
  soil_properties: Record<string, unknown>;
  // Long-term averages for the location, not today's weather
  weather: {
    temperature: number;
    humidity: number | null;
    rainfall: number;
    rainy_seasons: string[];
    elevation: number | null;
    period: string;
  };
  recommendations: Record<
    string,
    {
      explanation: string;
      score: number;
      market?: { summary: string | null };
    }
  >;
  forecast: {
    days: { date: string; rain_mm: number; chance: number }[];
    advice: string | null;
  } | null;
  notes: string[];
};

const dayName = (iso: string) =>
  new Date(`${iso}T12:00:00`).toLocaleDateString(undefined, {
    weekday: "short",
  });

// Scores below 1% would round to "0.0%", which reads like an error
const formatMatch = (score: number) =>
  score < 0.01 ? "<1%" : `${(score * 100).toFixed(score < 0.1 ? 1 : 0)}%`;

const CropRecommendation: React.FC = () => {
  const [latitude, setLatitude] = useState<number | null>(null);
  const [longitude, setLongitude] = useState<number | null>(null);
  const [result, setResult] = useState<RecommendationResponse | null>(null);
  const [region, setRegion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePick = (lat: number, lng: number) => {
    setLatitude(lat);
    setLongitude(lng);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!latitude || !longitude) {
      setError("Please select a location on the map.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/recommend/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ latitude, longitude }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data?.error ?? "Failed to fetch");
      setResult(data as RecommendationResponse);
    } catch (err) {
      console.error(err);
      setResult(null);
      setError(
        err instanceof Error && err.message !== "Failed to fetch"
          ? err.message
          : "Could not get recommendations. Please try again.",
      );
    }
    setLoading(false);
  };

  const handleSearch = () => {
    if (!region.trim()) return;

    const matchedRegion = tanzaniaRegions.find(
      (r) => r.name.toLowerCase() === region.toLowerCase(),
    );

    if (matchedRegion) {
      setLatitude(matchedRegion.latitude);
      setLongitude(matchedRegion.longitude);
      setError(null);
    } else {
      setError(
        "Region not found. Please check the spelling or try another region.",
      );
    }
  };

  return (
    <div>
      <PageHero
        image={recommendHeroImg}
        title="Crop Recommendation"
        subtitle="Choose a region or click on the map. We compare each crop's needs with the soil and long-term climate at that spot to suggest the best crops to grow."
      />
      <div className="page">
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Controls */}
          <div className="card space-y-6 p-5 lg:col-span-1">
            <div>
              <label htmlFor="region" className="label">
                Search by region
              </label>
              <div className="flex gap-2">
                <input
                  id="region"
                  type="text"
                  list="region-list"
                  placeholder="e.g. Dodoma"
                  value={region}
                  onChange={(e) => setRegion(e.target.value)}
                  onKeyDown={(e) =>
                    e.key === "Enter" && (e.preventDefault(), handleSearch())
                  }
                  className="input"
                />
                <datalist id="region-list">
                  {tanzaniaRegions.map((r) => (
                    <option key={r.name} value={r.name} />
                  ))}
                </datalist>
                <button
                  onClick={handleSearch}
                  type="button"
                  className="btn-secondary"
                >
                  Search
                </button>
              </div>
            </div>

            <form
              onSubmit={handleSubmit}
              className="space-y-4 border-t border-stone-200 pt-6"
            >
              <p className="text-sm font-medium text-stone-700">
                Selected location
              </p>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label htmlFor="lat" className="label text-xs text-stone-500">
                    Latitude
                  </label>
                  <input
                    id="lat"
                    type="text"
                    value={latitude?.toFixed(4) ?? ""}
                    readOnly
                    placeholder="—"
                    className="input"
                  />
                </div>
                <div>
                  <label htmlFor="lng" className="label text-xs text-stone-500">
                    Longitude
                  </label>
                  <input
                    id="lng"
                    type="text"
                    value={longitude?.toFixed(4) ?? ""}
                    readOnly
                    placeholder="—"
                    className="input"
                  />
                </div>
              </div>
              {error && <p className="alert-error">{error}</p>}
              <button
                type="submit"
                disabled={!latitude || !longitude || loading}
                className="btn-primary w-full py-2.5"
              >
                {loading ? "Analysing location…" : "Get recommendations"}
              </button>
            </form>
          </div>

          {/* Map */}
          <div className="card overflow-hidden lg:col-span-2">
            <LocationPicker
              latitude={latitude}
              longitude={longitude}
              onPick={handlePick}
              className="h-[420px] w-full bg-stone-100"
            />
          </div>
        </div>

        {result && (
          <section className="mt-12">
            <h2 className="section-title">
              Results for {result.location.region ?? "Unknown Region"}
            </h2>
            <p className="muted mt-1">
              {result.location.latitude.toFixed(4)},{" "}
              {result.location.longitude.toFixed(4)}
              {result.weather.elevation != null &&
                ` · ${Math.round(result.weather.elevation).toLocaleString()} m above sea level`}
            </p>

            <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div className="card p-5">
                <p className="stat-label">Temperature</p>
                <p className="stat-value">{result.weather.temperature}°C</p>
                <p className="mt-1 text-xs text-stone-500">Yearly average</p>
              </div>
              <div className="card p-5">
                <p className="stat-label">Humidity</p>
                <p className="stat-value">{result.weather.humidity ?? "—"}%</p>
                <p className="mt-1 text-xs text-stone-500">Yearly average</p>
              </div>
              <div className="card p-5">
                <p className="stat-label">Rainfall</p>
                <p className="stat-value">
                  {Math.round(result.weather.rainfall).toLocaleString()} mm
                </p>
                <p className="mt-1 text-xs text-stone-500">
                  Per year, {result.weather.period}
                  {result.weather.rainy_seasons.length > 0 &&
                    ` · Rains: ${result.weather.rainy_seasons.join(", ")}`}
                </p>
              </div>
            </div>

            {result.forecast?.advice && (
              <div className="card mt-4 p-5">
                <p className="stat-label">Next 5 days</p>
                <p className="mt-2 text-sm text-stone-600">
                  {result.forecast.advice}
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {result.forecast.days.map((day) => (
                    <div
                      key={day.date}
                      className="min-w-[4.5rem] rounded-lg bg-stone-50 px-3 py-2 text-center"
                    >
                      <p className="text-xs text-stone-500">
                        {dayName(day.date)}
                      </p>
                      <p className="text-sm font-medium text-stone-800">
                        {Math.round(day.rain_mm)} mm
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {result.notes.length > 0 && (
              <div className="card mt-4 p-5">
                <p className="stat-label">About this land</p>
                <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-stone-600">
                  {result.notes.map((note) => (
                    <li key={note}>{note}</li>
                  ))}
                </ul>
              </div>
            )}

            <h3 className="section-title mt-10">Top 3 recommended crops</h3>
            <div className="mt-4 space-y-4">
              {Object.entries(result.recommendations).map(([crop, info]) => (
                <div
                  key={crop}
                  className="card flex flex-col overflow-hidden sm:flex-row"
                >
                  <img
                    src={farm}
                    alt={crop}
                    className="h-36 w-full object-cover sm:h-auto sm:w-48"
                  />
                  <div className="flex-1 p-5">
                    <div className="flex flex-wrap items-baseline justify-between gap-2">
                      <h4 className="text-lg font-semibold text-stone-900">
                        {crop}
                      </h4>
                      <span className="text-sm font-medium text-primary">
                        {formatMatch(info.score)} match
                      </span>
                    </div>
                    <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-stone-100">
                      <div
                        className="h-full rounded-full bg-primary"
                        style={{ width: `${info.score * 100}%` }}
                      />
                    </div>
                    <p className="mt-3 text-sm text-stone-600">
                      {info.explanation}
                    </p>
                    {info.market?.summary && (
                      <p className="mt-2 text-sm text-stone-600">
                        <span className="font-medium text-stone-800">
                          Market:{" "}
                        </span>
                        {info.market.summary}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
};

export default CropRecommendation;
