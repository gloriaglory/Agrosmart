import { API_URL } from "./config";
import { crops } from "./components/Crops";

export const MARKET_API = `${API_URL}/market/items/`;

export interface MarketplaceItem {
  id: number;
  seller: number | null;
  seller_name: string | null;
  name: string;
  description: string;
  price: string;
  image: string | null;
  category: string;
  quantity: number;
  region: string;
  location: string;
  contact_info: string;
  created_at: string;
}

export interface RegionSummary {
  region: string;
  listings: number;
  crops: { name: string; listings: number; avg_price: number }[];
}

export const CATEGORIES = [
  "Cereals",
  "Legumes",
  "Vegetables",
  "Fruits",
  "Roots & tubers",
  "Cash crops",
  "Other",
];

// Stock photo for a crop name (e.g. "MAIZE" -> maize.png), used when a listing has no image.
const stockImages = new Map(crops.map((c) => [c.name.toLowerCase(), c.image]));
export const cropImage = (item: Pick<MarketplaceItem, "name" | "image">) =>
  item.image || stockImages.get(item.name.trim().toLowerCase()) || null;

// "MAIZE" -> "Maize"
export const titleCase = (s: string) =>
  s.trim().toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());
