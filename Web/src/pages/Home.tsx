import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import OurServices from "./OurServices";
import Maps from "../components/maps";
import heroImage from "../assets/images/farm1.jpeg";
import heroVideo from "../assets/videos/44765-440000959.mp4";
import Reveal from "../components/Reveal";
import CountUp from "../components/CountUp";
import { formatPrice } from "../format";
import { PRICES_API, monthLabel, type CropSummary } from "../prices";
import {
  MARKET_API,
  cropImage,
  titleCase,
  type MarketplaceItem,
  type RegionSummary,
} from "../market";

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

// Shared chart styling
const AXIS = { fontSize: 12, fill: "#78716c" };
const GRID = "#e7e5e4";
const GREEN = "#166534";
const PIE_COLORS = ["#14532d", "#166534", "#15803d", "#16a34a", "#4ade80", "#86efac", "#a8a29e", "#78716c"];

const prefersReducedMotion =
  typeof window !== "undefined" &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// Below this many listings the strip is shown as a static row instead of scrolling.
const MARQUEE_MIN = 6;

type Stats = { crops: number; regions: number; listings: number };

// Hero
const Hero = ({ stats }: { stats: Stats }) => (
  <section className="relative">
    <div className="relative flex min-h-[560px] items-center overflow-hidden bg-stone-900 pb-32 pt-20 lg:min-h-[640px]">
      <video
        className="absolute inset-0 h-full w-full object-cover opacity-70"
        src={heroVideo}
        poster={heroImage}
        autoPlay={!prefersReducedMotion}
        muted
        loop
        playsInline
        preload="auto"
        aria-hidden
      />
      <div className="absolute inset-0 bg-gradient-to-b from-stone-900/30 via-stone-900/40 to-stone-900/70" />
      <div className="container-x relative text-center">
        <p className="eyebrow text-green-300 animate-[pop-in_0.6s_ease-out]">
          Smart farming for Tanzania
        </p>
        <h1 className="mx-auto mt-4 max-w-4xl font-display text-4xl font-extrabold leading-tight tracking-tight text-white animate-[pop-in_0.8s_ease-out] sm:text-6xl">
          Grow the right crops and sell them at the right price.
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-white/85 animate-[pop-in_1s_ease-out]">
          Crop recommendations for your land, leaf disease checks, market
          prices and a marketplace to reach buyers, all in one place.
        </p>
      </div>
    </div>

    {/* Floating card overlapping the bottom of the hero */}
    <div className="container-x relative z-10 -mt-24 flex justify-center">
      <div className="w-full max-w-3xl rounded-[2rem] border border-stone-200 bg-white px-6 py-8 text-center shadow-2xl shadow-stone-900/10 animate-[pop-in_1.1s_ease-out] sm:px-10">
        <div className="grid grid-cols-3 divide-x divide-stone-200">
          {[
            { value: stats.crops, label: "Crops listed" },
            { value: stats.regions, label: "Regions selling" },
            { value: stats.listings, label: "Active listings" },
          ].map((s) => (
            <div key={s.label} className="px-2">
              <p className="font-display text-3xl font-extrabold text-primary sm:text-4xl">
                <CountUp end={s.value} />
              </p>
              <p className="mt-1 text-[11px] font-semibold uppercase tracking-wider text-stone-500 sm:text-xs">
                {s.label}
              </p>
            </div>
          ))}
        </div>
        <div className="mt-7 flex flex-wrap justify-center gap-3">
          <Link to="/crop_recommendation" className="btn-primary px-6 py-3">
            Get crop recommendations
          </Link>
          <Link to="/market" className="btn-secondary px-6 py-3">
            Visit marketplace
          </Link>
        </div>
      </div>
    </div>
  </section>
);

const CropCard = ({ item, hidden }: { item: MarketplaceItem; hidden?: boolean }) => {
  const img = cropImage(item);
  return (
    <Link
      to={`/market?search=${encodeURIComponent(item.name)}`}
      aria-hidden={hidden}
      tabIndex={hidden ? -1 : undefined}
      className="card block w-44 shrink-0 overflow-hidden transition duration-300 hover:-translate-y-1 hover:shadow-lg"
    >
      {img ? (
        <img src={img} alt={item.name} className="h-32 w-full bg-stone-100 object-cover" />
      ) : (
        <div className="flex h-32 items-center justify-center bg-stone-100 text-xs text-stone-400">
          No image
        </div>
      )}
      <div className="p-3.5">
        <h3 className="truncate font-display text-sm font-semibold text-stone-900">
          {titleCase(item.name)}
        </h3>
        <p className="mt-0.5 text-sm font-medium text-primary">{formatPrice(item.price)}</p>
        <p className="mt-1 truncate text-xs text-stone-500">
          {[item.location, item.region].filter(Boolean).join(", ")}
        </p>
      </div>
    </Link>
  );
};

// Latest marketplace listings
const CropMarquee = ({ items, loading }: { items: MarketplaceItem[]; loading: boolean }) => {
  const latest = items.slice(0, 20);
  return (
    <section>
      <Reveal className="section-head">
        <p className="eyebrow">Marketplace</p>
        <h2 className="mt-3">Featured crops</h2>
        <p>The latest produce listed by sellers across Tanzania.</p>
      </Reveal>

      {loading ? (
        <p className="muted text-center">Loading listings…</p>
      ) : latest.length === 0 ? (
        <div className="card mx-auto max-w-lg p-8 text-center">
          <p className="font-medium text-stone-900">No crops listed yet</p>
          <p className="muted mt-1">Registered sellers can be the first to list their produce.</p>
          <Link to="/products" className="btn-primary mt-5">
            Sell your produce
          </Link>
        </div>
      ) : latest.length < MARQUEE_MIN ? (
        <div className="flex flex-wrap justify-center gap-5">
          {latest.map((item) => (
            <CropCard key={item.id} item={item} />
          ))}
        </div>
      ) : (
        <div className="relative overflow-hidden [mask-image:linear-gradient(to_right,transparent,black_6%,black_94%,transparent)]">
          <div className="marquee-track flex w-max animate-marquee gap-5 py-2">
            {[...latest, ...latest].map((item, index) => (
              <CropCard key={index} item={item} hidden={index >= latest.length} />
            ))}
          </div>
        </div>
      )}

      {latest.length > 0 && (
        <div className="mt-8 text-center">
          <Link to="/market" className="btn-primary px-7 py-3">
            View marketplace
          </Link>
        </div>
      )}
    </section>
  );
};

// Real market prices (WFP) for the main crops, linking to the Marketplace trends tab
const MarketPricesStrip = () => {
  const [crops, setCrops] = useState<CropSummary[]>([]);

  useEffect(() => {
    axios
      .get<{ commodities: CropSummary[] }>(PRICES_API)
      .then((res) => setCrops(res.data.commodities))
      .catch(() => setCrops([]));
  }, []);

  if (!crops.length) return null;
  const latest = crops[0].date;

  return (
    <section>
      <Reveal className="section-head">
        <p className="eyebrow">Market prices</p>
        <h2 className="mt-3">Crop prices this month</h2>
        <p>
          Average wholesale prices across Tanzanian markets, {monthLabel(latest)}. Tap a crop to see its trend
          and 3-month outlook.
        </p>
      </Reveal>
      <Reveal className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {crops.slice(0, 8).map((c) => {
          const change = c.change_pct;
          return (
            <Link
              key={c.commodity}
              to={`/market?tab=trends&crop=${encodeURIComponent(c.commodity)}`}
              className="card card-hover p-5"
            >
              <p className="text-sm font-semibold text-stone-900">{c.commodity}</p>
              <p className="mt-2 font-display text-2xl font-bold text-primary">
                {c.price.toLocaleString()}
                <span className="ml-1 text-xs font-medium text-stone-500">TZS/kg</span>
              </p>
              <p className="mt-1 text-xs font-medium text-stone-600">
                {change === null
                  ? monthLabel(c.date)
                  : Math.abs(change) < 0.05
                    ? "No change this month"
                    : `${change > 0 ? "+" : ""}${change.toFixed(1)}% this month`}
              </p>
            </Link>
          );
        })}
      </Reveal>
      <div className="mt-8 text-center">
        <Link to="/market?tab=trends" className="btn-secondary px-6 py-2.5">
          See all price trends
        </Link>
      </div>
    </section>
  );
};

const EmptyChart = ({ text = "Not enough listings yet." }: { text?: string }) => (
  <div className="flex h-full items-center justify-center rounded-lg bg-stone-50 text-sm text-stone-400">
    {text}
  </div>
);

// Price trends, charts and regional map, all from marketplace listings
const PriceTrendsGraph = ({
  items,
  summaries,
}: {
  items: MarketplaceItem[];
  summaries: RegionSummary[];
}) => {
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null);

  const cropNames = useMemo(
    () => Array.from(new Set(items.map((i) => titleCase(i.name)))).sort(),
    [items]
  );
  const [selectedCrop, setSelectedCrop] = useState<string>("");
  const crop = selectedCrop || cropNames[0] || "";

  // Listing prices for the selected crop, oldest first
  const trendData = items
    .filter((i) => titleCase(i.name) === crop)
    .map((i) => ({ date: i.created_at, price: Number(i.price) }))
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  // Per-crop listing counts and average prices
  const perCrop = useMemo(() => {
    const map = new Map<string, { count: number; total: number }>();
    for (const i of items) {
      const name = titleCase(i.name);
      const entry = map.get(name) ?? { count: 0, total: 0 };
      entry.count++;
      entry.total += Number(i.price);
      map.set(name, entry);
    }
    return Array.from(map, ([name, { count, total }]) => ({
      name,
      listings: count,
      avgPrice: Math.round(total / count),
    }));
  }, [items]);

  const selectedSummary = summaries.find((s) => s.region === selectedRegion);

  return (
    <section>
      <Reveal className="section-head">
        <p className="eyebrow">Insights</p>
        <h2 className="mt-3">Prices and regional analysis</h2>
        <p>Live figures from crops listed on the marketplace.</p>
      </Reveal>

      <Reveal className="grid gap-5 lg:grid-cols-3">
        {/* Line chart */}
        <div className="card card-hover p-6 lg:col-span-2">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="font-medium text-stone-900">Listed price over time</h3>
              <p className="muted">Each point is one listing</p>
            </div>
            {cropNames.length > 0 && (
              <select
                aria-label="Select crop"
                className="input w-auto"
                value={crop}
                onChange={(e) => setSelectedCrop(e.target.value)}
              >
                {cropNames.map((name) => (
                  <option key={name} value={name}>
                    {name}
                  </option>
                ))}
              </select>
            )}
          </div>
          <div className="mt-4 h-72">
            {trendData.length === 0 ? (
              <EmptyChart />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid stroke={GRID} vertical={false} />
                  <XAxis
                    dataKey="date"
                    tick={AXIS}
                    tickLine={false}
                    axisLine={{ stroke: GRID }}
                    tickFormatter={(str) =>
                      new Date(str).toLocaleDateString(undefined, { month: "short", day: "numeric" })
                    }
                  />
                  <YAxis tick={AXIS} tickLine={false} axisLine={false} domain={["auto", "auto"]} />
                  <Tooltip
                    labelFormatter={(label) =>
                      new Date(label).toLocaleDateString(undefined, {
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                      })
                    }
                    formatter={(value: unknown) => [formatPrice(value as number), "Price"]}
                  />
                  <Line type="monotone" dataKey="price" stroke={GREEN} strokeWidth={2} dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Pie chart */}
        <div className="card card-hover p-6">
          <h3 className="font-medium text-stone-900">Listings by crop</h3>
          <p className="muted">Share of all listings</p>
          <div className="mt-4 h-72">
            {perCrop.length === 0 ? (
              <EmptyChart />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={perCrop}
                    dataKey="listings"
                    nameKey="name"
                    cx="50%"
                    cy="45%"
                    innerRadius={50}
                    outerRadius={85}
                    stroke="#fff"
                  >
                    {perCrop.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `${value} listing${value === 1 ? "" : "s"}`} />
                  <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 12 }} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Bar chart */}
        <div className="card card-hover p-6 lg:col-span-2">
          <h3 className="font-medium text-stone-900">Average listed price</h3>
          <p className="muted">TZS, per crop</p>
          <div className="mt-4" style={{ height: Math.max(240, perCrop.length * 34 + 40) }}>
            {perCrop.length === 0 ? (
              <EmptyChart />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={perCrop} layout="vertical" margin={{ top: 0, right: 20, left: 20, bottom: 0 }}>
                  <CartesianGrid stroke={GRID} horizontal={false} />
                  <XAxis type="number" tick={AXIS} tickLine={false} axisLine={{ stroke: GRID }} />
                  <YAxis dataKey="name" type="category" tick={AXIS} tickLine={false} axisLine={false} width={90} />
                  <Tooltip formatter={(value) => formatPrice(value as number)} cursor={{ fill: "#f5f5f4" }} />
                  <Bar dataKey="avgPrice" name="Average price" fill={GREEN} barSize={12} radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Map and region list */}
        <div className="card card-hover flex flex-col p-6">
          <h3 className="font-medium text-stone-900">Crops by region</h3>
          <p className="muted">Green markers have crops for sale. Click one.</p>
          <div className="mt-4 overflow-hidden rounded-lg">
            <Maps
              summaries={summaries}
              onSelectRegion={setSelectedRegion}
              selectedRegion={selectedRegion}
            />
          </div>
          <div className="mt-4 flex-1 text-sm">
            {!selectedRegion ? (
              <p className="muted">No region selected.</p>
            ) : selectedSummary ? (
              <>
                <p className="font-medium text-stone-900">For sale in {selectedRegion}</p>
                <ul className="mt-2 divide-y divide-stone-100">
                  {selectedSummary.crops.map((c) => (
                    <li key={c.name} className="flex justify-between gap-3 py-1.5">
                      <span className="text-stone-700">
                        {c.name}
                        <span className="text-stone-400"> · {c.listings}</span>
                      </span>
                      <span className="text-stone-900">avg {formatPrice(c.avg_price)}</span>
                    </li>
                  ))}
                </ul>
                <Link
                  to={`/market?region=${encodeURIComponent(selectedRegion)}`}
                  className="link-arrow mt-4"
                >
                  View listings <span aria-hidden>→</span>
                </Link>
              </>
            ) : (
              <p className="muted">No crops listed in {selectedRegion} yet.</p>
            )}
          </div>
        </div>
      </Reveal>
    </section>
  );
};

function Home() {
  const [items, setItems] = useState<MarketplaceItem[]>([]);
  const [summaries, setSummaries] = useState<RegionSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      axios.get<MarketplaceItem[]>(MARKET_API),
      axios.get<RegionSummary[]>(`${MARKET_API}regions/`),
    ])
      .then(([itemsRes, regionsRes]) => {
        setItems(itemsRes.data);
        setSummaries(regionsRes.data);
      })
      .catch((err) => console.error("Failed to load marketplace data", err))
      .finally(() => setLoading(false));
  }, []);

  const stats: Stats = {
    crops: new Set(items.map((i) => titleCase(i.name))).size,
    regions: summaries.length,
    listings: items.length,
  };

  return (
    <>
      <Hero stats={stats} />
      <div className="container-x space-y-24 pb-8 pt-20">
        <OurServices />
        <CropMarquee items={items} loading={loading} />
        <MarketPricesStrip />
        <PriceTrendsGraph items={items} summaries={summaries} />
      </div>
    </>
  );
}

export default Home;
