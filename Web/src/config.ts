// Backend address, set in Web/.env as VITE_API_URL
export const API_URL = (import.meta.env.VITE_API_URL ?? "http://localhost:8765").replace(/\/$/, "");

export const authHeaders = (): Record<string, string> => {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Token ${token}` } : {};
};
