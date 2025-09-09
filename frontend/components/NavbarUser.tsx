// 📂 components/NavbarUser.tsx
"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Image from "next/image";
import { motion } from "framer-motion";
import axios from "axios";
import { useTranslation } from "react-i18next";

type UserType = {
  username: string;
  plan: string;
  avatarUrl?: string;
};

export default function NavbarUser() {
  const router = useRouter();
  const { t } = useTranslation();
  const [user, setUser] = useState<UserType | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    console.log("🔍 Token atual no NavbarUser:", token); // <- ADICIONE ISSO
    if (!token) {
      router.push("/login");
      return;
    }

    axios
      .get(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => setUser(res.data))
      .catch(() => {
        localStorage.clear();
        router.push("/login");
      });
  }, [router]);

  const handleLogout = () => {
    localStorage.clear();
    router.push("/login");
  };

  return (
    <nav className="relative bg-black text-white px-6 py-4 mb-6 rounded-xl border-2 border-white shadow-lg flex flex-wrap justify-between items-center">
      {/* 🔲 Neon branco pulsante */}
      <div className="pointer-events-none absolute -inset-1 rounded-xl border-2 border-white blur-md opacity-40 animate-pulse z-0" />

      <div className="relative z-10 flex gap-4 items-center">
        <motion.button
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
          onClick={() => router.push("/software")}
          className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-500 text-black font-bold rounded-lg hover:brightness-110 transition"
          aria-label={t("Software")}
        >
          🎬 {t("Software")}
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
          onClick={() => router.push("/runway")}
          className="px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-black font-bold rounded-lg hover:brightness-110 transition"
          aria-label={t("Creator")}
        >
          🧠 {t("Creator")}
        </motion.button>
      </div>

      <div className="relative z-10 flex items-center gap-4">
        {user?.avatarUrl && (
          <Image
            src={user.avatarUrl}
            alt="Avatar do usuário"
            width={48}
            height={48}
            className="rounded-full border-2 border-white shadow"
          />
        )}

        <div className="flex flex-col items-end mr-2 text-xs sm:text-sm">
          <span className="font-semibold text-white">{user?.username}</span>
          <span className="text-green-400 drop-shadow-[0_0_5px_#22c55e]">
            {user?.plan}
          </span>
        </div>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleLogout}
          className="px-3 py-2 bg-gradient-to-r from-red-500 to-orange-500 text-black font-bold rounded hover:brightness-110 transition"
          aria-label={t("Logout")}
        >
          {t("Logout")}
        </motion.button>
      </div>
    </nav>
  );
}
