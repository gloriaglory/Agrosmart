import React, { useEffect, useState } from "react";
import axios from "axios";

interface MarketplaceItem {
  id: number | string;
  title: string;
  description: string;
  price: number;
  image?: string;
}

interface FormData {
  id?: number | string | null;
  title: string;
  description: string;
  price: string;
  image: string;
}

const API_BASE = "http://localhost:8000/market/items/";

export default function Marketplace() {
  const [items, setItems] = useState<MarketplaceItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    id: null,
    title: "",
    description: "",
    price: "",
    image: "",
  });

  // Fetch all items
  const fetchItems = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get<MarketplaceItem[]>(API_BASE);
      setItems(res.data);
    } catch (err) {
      setError("Failed to load marketplace items.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  // Open form for new or edit
  const openForm = (item?: MarketplaceItem) => {
    if (item) {
      setFormData({
        id: item.id,
        title: item.title,
        description: item.description,
        price: item.price.toString(),
        image: item.image || "",
      });
    } else {
      setFormData({ id: null, title: "", description: "", price: "", image: "" });
    }
    setShowForm(true);
  };

  // Handle form input changes
  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Submit form for create or update
  const handleSubmit = async () => {
    if (!formData.title.trim() || !formData.description.trim() || !formData.price.trim()) {
      alert("Please fill in all required fields.");
      return;
    }

    const payload = {
      title: formData.title.trim(),
      description: formData.description.trim(),
      price: parseFloat(formData.price),
      image: formData.image.trim() || null,
    };

    try {
      if (formData.id) {
        // Update existing
        await axios.put(`${API_BASE}${formData.id}/`, payload);
      } else {
        // Create new
        await axios.post(API_BASE, payload);
      }
      setShowForm(false);
      fetchItems();
    } catch {
      alert("Failed to save item. Please check your inputs.");
    }
  };

  // Delete an item
  const deleteItem = async (id: number | string) => {
    if (!window.confirm("Are you sure you want to delete this item?")) return;
    try {
      await axios.delete(`${API_BASE}${id}/`);
      fetchItems();
    } catch {
      alert("Failed to delete item.");
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-3xl font-bold">Marketplace</h1>
        <button
          onClick={() => openForm()}
          className="bg-primary text-white px-4 py-2 rounded hover:bg-primary/80"
        >
          + Add Item
        </button>
      </div>

      {loading && <p>Loading items...</p>}
      {error && <p className="text-red-600">{error}</p>}

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {items.map((item) => (
          <div
            key={item.id}
            className="border rounded shadow hover:shadow-lg p-4 flex flex-col"
          >
            {item.image ? (
              <img
                src={item.image}
                alt={item.title}
                className="w-full h-40 object-cover rounded mb-3"
              />
            ) : (
              <div className="w-full h-40 bg-gray-200 rounded mb-3 flex items-center justify-center text-gray-500">
                No image
              </div>
            )}
            <h2 className="text-xl font-semibold">{item.title}</h2>
            <p className="text-gray-700 flex-grow">{item.description}</p>
            <p className="font-bold mt-2">${item.price.toFixed(2)}</p>
            <div className="mt-3 flex justify-between">
              <button
                onClick={() => openForm(item)}
                className="text-primary hover:underline"
              >
                Edit
              </button>
              <button
                onClick={() => deleteItem(item.id)}
                className="text-red-600 hover:underline"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Modal Form */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded p-6 w-full max-w-md shadow-lg relative">
            <h2 className="text-2xl font-bold mb-4">
              {formData.id ? "Edit Item" : "Add New Item"}
            </h2>
            <input
              type="text"
              name="title"
              placeholder="Title"
              value={formData.title}
              onChange={handleInputChange}
              className="w-full mb-3 p-2 border rounded"
            />
            <textarea
              name="description"
              placeholder="Description"
              value={formData.description}
              onChange={handleInputChange}
              className="w-full mb-3 p-2 border rounded"
              rows={4}
            />
            <input
              type="number"
              step="0.01"
              name="price"
              placeholder="Price"
              value={formData.price}
              onChange={handleInputChange}
              className="w-full mb-3 p-2 border rounded"
            />
            <input
              type="text"
              name="image"
              placeholder="Image URL (optional)"
              value={formData.image}
              onChange={handleInputChange}
              className="w-full mb-4 p-2 border rounded"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowForm(false)}
                className="px-4 py-2 border rounded bg-primary text-white hover:bg-primary/80"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                className="bg-white text-primary px-4 py-2 rounded border border-green-300 hover:bg-primary/20"
              >
                {formData.id ? "Update" : "Add"}
              </button>
            </div>
            <button
              onClick={() => setShowForm(false)}
              className="absolute top-2 right-2 text-gray-500 hover:text-black text-xl"
              aria-label="Close form"
            >
              &times;
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
