import { createContext, useContext, useState, useEffect } from "react";

interface User {
  isAuthenticated: boolean;
  idNumber?: string | null;
}

const defaultUser: User = {
  isAuthenticated: false,
  idNumber: null,
};

const UserContext = createContext<{
  user: User;
  setUser: (user: User) => void;
}>({
  user: defaultUser,
  setUser: () => {},
});

export const UserProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User>(defaultUser);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const idNumber = localStorage.getItem("idNumber");
    if (token) {
      setUser({ isAuthenticated: true, idNumber });
    }
  }, []);

  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  );
};

export const User = () => useContext(UserContext);
