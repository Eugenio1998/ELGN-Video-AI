// 📁 context/UserContext.tsx
"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import { fetchUser } from "../utils/fetchUser";

// 🧠 Tipo do usuário retornado da API
type UserType = {
  id: string;
  username: string;
  plan: string;
  avatarUrl?: string;
  normalizedPlan?: string;
  role?: "admin" | "user" | string;
};

type UserContextType = {
  user: UserType | null;
  loading: boolean;
  refreshUser: () => Promise<void>;
};

// 🔠 Função para normalizar plano (uso em Pro/Premium/Anual/etc.)
const normalizePlan = (plan: string): string =>
  plan
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");

const UserContext = createContext<UserContextType>({
  user: null,
  loading: true,
  refreshUser: async () => {},
});

export const UserProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserType | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = async () => {
    const token = localStorage.getItem("token");

    if (!token || typeof token !== "string") {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      const data = await fetchUser(token);
      setUser({
        id: data.id,
        username: data.username,
        plan: data.plan,
        avatarUrl: data.avatarUrl,
        role: data.role, // ✅ agora o role vai ser reconhecido
        normalizedPlan: normalizePlan(data.plan || "free"),
      });
    } catch {
      localStorage.removeItem("token");
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  return (
    <UserContext.Provider value={{ user, loading, refreshUser }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => useContext(UserContext);
