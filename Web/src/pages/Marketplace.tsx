import PageHero from "../components/PageHero";
// Soko la Kilombero, Arusha. Photo: Wikimedia Commons, CC0 (public domain)
import marketHeroImg from "../assets/images/market-hero.jpg";
import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate, useSearchParams } from "react-router-dom";
import { tanzaniaRegions } from "../components/regions";
import { MARKET_API, cropImage, type MarketplaceItem } from "../market";
import { useUser } from "../UserContext";
import { formatPrice } from "../format";
import PriceTrends from "../components/PriceTrends";

class MarketplaceErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("Marketplace Error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="page text-center">
          <h2 className="section-title">Something went wrong.</h2>
          <p className="muted mt-2">{this.state.error?.message}</p>
        </div>
      );
    }
    return this.props.children;
  }
}

const regionNames = tanzaniaRegions.map((r) => r.name).sort();

export default function MarketplaceViewer() {
  const [items, setItems] = useState<MarketplaceItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedItem, setSelectedItem] = useState<MarketplaceItem | null>(
    null,
  );
  const [searchParams, setSearchParams] = useSearchParams();
  const region = searchParams.get("region") ?? "";
  const tab = searchParams.get("tab") === "trends" ? "trends" : "listings";

  const setParam = (key: string, value: string | null) => {
    const next = new URLSearchParams(searchParams);
    if (value) next.set(key, value);
    else next.delete(key);
    setSearchParams(next, { replace: true });
  };
  const [search, setSearch] = useState(searchParams.get("search") ?? "");

  const navigate = useNavigate();
  const { user } = useUser();

  useEffect(() => {
    const controller = new AbortController();
    const timer = setTimeout(async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await axios.get<MarketplaceItem[]>(MARKET_API, {
          params: {
            region: region || undefined,
            search: search.trim() || undefined,
          },
          signal: controller.signal,
        });
        setItems(res.data);
      } catch (err) {
        if (!axios.isCancel(err)) setError("Failed to load marketplace items.");
      } finally {
        setLoading(false);
      }
    }, 250);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [region, search]);

  const setRegion = (value: string) => {
    const next = new URLSearchParams(searchParams);
    if (value) next.set("region", value);
    else next.delete("region");
    setSearchParams(next, { replace: true });
  };

  const selectedImage = selectedItem ? cropImage(selectedItem) : null;

  return (
    <MarketplaceErrorBoundary>
      <div>
        <PageHero
          image={marketHeroImg}
          imageStyle="clear"
          imagePosition="center 70%"
          title="Marketplace"
          subtitle="Fresh produce listed directly by farmers verified with their NIDA number."
        >
          <button onClick={() => navigate("/products")} className="btn-primary">
            {user?.is_seller ? "Sell your produce" : "Become a seller"}
          </button>
        </PageHero>
        <div className="page">
          {/* Tabs */}
          <div
            className="mb-8 flex gap-1 border-b border-stone-200"
            role="tablist"
          >
            {[
              { key: "listings", label: "Listings" },
              { key: "trends", label: "Price trends" },
            ].map((t) => (
              <button
                key={t.key}
                role="tab"
                aria-selected={tab === t.key}
                onClick={() =>
                  setParam("tab", t.key === "trends" ? "trends" : null)
                }
                className={`-mb-px border-b-2 px-4 py-2.5 text-sm font-semibold transition-colors ${
                  tab === t.key
                    ? "border-primary text-primary"
                    : "border-transparent text-stone-500 hover:text-stone-800"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>

          {tab === "trends" ? (
            <PriceTrends
              initialCrop={searchParams.get("crop")}
              onCropChange={(crop) => setParam("crop", crop)}
            />
          ) : (
            <>
              <div className="mb-8 flex flex-col gap-3 sm:flex-row">
                <input
                  type="search"
                  placeholder="Search crops, e.g. maize"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="input sm:max-w-sm"
                  aria-label="Search listings"
                />
                <select
                  value={region}
                  onChange={(e) => setRegion(e.target.value)}
                  className="input sm:w-56"
                  aria-label="Filter by region"
                >
                  <option value="">All regions</option>
                  {regionNames.map((r) => (
                    <option key={r} value={r}>
                      {r}
                    </option>
                  ))}
                </select>
              </div>

              {loading && items.length === 0 && (
                <p className="muted">Loading items…</p>
              )}
              {error && <p className="alert-error">{error}</p>}
              {!loading && !error && items.length === 0 && (
                <div className="card p-10 text-center">
                  <p className="font-medium text-stone-900">
                    {region || search
                      ? "No listings match your filters"
                      : "No items listed yet"}
                  </p>
                  <p className="muted mt-1">
                    {region || search
                      ? "Try another region or search term."
                      : "Check back soon, or list your own produce."}
                  </p>
                </div>
              )}

              <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {items.map((item) => {
                  const img = cropImage(item);
                  return (
                    <button
                      key={item.id}
                      className="card card-hover flex flex-col overflow-hidden text-left"
                      onClick={() => setSelectedItem(item)}
                    >
                      {img ? (
                        <img
                          src={img}
                          alt={item.name}
                          className="h-44 w-full object-cover"
                        />
                      ) : (
                        <div className="flex h-44 w-full items-center justify-center bg-stone-100 text-sm text-stone-400">
                          No image
                        </div>
                      )}
                      <div className="flex flex-1 flex-col p-4">
                        <div className="flex items-start justify-between gap-3">
                          <h2 className="font-semibold text-stone-900">
                            {item.name}
                          </h2>
                          <span className="shrink-0 font-semibold text-primary">
                            {formatPrice(item.price)}
                          </span>
                        </div>
                        <p className="mt-1 flex-1 text-sm text-stone-600 line-clamp-2">
                          {item.description}
                        </p>
                        <p className="mt-3 text-xs text-stone-500">
                          {[item.location, item.region]
                            .filter(Boolean)
                            .join(", ")}
                        </p>
                      </div>
                    </button>
                  );
                })}
              </div>
            </>
          )}

          {selectedItem && (
            <div
              className="modal-backdrop"
              onClick={() => setSelectedItem(null)}
            >
              <div
                className="modal max-w-3xl p-0"
                onClick={(e) => e.stopPropagation()}
                role="dialog"
                aria-modal="true"
              >
                <div className="grid md:grid-cols-2">
                  {selectedImage ? (
                    <img
                      src={selectedImage}
                      alt={selectedItem.name}
                      className="h-64 w-full object-cover md:h-full"
                    />
                  ) : (
                    <div className="flex h-64 items-center justify-center bg-stone-100 text-sm text-stone-400 md:h-full">
                      No image
                    </div>
                  )}
                  <div className="flex flex-col p-6">
                    <div className="flex items-start justify-between gap-4">
                      <h2 className="text-xl font-semibold text-stone-900">
                        {selectedItem.name}
                      </h2>
                      <button
                        onClick={() => setSelectedItem(null)}
                        className="btn-ghost -mr-2 -mt-1 px-2 py-1 text-xs"
                      >
                        Close
                      </button>
                    </div>
                    <p className="mt-1 text-lg font-semibold text-primary">
                      {formatPrice(selectedItem.price)}
                    </p>
                    <p className="mt-4 text-sm text-stone-600">
                      {selectedItem.description}
                    </p>

                    <dl className="mt-6 grid grid-cols-2 gap-4 border-t border-stone-200 pt-4 text-sm">
                      <div>
                        <dt className="stat-label">Category</dt>
                        <dd className="mt-1 text-stone-900">
                          {selectedItem.category}
                        </dd>
                      </div>
                      <div>
                        <dt className="stat-label">Quantity</dt>
                        <dd className="mt-1 text-stone-900">
                          {selectedItem.quantity} kg
                        </dd>
                      </div>
                      <div>
                        <dt className="stat-label">Region</dt>
                        <dd className="mt-1 text-stone-900">
                          {selectedItem.region || "—"}
                        </dd>
                      </div>
                      <div>
                        <dt className="stat-label">Town / city</dt>
                        <dd className="mt-1 text-stone-900">
                          {selectedItem.location}
                        </dd>
                      </div>
                      <div>
                        <dt className="stat-label">Seller</dt>
                        <dd className="mt-1 text-stone-900">
                          {selectedItem.seller_name || "—"}
                        </dd>
                      </div>
                      <div>
                        <dt className="stat-label">Contact</dt>
                        <dd className="mt-1 text-stone-900">
                          {selectedItem.contact_info}
                        </dd>
                      </div>
                    </dl>

                    <a
                      href={`tel:${selectedItem.contact_info}`}
                      className="btn-primary mt-6 py-2.5"
                    >
                      Contact seller
                    </a>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </MarketplaceErrorBoundary>
  );
}
