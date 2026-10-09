import { authHeaders } from "../config";
import PageHero from "../components/PageHero";
import productsHeroImg from "../assets/images/nuts.png";
import React, { useCallback, useEffect, useState } from "react";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";
import { useUser } from "../UserContext";
import { formatPrice } from "../format";
import { tanzaniaRegions } from "../components/regions";
import {
  CATEGORIES,
  MARKET_API,
  cropImage,
  type MarketplaceItem,
} from "../market";

interface FormData {
  id: number | null;
  name: string;
  description: string;
  price: string;
  image: File | null;
  category: string;
  quantity: string;
  region: string;
  location: string;
  contact_info: string;
}

const regionNames = tanzaniaRegions.map((r) => r.name).sort();

export default function MyProducts() {
  const { user, loading } = useUser();
  const navigate = useNavigate();

  const emptyForm = useCallback(
    (): FormData => ({
      id: null,
      name: "",
      description: "",
      price: "",
      image: null,
      category: "",
      quantity: "",
      region: "",
      location: "",
      contact_info: user?.phone_number || "",
    }),
    [user],
  );

  const [items, setItems] = useState<MarketplaceItem[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<FormData>(emptyForm);
  const [error, setError] = useState<string | null>(null);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);

  const fetchItems = useCallback(async () => {
    try {
      const res = await axios.get<MarketplaceItem[]>(`${MARKET_API}mine/`, {
        headers: authHeaders(),
      });
      setItems(res.data);
    } catch {
      setError("Failed to load your items.");
    }
  }, []);

  useEffect(() => {
    if (loading) return;
    if (!user) navigate("/login", { state: { from: "/products" } });
    else if (user.is_seller) fetchItems();
  }, [loading, user, navigate, fetchItems]);

  const openForm = (item?: MarketplaceItem) => {
    setFormErrors({});
    setFormData(
      item
        ? {
            id: item.id,
            name: item.name,
            description: item.description,
            price: String(Number(item.price)),
            image: null,
            category: item.category,
            quantity: String(item.quantity),
            region: item.region,
            location: item.location,
            contact_info: item.contact_info,
          }
        : emptyForm(),
    );
    setShowForm(true);
  };

  const handleInputChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setFormErrors((prev) => ({ ...prev, [name]: "" }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormErrors({});

    const data = new FormData();
    data.append("name", formData.name.trim());
    data.append("description", formData.description.trim());
    data.append("price", formData.price);
    data.append("category", formData.category);
    data.append("quantity", formData.quantity);
    data.append("region", formData.region);
    data.append("location", formData.location.trim());
    data.append("contact_info", formData.contact_info.trim());
    if (formData.image) data.append("image", formData.image);

    setSaving(true);
    try {
      const config = { headers: authHeaders() };
      if (formData.id) {
        await axios.patch(`${MARKET_API}${formData.id}/`, data, config);
      } else {
        await axios.post(MARKET_API, data, config);
      }
      setShowForm(false);
      fetchItems();
    } catch (err) {
      const res = axios.isAxiosError(err) ? err.response : null;
      if (res?.data && typeof res.data === "object") {
        const errors: Record<string, string> = {};
        for (const [k, v] of Object.entries(res.data))
          errors[k] = Array.isArray(v) ? v.join(" ") : String(v);
        setFormErrors(errors);
      } else {
        setFormErrors({
          detail: "Failed to save item. Please check your inputs.",
        });
      }
    } finally {
      setSaving(false);
    }
  };

  const deleteItem = async (id: number) => {
    if (!window.confirm("Delete this item?")) return;
    try {
      await axios.delete(`${MARKET_API}${id}/`, { headers: authHeaders() });
      fetchItems();
    } catch {
      setError("Failed to delete item.");
    }
  };

  const fieldError = (name: string) =>
    formErrors[name] ? (
      <p className="mt-1 text-xs text-red-600">{formErrors[name]}</p>
    ) : null;

  if (loading || !user) {
    return (
      <div className="page">
        <p className="muted">Loading…</p>
      </div>
    );
  }

  if (!user.is_seller) {
    return (
      <div>
        <PageHero
          image={productsHeroImg}
          title="Sell on AgroSmart"
          subtitle="To protect buyers from scams, only sellers registered with their NIDA number can list produce."
        >
          <Link to="/profile" className="btn-primary">
            Add your NIDA number
          </Link>
        </PageHero>
      </div>
    );
  }

  const categoryOptions =
    formData.category && !CATEGORIES.includes(formData.category)
      ? [formData.category, ...CATEGORIES]
      : CATEGORIES;

  return (
    <div>
      <PageHero
        image={productsHeroImg}
        title="My Products"
        subtitle="Manage the produce you sell on the marketplace."
      >
        <button onClick={() => openForm()} className="btn-primary">
          Add product
        </button>
      </PageHero>
      <div className="page">
        {error && <p className="alert-error mb-6">{error}</p>}

        {items.length === 0 && !error && (
          <div className="card p-10 text-center">
            <p className="font-medium text-stone-900">
              You have no products yet
            </p>
            <p className="muted mt-1">
              Add your first product to start selling.
            </p>
          </div>
        )}

        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {items.map((item) => {
            const img = cropImage(item);
            return (
              <div
                key={item.id}
                className="card card-hover flex flex-col overflow-hidden"
              >
                {img ? (
                  <img
                    src={img}
                    alt={item.name}
                    className="h-40 w-full object-cover"
                  />
                ) : (
                  <div className="flex h-40 items-center justify-center bg-stone-100 text-sm text-stone-400">
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
                    {[item.location, item.region].filter(Boolean).join(", ") ||
                      "No region set"}{" "}
                    · {item.quantity} kg
                  </p>
                  <div className="mt-4 flex gap-2 border-t border-stone-100 pt-4">
                    <button
                      onClick={() => openForm(item)}
                      className="btn-secondary flex-1"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => deleteItem(item.id)}
                      className="btn-danger flex-1"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {showForm && (
          <div className="modal-backdrop">
            <form
              onSubmit={handleSubmit}
              className="modal max-w-lg"
              role="dialog"
              aria-modal="true"
            >
              <h2 className="text-lg font-semibold text-stone-900">
                {formData.id ? "Edit product" : "Add new product"}
              </h2>

              <div className="mt-5 grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label htmlFor="name" className="label">
                    Crop name
                  </label>
                  <input
                    id="name"
                    type="text"
                    name="name"
                    placeholder="e.g. Maize"
                    value={formData.name}
                    onChange={handleInputChange}
                    className="input"
                    required
                  />
                  {fieldError("name")}
                </div>
                <div className="col-span-2">
                  <label htmlFor="description" className="label">
                    Description
                  </label>
                  <textarea
                    id="description"
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    className="input"
                    rows={3}
                    required
                  />
                  {fieldError("description")}
                </div>
                <div>
                  <label htmlFor="price" className="label">
                    Price (TZS)
                  </label>
                  <input
                    id="price"
                    type="number"
                    min="0"
                    name="price"
                    value={formData.price}
                    onChange={handleInputChange}
                    className="input"
                    required
                  />
                  {fieldError("price")}
                </div>
                <div>
                  <label htmlFor="quantity" className="label">
                    Quantity (kg)
                  </label>
                  <input
                    id="quantity"
                    type="number"
                    min="1"
                    name="quantity"
                    value={formData.quantity}
                    onChange={handleInputChange}
                    className="input"
                    required
                  />
                  {fieldError("quantity")}
                </div>
                <div className="col-span-2">
                  <label htmlFor="category" className="label">
                    Category
                  </label>
                  <select
                    id="category"
                    name="category"
                    value={formData.category}
                    onChange={handleInputChange}
                    className="input"
                    required
                  >
                    <option value="" disabled>
                      Select a category
                    </option>
                    {categoryOptions.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </select>
                  {fieldError("category")}
                </div>
                <div>
                  <label htmlFor="region" className="label">
                    Region
                  </label>
                  <select
                    id="region"
                    name="region"
                    value={formData.region}
                    onChange={handleInputChange}
                    className="input"
                    required
                  >
                    <option value="" disabled>
                      Select a region
                    </option>
                    {regionNames.map((r) => (
                      <option key={r} value={r}>
                        {r}
                      </option>
                    ))}
                  </select>
                  {fieldError("region")}
                </div>
                <div>
                  <label htmlFor="location" className="label">
                    Town / city
                  </label>
                  <input
                    id="location"
                    type="text"
                    name="location"
                    placeholder="e.g. Kondoa"
                    value={formData.location}
                    onChange={handleInputChange}
                    className="input"
                    required
                  />
                  {fieldError("location")}
                </div>
                <div className="col-span-2">
                  <label htmlFor="contact_info" className="label">
                    Contact phone
                  </label>
                  <input
                    id="contact_info"
                    type="tel"
                    name="contact_info"
                    value={formData.contact_info}
                    onChange={handleInputChange}
                    className="input"
                    required
                  />
                  {fieldError("contact_info")}
                </div>
                <div className="col-span-2">
                  <label htmlFor="image" className="label">
                    Photo{" "}
                    <span className="font-normal text-stone-400">
                      (optional)
                    </span>
                  </label>
                  <input
                    id="image"
                    type="file"
                    name="image"
                    accept="image/*"
                    onChange={(e) => {
                      const file = e.target.files?.[0] ?? null;
                      setFormData((prev) => ({ ...prev, image: file }));
                    }}
                    className="input"
                  />
                  {fieldError("image")}
                </div>
              </div>

              {(formErrors.detail || formErrors.non_field_errors) && (
                <p className="alert-error mt-4">
                  {formErrors.detail || formErrors.non_field_errors}
                </p>
              )}

              <div className="mt-6 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button type="submit" disabled={saving} className="btn-primary">
                  {saving
                    ? "Saving…"
                    : formData.id
                      ? "Save changes"
                      : "Add product"}
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
