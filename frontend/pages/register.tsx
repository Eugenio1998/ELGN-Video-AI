// 📁 pages/register.tsx

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import Link from "next/link";

type FormFields = {
  email: string;
  fullName: string;
  displayName: string;
  password: string;
};

export default function RegisterPage() {
  const router = useRouter();
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [errorMsg, setErrorMsg] = useState("");
  const [form, setForm] = useState<FormFields>({
    email: "",
    fullName: "",
    displayName: "",
    password: "",
  });

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!form.email.includes("@")) newErrors.email = "Email inválido";
    if (form.password.length < 6) newErrors.password = "Mínimo de 6 caracteres";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const getPasswordStrength = () => {
    const length = form.password.length;
    const hasNumbers = /\d/.test(form.password);
    const hasSymbols = /[!@#$%^&*(),.?":{}|<>]/.test(form.password);
    const hasUpper = /[A-Z]/.test(form.password);

    if (length >= 10 && hasNumbers && hasSymbols && hasUpper) return "Forte";
    if (length >= 8 && (hasNumbers || hasSymbols)) return "Moderada";
    return "Fraca";
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
    setErrors((prev) => ({ ...prev, [name]: "" }));
    setErrorMsg("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      const res = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: form.email,
          password: form.password,
          username: form.displayName,
        }),
      });

      const data = await res.json();
      console.log("🔎 Resposta da API:", data);

      if (!res.ok) {
        let msg = "Erro desconhecido.";

        type BackendError = { field?: string; msg: string };

        if (Array.isArray(data.error)) {
          msg = (data.error as BackendError[]).map((d) => d.msg).join(" | ");
        } else if (typeof data.error === "string") {
          msg = data.error;
        }

        setErrorMsg(msg);
        return;
      }

      localStorage.setItem("token", data.token);
      localStorage.setItem("plan", data.plan || "basic");
      localStorage.setItem("userId", data.user_id);
      localStorage.setItem("userName", form.displayName);
      localStorage.setItem("userImage", "/img/user.png");

      router.push("/dashboard");
    } catch (error) {
      console.error("Erro ao registrar:", error);
      setErrorMsg(
        "Falha ao criar conta. Verifique sua conexão ou tente mais tarde."
      );
    }
  };

  const passwordStrength = getPasswordStrength();

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-[url('/img/Mario02.gif')] bg-cover bg-center bg-no-repeat bg-fixed px-4">
      <div className="absolute inset-0 bg-gradient-to-b from-black/30 to-black/50 z-0" />

      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
        whileHover={{ scale: 1.01, rotate: 0.3 }}
        className="relative z-10 w-full max-w-lg p-8 rounded-xl border border-cyan-500 shadow-[0_0_30px_5px_rgba(0,255,255,0.3)] bg-black/70 backdrop-blur-xl"
      >
        <h1 className="text-3xl font-extrabold text-center text-cyan-300 drop-shadow-[0_0_10px_cyan] mb-6">
          📝 Criar Conta no ELGN Video AI
        </h1>

        {errorMsg && (
          <div className="bg-red-600 text-white px-4 py-2 rounded text-sm mb-4 text-center animate-pulse">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {[
            { name: "email", label: "Email", type: "email" },
            { name: "fullName", label: "Nome Completo", type: "text" },
            {
              name: "displayName",
              label: "Nome de Usuário no Software",
              type: "text",
            },
            { name: "password", label: "Senha", type: "password" },
          ].map((field) => (
            <div key={field.name}>
              <label htmlFor={field.name} className="block text-white mb-1">
                {field.label}
              </label>
              <input
                id={field.name}
                type={field.type}
                name={field.name}
                value={form[field.name as keyof FormFields]}
                onChange={handleChange}
                required
                className={`w-full px-4 py-2 rounded bg-gray-800 text-white border ${
                  errors[field.name]
                    ? "border-red-500"
                    : "border-gray-600 focus:ring-2 focus:ring-cyan-400"
                } focus:outline-none`}
              />
              {field.name === "password" && form.password && (
                <p
                  className={`text-sm mt-1 ${
                    passwordStrength === "Forte"
                      ? "text-green-400"
                      : passwordStrength === "Moderada"
                        ? "text-yellow-400"
                        : "text-red-400"
                  }`}
                >
                  Segurança da senha: {passwordStrength}
                </p>
              )}
              {errors[field.name] && (
                <p className="text-sm text-red-400 mt-1">
                  {errors[field.name]}
                </p>
              )}
            </div>
          ))}

          <button
            type="submit"
            className="w-full py-2 bg-gradient-to-r from-green-500 to-blue-600 text-white font-bold rounded hover:scale-105 transition-transform"
          >
            ✅ Criar Conta
          </button>

          <div className="text-center mt-4">
            <Link
              href="/login"
              className="text-sm text-cyan-300 hover:underline"
            >
              Já tem conta? Entrar
            </Link>
          </div>
        </form>
      </motion.div>
    </div>
  );
}
