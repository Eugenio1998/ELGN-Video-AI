// 📁 pages/login.tsx

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import Link from "next/link";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/auth/login`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        }
      );

      const data = await res.json();

      console.log("🔐 Dados recebidos do backend:", data);

      if (!res.ok) {
        setErrorMsg(
          data?.detail?.[0]?.msg ||
            data?.message ||
            "❌ Falha ao efetuar login."
        );
        return;
      }

      // Salva dados no localStorage
      localStorage.setItem("token", data.token);
      localStorage.setItem("plan", data.plan || "free");
      localStorage.setItem("userId", data.user_id);
      localStorage.setItem("userName", data.username);
      localStorage.setItem("userImage", data.image_url || "/img/user.png");
      localStorage.setItem("userRole", data.role || "USER");
      localStorage.setItem("userStatus", "ativo"); // ✅ Considerar ativo após login

      // Limpa formulário
      setEmail("");
      setPassword("");

      // Redireciona com base no role
      const role = (data.role || "").toUpperCase();
      if (role === "ADMIN") {
        router.push("/admin");
      } else {
        router.push("/dashboard");
      }
    } catch (error) {
      console.error("Erro de login:", error);
      setErrorMsg("❌ Erro ao conectar com o servidor.");
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-[url('/img/Mario02.gif')] bg-cover bg-center bg-no-repeat bg-fixed px-4">
      <div className="absolute inset-0 bg-gradient-to-b from-black/30 to-black/60 z-0" />

      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.9 }}
        whileHover={{ scale: 1.02, rotate: 0.3 }}
        className="relative z-10 w-full max-w-md p-8 rounded-xl border border-green-500 shadow-[0_0_30px_5px_rgba(0,255,100,0.3)] bg-black/70 backdrop-blur-xl"
      >
        <h1 className="text-3xl font-extrabold text-center text-green-300 drop-shadow-[0_0_10px_lime] mb-6">
          🔐 Entrar no ELGN Video AI
        </h1>

        {errorMsg && (
          <div className="bg-red-600 text-white px-4 py-2 rounded text-sm mb-4 text-center animate-pulse">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-white mb-1" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              aria-label="Digite seu e-mail"
              className="w-full px-4 py-2 rounded bg-gray-800 text-white border border-gray-600 focus:ring-2 focus:ring-green-400 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-white mb-1" htmlFor="password">
              Senha
            </label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              aria-label="Digite sua senha"
              className="w-full px-4 py-2 rounded bg-gray-800 text-white border border-gray-600 focus:ring-2 focus:ring-green-400 focus:outline-none"
            />
          </div>

          <button
            type="submit"
            className="w-full py-2 bg-gradient-to-r from-green-500 to-blue-600 text-white font-bold rounded hover:scale-105 transition-transform"
          >
            ✅ Entrar
          </button>

          <div className="text-center mt-4">
            <Link
              href="/register"
              className="text-sm text-green-300 hover:underline"
            >
              Não tem conta? Criar agora
            </Link>
          </div>
        </form>
      </motion.div>
    </div>
  );
}
