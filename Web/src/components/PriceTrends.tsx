import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import {
  Area,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { MONTHS, PRICES_API, monthLabel, type CropSummary } from "../prices";

type Detail = {
  commodity: string;
  price_type: "wholesale" | "retail";
  region: string;
  current: {
    price: number;
    date: string;
    change_pct: number | null;
    markets: number;
    stale: boolean;
  };
  history: { month: string; price: number }[];
  outlook: { month: string; low: number; typical: number; high: number }[];
  outlook_hit_rate_pct: number | null;
  seasonality: {
    months: { month: number; index_pct: number }[];
    best_month: number;
    cheapest_month: number;
    spread_pct: number;
  } | null;
  regions: {
    region: string;
    price: number;
    date: string;
    markets: number;
    stale: boolean;
  }[];
  source: { name: string; url: string; license: string };
};

const MONTHS_LONG = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

const tzs = (n: number) => `TZS ${Math.round(n).toLocaleString()}`;

const AXIS = { fontSize: 12, fill: "#78716c" };
const GRID = "#e7e5e4";
const GREEN = "#166534";

// Neutral colour: a rise is good for sellers but bad for buyers
export const ChangeBadge = ({ pct }: { pct: number | null }) => {
  if (pct === null) return <span className="text-stone-400">no change data</span>;
  const flat = Math.abs(pct) < 0.05;
  return (
    <span className="font-medium text-stone-600">
      {flat ? "No change" : `${pct > 0 ? "+" : ""}${pct.toFixed(1)}%`} vs last month
    </span>
  );
};

type Props = {
  initialCrop?: string | null;
  onCropChange?: (crop: string) => void;
};

// Real market prices from WFP: current price, 3-month outlook range,
// seasonal pattern and prices by region.
export default function PriceTrends({ initialCrop, onCropChange }: Props) {
  const [crops, setCrops] = useState<CropSummary[]>([]);
  const [crop, setCrop] = useState<string>(initialCrop || "");
  const [region, setRegion] = useState<string>("");
  const [detail, setDetail] = useState<Detail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    axios
      .get<{ commodities: CropSummary[] }>(PRICES_API)
      .then((res) => {
        setCrops(res.data.commodities);
        if (!res.data.commodities.length) setLoading(false);
        setCrop((current) => {
          const names = res.data.commodities.map((c) => c.commodity);
          if (current && names.includes(current)) return current;
          return names.includes("Maize") ? "Maize" : names[0] || "";
        });
      })
      .catch(() => {
        setError("Could not load market prices.");
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (!crop) return;
    setLoading(true);
    setError(null);
    axios
      .get<Detail>(`${PRICES_API}detail/`, {
        params: { commodity: crop, region: region || undefined },
      })
      .then((res) => setDetail(res.data))
      .catch((err) => {
        setDetail(null);
        setError(
          axios.isAxiosError(err) && err.response?.data?.error
            ? err.response.data.error
            : "Could not load prices.",
        );
      })
      .finally(() => setLoading(false));
  }, [crop, region]);

  const chooseCrop = (name: string) => {
    setCrop(name);
    setRegion("");
    onCropChange?.(name);
  };

  // History (last 3 years) joined to the outlook band so the chart reads left to right
  const chartData = useMemo(() => {
    if (!detail) return [];
    const recent = detail.history
      .slice(-36)
      .map(
        (h) => ({ month: h.month, price: h.price }) as Record<string, unknown>,
      );
    if (recent.length && detail.outlook.length) {
      const last = recent[recent.length - 1];
      last.range = [last.price, last.price];
      last.typical = last.price;
    }
    return [
      ...recent,
      ...detail.outlook.map((o) => ({
        month: o.month,
        range: [o.low, o.high],
        typical: o.typical,
      })),
    ];
  }, [detail]);

  const regionsByPrice = useMemo(
    () =>
      detail
        ? [...detail.regions].sort(
            (a, b) => Number(a.stale) - Number(b.stale) || b.price - a.price,
          )
        : [],
    [detail],
  );

  if (!loading && !crops.length && !error) {
    return (
      <div className="card p-10 text-center">
        <p className="font-medium text-stone-900">
          No market prices loaded yet
        </p>
        <p className="muted mt-1">
          An admin can load them with{" "}
          <code className="rounded bg-stone-100 px-1">
            python manage.py refresh_prices
          </code>
          .
        </p>
      </div>
    );
  }

  const season = detail?.seasonality;
  const strongSeason = season && season.spread_pct >= 3;
  const lastOutlook = detail?.outlook[detail.outlook.length - 1];

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-col gap-3 sm:flex-row">
          <select
            value={crop}
            onChange={(e) => chooseCrop(e.target.value)}
            className="input sm:w-56"
            aria-label="Crop"
          >
            {crops.map((c) => (
              <option key={c.commodity} value={c.commodity}>
                {c.commodity}
              </option>
            ))}
          </select>
          <select
            value={region}
            onChange={(e) => setRegion(e.target.value)}
            className="input sm:w-56"
            aria-label="Region"
          >
            <option value="">All Tanzania</option>
            {detail?.regions.map((r) => (
              <option key={r.region} value={r.region}>
                {r.region}
              </option>
            ))}
          </select>
        </div>
        {detail && (
          <p className="text-xs text-stone-500">
            {detail.price_type === "wholesale" ? "Wholesale" : "Retail"} prices
            per kg · latest data {monthLabel(detail.current.date)}
          </p>
        )}
      </div>

      {error && <p className="alert-error">{error}</p>}
      {loading && !detail && <p className="muted">Loading prices…</p>}

      {detail && (
        <div
          className={`space-y-6 transition-opacity ${loading ? "opacity-60" : ""}`}
        >
          {/* Headline numbers */}
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="card p-5">
              <p className="stat-label">
                {detail.commodity} · {detail.region}
              </p>
              <p className="stat-value">
                {tzs(detail.current.price)}
                <span className="text-base font-medium text-stone-500">
                  {" "}
                  /kg
                </span>
              </p>
              <p className="mt-1 text-xs">
                <ChangeBadge pct={detail.current.change_pct} />
              </p>
              <p className="mt-1 text-xs text-stone-500">
                {monthLabel(detail.current.date)} · average of{" "}
                {detail.current.markets} market
                {detail.current.markets === 1 ? "" : "s"}
                {detail.current.stale && " · older data for this region"}
              </p>
            </div>
            <div className="card p-5">
              <p className="stat-label">
                Likely in{" "}
                {lastOutlook ? monthLabel(lastOutlook.month) : "3 months"}
              </p>
              <p className="stat-value">
                {lastOutlook
                  ? `${tzs(lastOutlook.low)} – ${lastOutlook.high.toLocaleString()}`
                  : "—"}
              </p>
              <p className="mt-1 text-xs text-stone-500">
                A range, not a promise: based on how prices moved from this time
                of year in the last 10 years.
              </p>
            </div>
            <div className="card p-5">
              <p className="stat-label">Best time to sell</p>
              {strongSeason ? (
                <>
                  <p className="stat-value">
                    {MONTHS_LONG[season.best_month - 1]}
                  </p>
                  <p className="mt-1 text-xs text-stone-500">
                    Usually cheapest in {MONTHS_LONG[season.cheapest_month - 1]}
                    . Prices typically swing about {season.spread_pct}% over the
                    year.
                  </p>
                </>
              ) : (
                <>
                  <p className="stat-value">Any month</p>
                  <p className="mt-1 text-xs text-stone-500">
                    No strong seasonal pattern for this crop.
                  </p>
                </>
              )}
            </div>
          </div>

          <div className="grid gap-5 lg:grid-cols-3">
            {/* History + outlook */}
            <div className="card p-6 lg:col-span-2">
              <h3 className="font-medium text-stone-900">
                Price history and 3-month outlook
              </h3>
              <p className="muted">
                TZS per kg. The shaded area is the likely range.
                {detail.outlook_hit_rate_pct !== null &&
                  ` Tested on the past year, real prices landed inside it ${detail.outlook_hit_rate_pct}% of the time.`}
              </p>
              <div className="mt-4 h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart
                    data={chartData}
                    margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
                  >
                    <CartesianGrid stroke={GRID} vertical={false} />
                    <XAxis
                      dataKey="month"
                      tick={AXIS}
                      tickLine={false}
                      axisLine={{ stroke: GRID }}
                      tickFormatter={monthLabel}
                      minTickGap={24}
                    />
                    <YAxis
                      tick={AXIS}
                      tickLine={false}
                      axisLine={false}
                      domain={["auto", "auto"]}
                      width={56}
                    />
                    <Tooltip
                      labelFormatter={(label) => monthLabel(String(label))}
                      formatter={(value: unknown, name: string) => {
                        if (Array.isArray(value))
                          return [
                            `${tzs(value[0])} – ${tzs(value[1])}`,
                            "Likely range",
                          ];
                        return [
                          tzs(Number(value)),
                          name === "price" ? "Price" : "Typical",
                        ];
                      }}
                    />
                    {detail.outlook.length > 0 && (
                      <ReferenceLine
                        x={detail.current.date}
                        stroke="#a8a29e"
                        strokeDasharray="3 3"
                        label={{
                          value: "Today",
                          position: "insideTopRight",
                          fontSize: 11,
                          fill: "#78716c",
                        }}
                      />
                    )}
                    <Area
                      dataKey="range"
                      stroke="none"
                      fill={GREEN}
                      fillOpacity={0.15}
                      isAnimationActive={false}
                    />
                    <Line
                      dataKey="price"
                      stroke={GREEN}
                      strokeWidth={2}
                      dot={false}
                      connectNulls
                    />
                    <Line
                      dataKey="typical"
                      stroke={GREEN}
                      strokeWidth={2}
                      strokeDasharray="5 4"
                      dot={false}
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
              {detail.outlook.length > 0 && (
                <div className="mt-4 grid grid-cols-3 gap-3 border-t border-stone-100 pt-4 text-sm">
                  {detail.outlook.map((o) => (
                    <div key={o.month}>
                      <p className="stat-label">{monthLabel(o.month)}</p>
                      <p className="mt-1 font-medium text-stone-900">
                        {o.low.toLocaleString()} – {o.high.toLocaleString()}
                      </p>
                      <p className="text-xs text-stone-500">
                        typical {o.typical.toLocaleString()}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Seasonal pattern */}
            <div className="card p-6">
              <h3 className="font-medium text-stone-900">
                Typical price through the year
              </h3>
              <p className="muted">
                Compared with the yearly average, over the last 15 years
              </p>
              {season ? (
                <div className="mt-4 h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={season.months.map((m) => ({
                        ...m,
                        name: MONTHS[m.month - 1],
                      }))}
                      margin={{ top: 10, right: 0, left: -10, bottom: 0 }}
                    >
                      <CartesianGrid stroke={GRID} vertical={false} />
                      <XAxis
                        dataKey="name"
                        tick={AXIS}
                        tickLine={false}
                        axisLine={{ stroke: GRID }}
                        interval={0}
                        fontSize={10}
                      />
                      <YAxis
                        tick={AXIS}
                        tickLine={false}
                        axisLine={false}
                        tickFormatter={(v) => `${v}%`}
                      />
                      <ReferenceLine y={0} stroke="#a8a29e" />
                      <Tooltip
                        formatter={(v: number) => [
                          `${v > 0 ? "+" : ""}${v}%`,
                          "vs yearly average",
                        ]}
                      />
                      <Bar dataKey="index_pct" radius={[3, 3, 0, 0]}>
                        {season.months.map((m) => (
                          <Cell
                            key={m.month}
                            fill={
                              m.month === season.best_month
                                ? GREEN
                                : m.index_pct >= 0
                                  ? "#4ade80"
                                  : "#d6d3d1"
                            }
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <p className="muted mt-6">
                  Not enough history to show a seasonal pattern.
                </p>
              )}
            </div>
          </div>

          {/* Prices by region */}
          <div className="card overflow-hidden">
            <div className="flex flex-wrap items-baseline justify-between gap-2 px-6 pt-5">
              <h3 className="font-medium text-stone-900">
                {detail.commodity} prices by region
              </h3>
              <p className="muted">
                Latest month for each region · click a row to see its trend
              </p>
            </div>
            <div className="mt-3 max-h-96 overflow-y-auto">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-stone-50 text-left text-xs uppercase tracking-wide text-stone-500">
                  <tr>
                    <th className="px-6 py-2 font-medium">Region</th>
                    <th className="px-6 py-2 text-right font-medium">
                      TZS / kg
                    </th>
                    <th className="hidden px-6 py-2 font-medium sm:table-cell">
                      Month
                    </th>
                    <th className="hidden px-6 py-2 text-right font-medium sm:table-cell">
                      Markets
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-100">
                  {regionsByPrice.map((r) => (
                    <tr
                      key={r.region}
                      onClick={() =>
                        setRegion(r.region === region ? "" : r.region)
                      }
                      className={`cursor-pointer transition-colors hover:bg-stone-50 ${
                        r.region === region ? "bg-primary-soft" : ""
                      } ${r.stale ? "text-stone-400" : "text-stone-800"}`}
                    >
                      <td className="px-6 py-2.5 font-medium">{r.region}</td>
                      <td className="px-6 py-2.5 text-right tabular-nums">
                        {r.price.toLocaleString()}
                      </td>
                      <td className="hidden px-6 py-2.5 sm:table-cell">
                        {monthLabel(r.date)}
                        {r.stale && " (old)"}
                      </td>
                      <td className="hidden px-6 py-2.5 text-right sm:table-cell">
                        {r.markets}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <p className="text-xs text-stone-500">
            Source:{" "}
            <a
              href={detail.source.url}
              target="_blank"
              rel="noreferrer"
              className="underline hover:text-stone-700"
            >
              {detail.source.name}
            </a>{" "}
            ({detail.source.license}). Prices are monthly market averages and
            can differ from farm-gate prices.
          </p>
        </div>
      )}
    </div>
  );
}
