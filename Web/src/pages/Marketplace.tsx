import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { User } from "../UserContext";
import axios from "axios";

// Error Boundary Component
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

// Interfaces
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

interface FormData {
  id?: number | string | null;
  name: string;
  description: string;
  price: string;
  image: string | File;
  category: string;
  quantity: string;
  location: string;
  contact_info: string;
}

const API_BASE = "http://localhost:8000/market/items/";

export default function Marketplace() {
  const { user: currentUser, setUser } = User();
  const [items, setItems] = useState<MarketplaceItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [showForm, setShowForm] = useState(false);
  const [showLoginPrompt, setShowLoginPrompt] = useState(false);
  const [showIdPrompt, setShowIdPrompt] = useState(false);
  const [idNumberInput, setIdNumberInput] = useState("");
  const [selectedItem, setSelectedItem] = useState<MarketplaceItem | null>(null);

  const navigate = useNavigate();
  const location = useLocation();

  const handleLoginClick = () => {
    setShowLoginPrompt(false);
    navigate("/login", { state: { from: location.pathname } });
  };

  const [formData, setFormData] = useState<FormData>({
    id: null,
    name: "",
    description: "",
    price: "",
    image: "",
    category: "",
    quantity: "",
    location: "",
    contact_info: "",
  });

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

  const openForm = (item?: MarketplaceItem) => {
    if (item) {
      setFormData({
        id: item.id,
        name: item.name,
        description: item.description,
        price: item.price.toString(),
        image: item.image || "",
        category: item.category,
        quantity: item.quantity.toString(),
        location: item.location,
        contact_info: item.contact_info,
      });
    } else {
      setFormData({
        id: null,
        name: "",
        description: "",
        price: "",
        image: "",
        category: "",
        quantity: "",
        location: "",
        contact_info: "",
      });
    }
    setShowForm(true);
  };

  const handleAddClick = () => {
  if (!currentUser?.isAuthenticated) {
    setShowLoginPrompt(true);
    return;
  }
  if (!currentUser.idNumber) {
    setShowIdPrompt(true);
    return;
  }
  openForm();
};


  const saveIdNumber = async () => {
    if (!idNumberInput.trim()) {
      alert("Please enter your ID number.");
      return;
    }
    try {
      const token = localStorage.getItem("token");
      await axios.post(
        "http://localhost:8000/api/auth/user/idnumber/",
        { id_number: idNumberInput.trim() },
        { headers: { Authorization: `Token ${token}` } }
      );

      // Save in localStorage for persistence
      localStorage.setItem("idNumber", idNumberInput.trim());

      // Update UserContext state
      setUser({
        ...currentUser,
        idNumber: idNumberInput.trim(),
      });

      setShowIdPrompt(false);
      openForm();
    } catch {
      alert("Failed to save ID number. Please try again.");
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async () => {
    if (!formData.name || !formData.description || !formData.price) {
      alert("Please fill in all required fields.");
      return;
    }

    const data = new FormData();
    data.append("name", formData.name.trim());
    data.append("description", formData.description.trim());
    data.append("price", formData.price);
    data.append("category", formData.category.trim());
    data.append("quantity", formData.quantity);
    data.append("location", formData.location.trim());
    data.append("contact_info", formData.contact_info.trim());

    if (formData.image instanceof File) {
      data.append("image", formData.image);
    }

    try {
      if (formData.id) {
        await axios.put(`${API_BASE}${formData.id}/`, data, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      } else {
        await axios.post(API_BASE, data, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      }
      setShowForm(false);
      fetchItems();
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Failed to save item. Please check your inputs.");
    }
  };

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
    <MarketplaceErrorBoundary>
      <div className="max-w-6xl mx-auto p-4">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-3xl font-bold">Marketplace</h1>
          <button
            onClick={handleAddClick}
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
              <div className="mt-3 flex justify-between">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    openForm(item);
                  }}
                  className="text-primary hover:underline"
                >
                  Edit
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteItem(item.id);
                  }}
                  className="text-red-600 hover:underline"
                >
                  Delete
                </button>
              </div>
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

        {showForm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded p-6 w-full max-w-md shadow-lg relative">
              <h2 className="text-2xl font-bold mb-4">
                {formData.id ? "Edit Item" : "Add New Item"}
              </h2>
              <input
                type="text"
                name="name"
                placeholder="Name"
                value={formData.name}
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
                name="price"
                placeholder="Price"
                value={formData.price}
                onChange={handleInputChange}
                className="w-full mb-3 p-2 border rounded"
              />
              <input
                type="file"
                name="image"
                accept="image/*"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    setFormData((prev) => ({ ...prev, image: file }));
                  }
                }}
                className="w-full mb-3 p-2 border rounded"
              />
              <input
                type="text"
                name="category"
                placeholder="Category"
                value={formData.category}
                onChange={handleInputChange}
                className="w-full mb-3 p-2 border rounded"
              />
              <input
                type="number"
                name="quantity"
                placeholder="Quantity"
                value={formData.quantity}
                onChange={handleInputChange}
                className="w-full mb-3 p-2 border rounded"
              />
              <input
                type="text"
                name="location"
                placeholder="Location"
                value={formData.location}
                onChange={handleInputChange}
                className="w-full mb-3 p-2 border rounded"
              />
              <input
                type="text"
                name="contact_info"
                placeholder="Contact Info"
                value={formData.contact_info}
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

        {showLoginPrompt && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded p-6 max-w-sm w-full shadow-lg">
              <h2 className="text-xl font-bold mb-4">Please Log In</h2>
              <p className="mb-4">You need to be logged in to add a new item.</p>
              <button
                onClick={handleLoginClick}
                className="bg-primary text-white px-4 py-2 rounded"
              >
                Log In
              </button>

              <button
                onClick={() => setShowLoginPrompt(false)}
                className="ml-4 px-4 py-2 border rounded"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {showIdPrompt && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded p-6 max-w-sm w-full shadow-lg">
              <h2 className="text-xl mb-4">Add Your NIN to continue</h2>
              <input
                type="text"
                value={idNumberInput}
                onChange={(e) => setIdNumberInput(e.target.value)}
                placeholder="Enter your ID number"
                className="w-full mb-4 p-2 border rounded"
              />
              <div className="flex justify-end gap-2">
                <button
                  onClick={() => setShowIdPrompt(false)}
                  className="px-4 py-2 border rounded"
                >
                  Cancel
                </button>
                <button
                  onClick={saveIdNumber}
                  className="bg-primary text-white px-4 py-2 rounded"
                >
                  Save
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </MarketplaceErrorBoundary>
  );
}
