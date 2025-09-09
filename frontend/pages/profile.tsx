"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import toast, { Toaster } from "react-hot-toast";
import { useTranslation } from "react-i18next";
import { withAuth } from "../utils/withAuth";

function getPasswordStrength(password: string): "fraca" | "moderada" | "forte" {
  const hasNumber = /\d/.test(password);
  const hasUpper = /[A-Z]/.test(password);
  const hasSymbol = /[!@#$%^&*()_+[\]{};':"\\|,.<>/?]/.test(password);

  if (password.length >= 10 && hasNumber && hasUpper && hasSymbol)
    return "forte";
  if (password.length >= 6 && (hasNumber || hasUpper)) return "moderada";
  return "fraca";
}

function RenderProfileContent() {
  const router = useRouter();
  const { t } = useTranslation();

  const [form, setForm] = useState({
    name: "",
    displayName: "",
    email: "",
    phone: "",
    password: "",
    confirmPassword: "",
  });
  const [avatar, setAvatar] = useState<string | null>(null);
  const [passwordStrength, setPasswordStrength] = useState<
    "fraca" | "moderada" | "forte"
  >("fraca");

  useEffect(() => {
    const saved = {
      name: localStorage.getItem("userName") || "",
      displayName: localStorage.getItem("userDisplay") || "",
      email: localStorage.getItem("userEmail") || "",
      phone: localStorage.getItem("userPhone") || "",
    };
    setForm((prev) => ({ ...prev, ...saved }));
    const savedAvatar = localStorage.getItem("userAvatar");
    if (savedAvatar) setAvatar(savedAvatar);
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (name === "password") {
      setPasswordStrength(getPasswordStrength(value));
    }
  };

  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const token = localStorage.getItem("token");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/profile/avatar`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        }
      );
      const data = await res.json();
      setAvatar(data.avatar_url);
      localStorage.setItem("userAvatar", data.avatar_url);
      toast.success(t("profile.avatarSuccess"));
    } catch {
      toast.error(t("profile.avatarError"));
    }
  };

  const handleAvatarRemove = () => {
    setAvatar(null);
    localStorage.removeItem("userAvatar");
    toast(t("profile.avatarRemoved"), { icon: "🗑️" });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (form.password && form.password.length < 6) {
      toast.error(t("profile.passwordTooShort"));
      return;
    }
    if (form.password && form.password !== form.confirmPassword) {
      toast.error(t("profile.passwordMismatch"));
      return;
    }

    localStorage.setItem("userName", form.name);
    localStorage.setItem("userDisplay", form.displayName);
    localStorage.setItem("userEmail", form.email);
    localStorage.setItem("userPhone", form.phone);

    toast.success(t("profile.updated"));
  };

  const strengthColor = {
    fraca: "text-red-400",
    moderada: "text-yellow-300",
    forte: "text-green-400",
  };

  const strengthLabel = {
    fraca: t("profile.strengthWeak"),
    moderada: t("profile.strengthModerate"),
    forte: t("profile.strengthStrong"),
  };

  return (
    <div className="min-h-screen bg-[url('/img/user.png')] bg-cover bg-center bg-no-repeat bg-fixed flex items-center justify-center px-4 py-12 relative">
      <div className="absolute inset-0 bg-black/20 z-0" />
      <Toaster position="top-center" />

      <motion.form
        onSubmit={handleSubmit}
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="relative z-10 w-full max-w-2xl p-10 rounded-xl border-2 border-white shadow-lg bg-black/80 backdrop-blur-lg space-y-6"
      >
        <div className="pointer-events-none absolute -inset-1 rounded-xl border-2 border-white opacity-40 blur-md animate-pulse" />

        {/* Cabeçalho com botão à esquerda e título central */}
        <div className="flex items-center justify-between">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => router.push("/dashboard")}
            className="text-sm border-2 border-green-400 text-green-400 px-4 py-2 rounded-lg shadow hover:bg-green-500 hover:text-black transition"
            aria-label={t("profile.back")}
          >
            ← {t("profile.back")}
          </motion.button>
          <h1 className="text-3xl font-bold text-orange-400 drop-shadow-[0_0_10px_orange] text-center w-full -ml-12">
            👤 {t("profile.title")}
          </h1>
          <div className="w-[115px]" /> {/* Espaço para equilibrar o layout */}
        </div>

        {/* Avatar */}
        <div className="flex flex-col items-center gap-3">
          {avatar ? (
            <>
              <Image
                src={avatar}
                alt="Avatar"
                width={128}
                height={128}
                className="rounded-full border-4 border-white object-cover shadow"
              />
              <button
                onClick={handleAvatarRemove}
                type="button"
                className="text-sm text-red-400 hover:underline"
              >
                {t("profile.removeAvatar")}
              </button>
            </>
          ) : (
            <label className="text-sm text-white border border-white rounded px-4 py-2 cursor-pointer hover:bg-white hover:text-black transition">
              📸 {t("profile.uploadAvatar")}
              <input
                type="file"
                accept="image/*"
                onChange={handleAvatarUpload}
                hidden
              />
            </label>
          )}
        </div>

        {/* Campos */}
        {[
          { label: t("profile.fullName"), name: "name", type: "text" },
          {
            label: t("profile.displayName"),
            name: "displayName",
            type: "text",
          },
          { label: "Email", name: "email", type: "email" },
          { label: t("profile.phone"), name: "phone", type: "tel" },
          {
            label: t("profile.newPassword"),
            name: "password",
            type: "password",
          },
          {
            label: t("profile.confirmPassword"),
            name: "confirmPassword",
            type: "password",
          },
        ].map((field) => (
          <div key={field.name} className="space-y-1">
            <label className="text-sm font-medium text-white">
              {field.label}
            </label>
            <input
              type={field.type}
              name={field.name}
              value={form[field.name as keyof typeof form]}
              onChange={handleChange}
              className="w-full text-lg px-5 py-3 rounded bg-gray-800 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-white"
            />
            {field.name === "password" && form.password && (
              <p className={`text-sm ${strengthColor[passwordStrength]}`}>
                {t("profile.strength")}: {strengthLabel[passwordStrength]}
              </p>
            )}
          </div>
        ))}

        <motion.button
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.95 }}
          type="submit"
          className="w-full py-3 bg-gradient-to-r from-orange-400 to-yellow-300 text-black font-bold rounded-lg hover:brightness-110 transition"
        >
          💾 {t("profile.save")}
        </motion.button>
      </motion.form>
    </div>
  );
}

function ProfilePage() {
  return <RenderProfileContent />;
}

export default withAuth(ProfilePage);
