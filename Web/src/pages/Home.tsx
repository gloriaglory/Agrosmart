import { useEffect, useRef, useState } from "react";
import { crops, type crop } from "../components/Crops";
import OurServices from "./OurServices";
import Maps from "../components/maps";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  BarChart,
  Bar,
} from "recharts";


// Crop Slider Component
const CropSlider = () => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const scrollSpeed = 0.5;
    let animationFrameId: number;

    const scroll = () => {
      const maxScrollLeft = container.scrollWidth - container.clientWidth;
      container.scrollLeft =
        container.scrollLeft >= maxScrollLeft
          ? 0
          : container.scrollLeft + scrollSpeed;
      animationFrameId = requestAnimationFrame(scroll);
    };

    animationFrameId = requestAnimationFrame(scroll);
    return () => cancelAnimationFrame(animationFrameId);
  }, []);

  // Filter for unique crops by name (show one card per crop type)
  const uniqueCropsMap: Map<string, crop> = new Map();
  for (const crop of crops) {
    if (!uniqueCropsMap.has(crop.name)) {
      uniqueCropsMap.set(crop.name, crop);
    }
  }
  const uniqueCrops = Array.from(uniqueCropsMap.values());

  return (
    <div className="relative w-full overflow-hidden py-4">
      <h3 className="text-lg font-semibold text-center mb-4">Featured Crops</h3>
      <div
        ref={containerRef}
        className="flex gap-4 whitespace-nowrap no-scrollbar"
        style={{ overflowX: "scroll", scrollBehavior: "auto" }}
      >
        {uniqueCrops.map((crop, index) => (
          <div
            key={index}
            className="inline-block min-w-[160px] bg-white rounded-xl shadow p-2"
          >
            <img
              src={crop.image}
              alt={crop.name}
              className="h-24 w-full object-cover rounded"
            />
            <h4 className="text-sm font-semibold mt-2">{crop.name}</h4>
            <p className="text-xs text-green-700">{crop.price}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

// Extract numeric price from TZS string
const parsePrice = (priceStr: string) => Number(priceStr.replace(/[^\d]/g, ""));

// Get unique crop names for filter dropdown
const uniqueCropNames = Array.from(new Set(crops.map((c) => c.name)));

// Main Graph and Map Section
const PriceTrendsGraph = () => {
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null);
  const [selectedCrop, setSelectedCrop] = useState<string>(uniqueCropNames[0]);

  // Filter crops by selected crop name, sort by date asc
  const cropPriceTrendData = crops
    .filter((crop) => crop.name === selectedCrop)
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    .map((crop) => ({
      date: crop.date,
      price: parsePrice(crop.price),
    }));

  // Filter available crops by region
  const availableCrops = crops.filter(
    (crop) => crop.status.toLowerCase() !== "sold"
  );

  const regionCropAverages = selectedRegion
    ? (() => {
        const filtered = availableCrops.filter(
          (crop) => crop.region === selectedRegion
        );

        const priceMap: Record<string, { total: number; count: number }> = {};

        for (const crop of filtered) {
          const price = parsePrice(crop.price);
          if (!priceMap[crop.name]) {
            priceMap[crop.name] = { total: 0, count: 0 };
          }
          priceMap[crop.name].total += price;
          priceMap[crop.name].count++;
        }

        return Object.entries(priceMap).map(([name, { total, count }]) => ({
          name,
          avgPrice: Math.round(total / count),
        }));
      })()
    : [];

  // Calculate average price per crop for Pie and Bar charts
  const avgPricePerCrop: Record<string, { total: number; count: number }> = {};
  crops.forEach(({ name, price }) => {
    const p = parsePrice(price);
    if (!avgPricePerCrop[name]) avgPricePerCrop[name] = { total: 0, count: 0 };
    avgPricePerCrop[name].total += p;
    avgPricePerCrop[name].count++;
  });

  // Pie chart data with average price per crop (unique crops)
  const pieData = Object.entries(avgPricePerCrop)
    .map(([name, { total, count }]) => ({
      name,
      value: Math.round(total / count),
    }))
    .filter((item) => item.value > 2000);

  // Bar chart data for average crop prices (same as pieData)
  const priceBarData = pieData;

  const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#AA336A"];
  const BAR_COLORS = [
    "#4ade80",
    "#60a5fa",
    "#facc15",
    "#f472b6",
    "#a78bfa",
    "#fb923c",
    "#22d3ee",
  ];

  const handleRegionSelect = (region: string) => {
    setSelectedRegion(region);
  };

  return (
    <div className="my-8">
      <div className="bg-green-100 rounded-lg p-6 mb-6 text-center shadow">
        <h1 className="text-3xl font-extrabold mb-2 text-green-900">
          Price Trends & Regional Analysis
        </h1>
        <p className="text-green-800">
          visualisation of crop prices and trends.
        </p>
      </div>

      {/* Crop Selector */}
      <div className="mb-4">
        <label htmlFor="crop-select" className="mr-2 font-medium">
          Select Crop:
        </label>
        <select
          id="crop-select"
          className="border border-gray-300 rounded px-2 py-1"
          value={selectedCrop}
          onChange={(e) => setSelectedCrop(e.target.value)}
        >
          {uniqueCropNames.map((cropName) => (
            <option key={cropName} value={cropName}>
              {cropName}
            </option>
          ))}
        </select>
      </div>

      <div className="flex flex-col py-14 lg:flex-row gap-6 mb-10">
        {/* Line Chart for Selected Crop Price Trend */}
        <div style={{ flex: 1, height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={cropPriceTrendData}
              margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tickFormatter={(str) => {
                  const date = new Date(str);
                  return date.toLocaleDateString(undefined, {
                    month: "short",
                    day: "numeric",
                  });
                }}
              />
              <YAxis domain={["dataMin - 100", "dataMax + 100"]} />
              <Tooltip
                labelFormatter={(label) =>
                  new Date(label).toLocaleDateString(undefined, {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })
                }
                formatter={(value: unknown) => [`TZS ${value}`, "Price"]}
              />
              <Line
                type="monotone"
                dataKey="price"
                stroke="#16a34a"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Pie Chart for Average Crop Prices */}
        <div style={{ flex: 1, height: 300 }}>
          <h2 className="text-center py-4">
            crops with price greater than 2000/=
          </h2>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                fill="#8884d8"
                label
              >
                {pieData.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `TZS ${value}`} />
              <Legend verticalAlign="bottom" height={36} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Bar Chart for Average Crop Prices */}
        <div className="w-full lg:w-1/2 h-[400px] bg-white p-4 rounded shadow">
          <h4 className="text-md font-medium text-center mb-2">
            Average Crop Prices (TZS/kg)
          </h4>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={priceBarData}
              layout="vertical"
              margin={{ top: 10, right: 30, left: 60, bottom: 10 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" />
              <Tooltip formatter={(value) => `TZS ${value}`} />
              <Legend />
              <Bar
                dataKey="value"
                fill="#34d399"
                barSize={14}
                isAnimationActive
              >
                {priceBarData.map((_, index) => (
                  <Cell
                    key={`price-bar-${index}`}
                    fill={BAR_COLORS[index % BAR_COLORS.length]}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Map and Region Crop List */}
        <div className="w-full lg:w-1/2 h-[400px] bg-white p-4 rounded shadow">
          <h4 className="text-md font-medium text-center mb-2">
            Select Region on Map
          </h4>
          <div className="h-[200px] mb-3">
            <Maps onSelectRegion={handleRegionSelect} />
          </div>
          {selectedRegion && (
            <div className="mt-2 text-sm">
              <p className="font-semibold text-center mb-1">
                Available Crops in {selectedRegion}:
              </p>
              <ul className="list-disc ml-5">
                {regionCropAverages.length > 0 ? (
                  regionCropAverages.map((crop, index) => (
                    <li key={index}>
                      {crop.name} – Avg: TZS {crop.avgPrice}
                    </li>
                  ))
                ) : (
                  <li>No available crops found.</li>
                )}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Home Page Component
function Home() {
  return (
    <div className="px-4 py-6">
      <CropSlider />
      <PriceTrendsGraph />
      <OurServices />
    </div>
  );
}

export default Home;
