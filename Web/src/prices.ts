import { API_URL } from "./config";

export const PRICES_API = `${API_URL}/api/prices/`;

export type CropSummary = {
  commodity: string;
  category: string;
  price_type: "wholesale" | "retail";
  price: number;
  date: string;
  change_pct: number | null;
};

export const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

// "2026-08" -> "Aug 2026"
export const monthLabel = (ym: string) => {
  const [y, m] = ym.split("-").map(Number);
  return `${MONTHS[m - 1]} ${y}`;
};
