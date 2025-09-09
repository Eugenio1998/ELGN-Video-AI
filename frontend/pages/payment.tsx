"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { FaCreditCard } from "react-icons/fa";
import { motion } from "framer-motion";
import { withAuth } from "../utils/withAuth";

function RenderPaymentContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(false);
  const [selectedMethod, setSelectedMethod] = useState("stripe");
  const [plano, setPlano] = useState<string>("");

  useEffect(() => {
    const planoSelecionado = searchParams?.get("plano");
    if (planoSelecionado) {
      setPlano(planoSelecionado);
      localStorage.setItem("plan", planoSelecionado);
    } else {
      router.push("/plans");
    }
  }, [searchParams, router]);

  const handlePayment = async () => {
    setLoading(true);

    const userEmail = localStorage.getItem("userEmail");

    if (!userEmail) {
      alert("Erro: email do usuário não encontrado.");
      setLoading(false);
      return;
    }

    try {
      const res = await fetch("/api/payments/stripe-session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ plan: plano, email: userEmail }),
      });

      const data = await res.json();
      if (data?.url) {
        window.location.href = data.url;
      } else {
        alert("❌ Falha ao iniciar pagamento.");
      }
    } catch {
      alert("❌ Erro ao processar pagamento.");
    } finally {
      setLoading(false);
    }
  };

  const methods = [
    {
      id: "stripe",
      label: "Cartão de Crédito (Stripe)",
      icon: <FaCreditCard />,
    },
  ];

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-black text-white px-4 py-16">
      {/* 🔳 Fundo com camada escurecida */}
      <div className="absolute inset-0 bg-[url('/img/Mario02.gif')] bg-cover bg-center bg-fixed" />
      <div className="absolute inset-0 bg-black/50 z-0" />

      {/* 🧾 Card de Pagamento com neon */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        whileHover={{ scale: 1.01 }}
        className="relative z-10 max-w-lg w-full p-8 bg-black/90 rounded-xl border border-lime-400 shadow-[0_0_30px_5px_rgba(0,255,100,0.3)] backdrop-blur-lg"
      >
        <h1 className="text-2xl font-bold mb-2 text-lime-300 drop-shadow">
          🛒 Finalizar Assinatura
        </h1>
        <p className="text-sm text-gray-400 mb-6">
          Plano selecionado:{" "}
          <span className="text-green-400 font-semibold">{plano}</span>
        </p>

        <div className="grid gap-4 mb-6">
          {methods.map((method) => (
            <button
              key={method.id}
              onClick={() => setSelectedMethod(method.id)}
              className={`w-full flex items-center justify-center gap-3 px-4 py-3 rounded-lg font-semibold transition-all border border-gray-700 ${
                selectedMethod === method.id
                  ? "bg-green-600 text-black"
                  : "bg-gray-800 text-white hover:bg-gray-700"
              }`}
            >
              {method.icon} {method.label}
            </button>
          ))}
        </div>

        <motion.button
          onClick={handlePayment}
          disabled={loading}
          whileTap={{ scale: 0.97 }}
          className="w-full py-3 mt-6 bg-gradient-to-r from-green-400 to-lime-500 text-black font-bold rounded-lg hover:brightness-110 transition"
        >
          {loading
            ? "Processando pagamento..."
            : `Pagar com ${
                methods.find((m) => m.id === selectedMethod)?.label
              }`}
        </motion.button>

        <p className="text-sm text-gray-500 mt-6">
          Ao continuar, você concorda com nossos Termos de Uso e Política de
          Privacidade.
        </p>
      </motion.div>
    </div>
  );
}

function PaymentPage() {
  return <RenderPaymentContent />;
}

export default withAuth(PaymentPage);
