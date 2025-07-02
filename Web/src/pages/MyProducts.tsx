import React, { useEffect, useState } from "react";
import axios from "axios";
import { User } from "../UserContext";
import { useNavigate } from "react-router-dom";

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
  seller_id: string;
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

export default function MyProducts() {
  const { user: currentUser } = User();
  const navigate = useNavigate();

  const [items, setItems] = useState<MarketplaceItem[]>([]);
  const [showForm, setShowForm] = useState(false);
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
    if (!currentUser?.isAuthenticated || !currentUser?.idNumber) {
      navigate("/login");
    } else {
      fetchItems();
    }
  }, [currentUser]);

  const fetchItems = async () => {
    try {
      const res = await axios.get<MarketplaceItem[]>(API_BASE);
      const userItems = res.data.filter(
        (item) => item.seller_id === currentUser.idNumber
      );
      setItems(userItems);
    } catch {
      alert("Failed to load your items.");
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

  if (!currentUser?.idNumber) {
    alert("User ID is missing. Please update your profile.");
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
  data.append("seller_id", currentUser.idNumber); 

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
    if (!window.confirm("Delete this item?")) return;
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
        <h1 className="text-2xl font-bold">My Products</h1>
        <button
          onClick={() => openForm()}
          className="bg-primary text-white px-4 py-2 rounded"
        >
          + Add Product
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {items.map((item) => (
          <div
            key={item.id}
            className="border p-4 rounded shadow relative"
          >
            {item.image && (
              <img
                src={item.image}
                alt={item.name}
                className="w-full h-40 object-cover mb-3 rounded"
              />
            )}
            <h2 className="text-lg font-bold">{item.name}</h2>
            <p className="text-gray-600">{item.description}</p>
            <p className="text-sm text-gray-500 mt-1">
              Location: {item.location} | Contact: {item.contact_info}
            </p>
            <p className="mt-2 font-semibold">{item.price.toFixed(2)} /=</p>
            <div className="flex justify-between mt-3">
              <button
                onClick={() => openForm(item)}
                className="text-blue-600 hover:underline"
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

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">
              {formData.id ? "Edit Product" : "Add New Product"}
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
              rows={3}
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
                if (file) setFormData((prev) => ({ ...prev, image: file }));
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
              className="w-full mb-3 p-2 border rounded"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowForm(false)}
                className="px-4 py-2 border rounded"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                className="bg-primary text-white px-4 py-2 rounded"
              >
                {formData.id ? "Update" : "Add"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
