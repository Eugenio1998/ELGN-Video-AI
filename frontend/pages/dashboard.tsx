"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import NavbarUser from "../components/NavbarUser";
import { motion } from "framer-motion";
import { withAuth } from "../utils/withAuth";
import { API_BASE_URL } from "../utils/api";
import VideoList from "../components/VideoList";
import ImageList from "../components/ImageList";
import AudioList from "../components/AudioList";

function RenderDashboardContent() {
  const router = useRouter();
  const [user, setUser] = useState({
    name: "",
    email: "",
    plan: "",
    status: "",
    verified: true,
    id: "",
  });

  const [storage, setStorage] = useState({ used: 0, total: 0 });
  const [showPlanWarning, setShowPlanWarning] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const plan = localStorage.getItem("plan")?.toLowerCase() || "basic";
    const userStatus =
      localStorage.getItem("userStatus")?.toLowerCase() || "inativo";

    if (!token) {
      router.push("/login");
      return;
    }

    if (userStatus !== "ativo") {
      router.push("/plans");
      return;
    }

    if (
      ![
        "pro",
        "pro anual",
        "premium",
        "premium anual",
        "empresarial",
        "empresarial anual",
      ].includes(plan)
    ) {
      setShowPlanWarning(true);
    } else {
      localStorage.removeItem("downloads"); // limpa contador para planos superiores
    }

    setUser({
      name: localStorage.getItem("userName") || "Usuário",
      email: "usuario@elgn.ai",
      plan,
      status: userStatus,
      verified: true,
      id: localStorage.getItem("userId") || "ID-000",
    });

    // 💾 Buscar uso de armazenamento
    fetch(`${API_BASE_URL}/api/v1/storage`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => setStorage(data || { used: 0, total: 0 }))
      .catch(() => setStorage({ used: 0, total: 0 }));
  }, [router]);

  const Card = ({
    title,
    children,
    color,
  }: {
    title: string;
    children: React.ReactNode;
    color?: string;
  }) => {
    const cor = color || "cyan";
    return (
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        whileHover={{ scale: 1.02 }}
        className={`relative bg-black border-2 border-${cor}-400 rounded-xl p-6 text-white`}
      >
        <div
          className={`absolute -inset-1 border-2 border-${cor}-400 rounded-xl blur-md opacity-30 animate-pulse pointer-events-none`}
        />
        <h2
          className={`text-xl font-bold mb-4 text-${cor}-300 drop-shadow-[0_0_10px_${cor}]`}
        >
          {title}
        </h2>
        {children}
      </motion.div>
    );
  };

  return (
    <div className="relative min-h-screen bg-[url('/img/Mario02.gif')] bg-cover bg-center bg-no-repeat bg-fixed px-4 text-white">
      <div className="absolute inset-0 bg-gradient-to-b from-black/30 to-black/50 z-0" />

      <div className="relative z-10 min-h-screen px-6 py-12 space-y-12">
        <NavbarUser />

        {showPlanWarning && (
          <div className="bg-red-600 text-white px-4 py-2 rounded shadow shadow-red-400 animate-pulse text-sm">
            ⚠️ Apenas usuários com plano Pro ou superior podem baixar ZIP
            completo.
          </div>
        )}

        <section className="grid md:grid-cols-3 gap-6">
          <Card title="👤 Informações do Usuário" color="white">
            <p>
              <strong>Nome:</strong> {user.name}
            </p>
            <p>
              <strong>Email:</strong> {user.email}
            </p>
            <p>
              <strong>Plano:</strong> {user.plan}
            </p>
            <p>
              <strong>Status:</strong> {user.status}
            </p>
            <p>
              <strong>Verificado:</strong> {user.verified ? "Sim" : "Não"}
            </p>
            <Link
              href="/profile"
              className="text-blue-400 hover:underline block mt-3"
            >
              Editar Perfil
            </Link>
          </Card>

          <Card title="💳 Pagamento" color="lime">
            <p>
              <strong>Plano Atual:</strong> {user.plan}
            </p>
            <p>
              <strong>Próximo vencimento:</strong> 05/05/2026
            </p>
            <p>
              <strong>Armazenamento:</strong> {storage.used} GB /{" "}
              {storage.total} GB
            </p>
            <Link
              href="/plans"
              className="text-green-400 hover:underline block mt-3"
            >
              Gerenciar Assinatura
            </Link>
          </Card>

          <Card title="⚙️ Preferências (em breve)" color="fuchsia">
            <p className="text-gray-400 text-sm">
              Em breve você poderá salvar filtros, vozes e estilos de IA.
            </p>
          </Card>
        </section>

        <Card title="🎥 Meus Vídeos Processados" color="orange">
          <VideoList />
        </Card>

        <Card title="🖼️ Minhas Imagens Geradas" color="blue">
          <ImageList />
        </Card>

        <Card title="🎵 Minhas Músicas / Vozes Geradas" color="pink">
          <AudioList />
        </Card>
      </div>
    </div>
  );
}

function DashboardPage() {
  return <RenderDashboardContent />;
}

export default withAuth(DashboardPage);
