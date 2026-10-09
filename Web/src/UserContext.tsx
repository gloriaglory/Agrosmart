import { createContext, useCallback, useContext, useEffect, useState } from "react";
import axios from "axios";
import { API_URL, authHeaders } from "./config";

export interface Profile {
  id: number;
  username: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  phone_number: string | null;
  id_number: string | null;
  nida_verified: boolean;
  nida_birth_date: string | null;
  role: "buyer" | "seller";
  is_seller: boolean;
  is_staff: boolean;
}

type UserContextValue = {
  user: Profile | null;
  loading: boolean;
  // Reload the profile from the backend (call after login or profile changes)
  refreshUser: () => Promise<Profile | null>;
  logout: () => void;
};

const UserContext = createContext<UserContextValue>({
  user: null,
  loading: true,
  refreshUser: async () => null,
  logout: () => {},
});

export const UserProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
  }, []);

  const refreshUser = useCallback(async () => {
    if (!localStorage.getItem("token")) {
      setUser(null);
      setLoading(false);
      return null;
    }
    try {
      const res = await axios.get<Profile>(`${API_URL}/api/auth/profile/`, {
        headers: authHeaders(),
      });
      setUser(res.data);
      return res.data;
    } catch {
      logout();
      return null;
    } finally {
      setLoading(false);
    }
  }, [logout]);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  return (
    <UserContext.Provider value={{ user, loading, refreshUser, logout }}>
      {children}
    </UserContext.Provider>
  );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useUser = () => useContext(UserContext);
