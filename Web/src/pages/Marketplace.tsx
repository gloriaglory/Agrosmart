import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

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
        <div className="text-center text-red-600 p-10">
          <h2 className="text-2xl font-bold mb-2">Something went wrong.</h2>
          <p>{this.state.error?.message}</p>
        </div>
      );
    }
    return this.props.children;
  }
}

interface MarketplaceItem {
  id: number | string;
  name: string;
  description: string;
  price: number;
  image?: string;
  category: string;
  quantity: number;
  location: string;
  contact_info: string;
}

const API_BASE = "http://localhost:8000/market/items/";

export default function MarketplaceViewer() {
  const [items, setItems] = useState<MarketplaceItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedItem, setSelectedItem] = useState<MarketplaceItem | null>(null);

  const navigate = useNavigate(); // 👈 Hook to navigate

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get<MarketplaceItem[]>(API_BASE);
      setItems(res.data);
    } catch {
      setError("Failed to load marketplace items.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <MarketplaceErrorBoundary>
      <div className="mb-4 flex justify-between items-center">
          <h1 className="text-3xl font-bold">Marketplace</h1>

          {/* Become a Seller button */}
          <button
            onClick={() => navigate("/products")}
            className="bg-primary text-white px-4 py-4 rounded hover:bg-primary/80"
          >
            Become a Seller
          </button>
        </div>
      <div className="max-w-6xl mx-auto p-4">
        <div className="mb-4">
          <h1 className="text-3xl font-bold">Marketplace</h1>
        </div>

        {loading && <p>Loading items...</p>}
        {error && <p className="text-red-600">{error}</p>}

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
          {items.map((item) => (
            <div
              key={item.id}
              className="border rounded shadow hover:shadow-lg p-4 flex flex-col"
              onClick={() => setSelectedItem(item)}
            >
              {item.image ? (
                <img
                  src={item.image}
                  alt={item.name}
                  className="w-full h-40 object-cover rounded mb-3"
                />
              ) : (
                <div className="w-full h-40 bg-gray-200 rounded mb-3 flex items-center justify-center text-gray-500">
                  No image
                </div>
              )}
              <h2 className="text-xl font-semibold">{item.name}</h2>
              <p className="text-gray-700 flex-grow line-clamp-2">
                {item.description}
              </p>
              <p className="text-gray-600 text-sm">Location: {item.location}</p>
              <p className="font-bold mt-2">{Number(item.price).toFixed(2)} /=</p>
            </div>
          ))}
        </div>

        {selectedItem && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-3xl flex gap-6">
              <img
                src={selectedItem.image || ""}
                alt={selectedItem.name}
                className="w-1/2 h-full object-cover rounded"
              />
              <div className="w-1/2 relative">
                <button
                  onClick={() => setSelectedItem(null)}
                  className="absolute top-2 right-2 text-gray-500 hover:text-black text-xl"
                  aria-label="Close content view"
                >
                  &times;
                </button>
                <h2 className="text-2xl font-bold mb-2">{selectedItem.name}</h2>
                <p className="text-gray-700 flex-grow pb-5">
                  {selectedItem.description}
                </p>
                <div className="flex items-center justify-between gap-4 mb-2">
                  <span className="text-gray-600">
                    Category: {selectedItem.category}
                  </span>
                  <span className="text-gray-600">
                    Quantity: {selectedItem.quantity}Kg
                  </span>
                </div>
                <div className="flex items-center justify-between gap-4 mb-2">
                  <span className="text-gray-600">
                    Contact: {selectedItem.contact_info}
                  </span>
                  <span className="text-gray-600">
                    Location: {selectedItem.location}
                  </span>
                </div>
                <p className="font-bold text-xl mt-2">
                  {Number(selectedItem.price).toFixed(2)} /=
                </p>

                <a
                  href={`tel:${selectedItem.contact_info}`}
                  className="mt-4 text-center inline-block px-4 py-2 w-80 bg-primary text-white rounded hover:bg-primary/65"
                >
                  Contact Seller
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    </MarketplaceErrorBoundary>
  );
}
