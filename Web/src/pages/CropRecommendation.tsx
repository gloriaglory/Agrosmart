import React, { useState, useEffect, useCallback } from "react";
import farm from "../assets/images/farm.jpeg";
import irrigation from "../assets/images/farm1.jpeg";
import soil from "../assets/images/farm2.jpeg";

declare global {
  interface Window {
    initMap: () => void;
  }
}

type RecommendationResponse = {
  location: {
    latitude: number;
    longitude: number;
    address: string;
  };
  soil_properties: Record<string, unknown>;
  weather: {
    temperature: number;
    humidity: number;
    rainfall: number;
  };
  recommendations: Record<string, { explanation: string; score: number }>;
};

const CropRecommendation: React.FC = () => {
  const [, setMap] = useState<google.maps.Map | null>(null);
  const [marker, setMarker] = useState<google.maps.Marker | null>(null);
  const [latitude, setLatitude] = useState<number | null>(null);
  const [longitude, setLongitude] = useState<number | null>(null);
  const [result, setResult] = useState<RecommendationResponse | null>(null);
  const [region, setRegion] = useState("");
  const [loading, setLoading] = useState(false);

  const images = [farm, irrigation, soil];
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  // Slide image every 4 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImageIndex((prevIndex) => (prevIndex + 1) % images.length);
    }, 4000);
    return () => clearInterval(interval);
  }, [images.length]);

  const loadGoogleMaps = () => {
    const existingScript = document.getElementById("googleMapsScript");
    if (!existingScript) {
      const script = document.createElement("script");
      script.id = "googleMapsScript";
      script.src = `https://maps.googleapis.com/maps/api/js?key=AIzaSyA1LgMoAuAn72cs0wXatbVn3WI9WxqoKFM&callback=initMap`;
      script.async = true;
      document.body.appendChild(script);
    } else {
      window.initMap();
    }
  };

  const initMap = useCallback(() => {
    const defaultLocation = { lat: -6.163, lng: 35.7516 };
    const mapInstance = new google.maps.Map(
      document.getElementById("map") as HTMLElement,
      {
        center: defaultLocation,
        zoom: 7,
        disableDefaultUI: true,
      }
    );

    mapInstance.addListener("click", (event: google.maps.MapMouseEvent) => {
      const clickedLat = event.latLng?.lat();
      const clickedLng = event.latLng?.lng();

      if (clickedLat && clickedLng) {
        setLatitude(clickedLat);
        setLongitude(clickedLng);

        if (marker) {
          marker.setPosition({ lat: clickedLat, lng: clickedLng });
        } else {
          const newMarker = new google.maps.Marker({
            position: { lat: clickedLat, lng: clickedLng },
            map: mapInstance,
            animation: google.maps.Animation.DROP,
          });
          setMarker(newMarker);
        }
      }
    });

    setMap(mapInstance);
  }, [marker]);

  useEffect(() => {
    window.initMap = initMap;
    loadGoogleMaps();
  }, [initMap]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!latitude || !longitude)
      return alert("Please select a location on the map.");
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/recommend/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ latitude, longitude }),
      });

      if (!response.ok) throw new Error("Failed to fetch");
      const data: RecommendationResponse = await response.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setResult(null);
    }
    setLoading(false);
  };

  const handleSearch = async () => {
    if (!region.trim()) return;
    try {
      const res = await fetch("https://api.tanzaniaregions.com/api/v1/regions");
      if (!res.ok) throw new Error("Failed to fetch regions");
      const json = await res.json();
      const regions = json.data as Array<{
        name: string;
        latitude: number;
        longitude: number;
      }>;

      const matchedRegion = regions.find(
        (r) => r.name.toLowerCase() === region.toLowerCase()
      );

      if (matchedRegion && matchedRegion.latitude && matchedRegion.longitude) {
        setLatitude(matchedRegion.latitude);
        setLongitude(matchedRegion.longitude);
      } else {
        alert("Region not found.");
      }
    } catch (error) {
      console.error("Error fetching regions:", error);
      alert("Could not fetch regions.");
    }
  };

  return (
    <div className="mx-auto p-6 font-sans">
      {/* Image Banner with Overlay and Welcome */}
      <div className="relative w-full h-64 mb-10 rounded-xl overflow-hidden shadow-lg">
        <img
          src={images[currentImageIndex]}
          alt="Agriculture"
          className="w-full h-full object-cover transition duration-1000"
        />
        <div className="absolute inset-0 bg-black bg-opacity-40 z-10"></div>
        <div className="absolute z-20 top-10 left-1/2 transform -translate-x-1/2 bg-white bg-opacity-90 px-6 py-4 rounded-xl shadow-xl text-center max-w-md">
          <h1 className="text-2xl font-bold text-green-700 mb-2">
            🌾 Welcome to Smart Crop Advisor
          </h1>
          <p className="text-gray-700 text-sm">
            Select a region or click on the map to get AI-based crop
            recommendations tailored to Tanzanian agriculture.
          </p>
        </div>
      </div>

      {/* Region Search Input */}
      <div className="flex flex-col md:flex-row items-center gap-4 mb-6">
        <input
          type="text"
          placeholder="Search regions..."
          value={region}
          onChange={(e) => setRegion(e.target.value)}
          onKeyDown={(e) =>
            e.key === "Enter" && (e.preventDefault(), handleSearch())
          }
          className="w-full md:w-80 px-4 py-3 rounded-lg border border-gray-300 text-gray-700 text-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
        />
        <button
          onClick={handleSearch}
          type="button"
          className="bg-green-600 hover:bg-green-700 text-white font-semibold px-6 py-3 rounded-lg shadow-md"
        >
          Search
        </button>
      </div>

      {/* Google Map */}
      <div id="map" className="w-full h-96 rounded-xl shadow-lg mb-8"></div>

      {/* Coordinates + Submit */}
      <form
        onSubmit={handleSubmit}
        className="flex flex-wrap items-center gap-4"
      >
        <label className="font-semibold text-gray-700">
          Latitude:
          <input
            type="text"
            value={latitude ?? ""}
            readOnly
            className="ml-2 w-40 px-3 py-2 border border-gray-300 rounded-lg bg-gray-100"
          />
        </label>
        <label className="font-semibold text-gray-700">
          Longitude:
          <input
            type="text"
            value={longitude ?? ""}
            readOnly
            className="ml-2 w-40 px-3 py-2 border border-gray-300 rounded-lg bg-gray-100"
          />
        </label>
        <button
          type="submit"
          disabled={!latitude || !longitude || loading}
          className={`px-8 py-3 rounded-lg font-bold text-white shadow-md transition ${
            latitude && longitude && !loading
              ? "bg-green-600 hover:bg-green-700"
              : "bg-green-300 cursor-not-allowed"
          }`}
        >
          {loading ? "Loading..." : "Get Recommendations"}
        </button>
      </form>

      {/* Result */}
      {result && (
        <section className="mt-12">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-green-100 p-5 rounded-lg shadow font-semibold">
              🌡️ Temperature: {result.weather.temperature}°C
            </div>
            <div className="bg-green-100 p-5 rounded-lg shadow font-semibold">
              💧 Humidity: {result.weather.humidity}%
            </div>
            <div className="bg-green-100 p-5 rounded-lg shadow font-semibold">
              🌧️ Rainfall: {result.weather.rainfall}mm
            </div>
            <div className="bg-green-100 p-5 rounded-lg shadow font-semibold truncate">
              📍 Location: {result.location.latitude.toFixed(4)},{" "}
              {result.location.longitude.toFixed(4)}
            </div>
          </div>

          <h2 className="text-2xl font-bold mb-4">Recommendations</h2>
          <div className="flex flex-col gap-6">
            {Object.entries(result.recommendations).map(
              ([crop, info]) => (
                <div
                  key={crop}
                  className="bg-yellow-50 rounded-xl shadow-md flex flex-col sm:flex-row overflow-hidden"
                >
                  <img
                    src={farm}
                    alt={crop}
                    className="w-full sm:w-44 h-32 sm:h-auto object-cover"
                  />

                  <div className="p-4 flex flex-col justify-between">
                    <h3 className="text-xl font-semibold">{crop}</h3>
                    <p className="text-gray-700">{info.explanation}</p>
                    <p className="text-green-700 font-bold">
                      Score: {(info.score * 100).toFixed(2)}%
                    </p>
                  </div>
                </div>
              )
            )}
          </div>
        </section>
      )}

      {loading && !result && (
        <p className="mt-6 text-center font-semibold text-gray-600 animate-pulse">
          Loading recommendations...
        </p>
      )}
    </div>
  );
};

export default CropRecommendation;
