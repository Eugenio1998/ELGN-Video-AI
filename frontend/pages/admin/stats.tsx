// 📁 pages/admin/stats.tsx

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/router";

interface StatsData {
  totalUsers: number;
  activeUsers: number;
  totalJobs: number;
  videosGenerated: number;
  audiosGenerated: number;
  storageUsedGB: number;
}

export default function AdminStatsPage() {
  const router = useRouter();
  const [data, setData] = useState<StatsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch("/api/admin/stats");
        if (res.status === 401) {
          router.push("/login");
          return;
        }
        const json = await res.json();
        setData(json);
      } catch (error) {
        console.error("Erro ao buscar estatísticas:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [router]);

  if (loading)
    return <p className="text-center mt-10 text-white">⏳ Carregando...</p>;

  if (!data)
    return (
      <p className="text-center mt-10 text-red-400">
        ❌ Erro ao carregar estatísticas do sistema.
      </p>
    );

  return (
    <section className="p-8 max-w-6xl mx-auto text-white">
      <h1 className="text-2xl font-bold mb-6 text-[var(--color-accent)]">
        📊 Estatísticas do Sistema
      </h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <StatCard title="👥 Total de Usuários" value={data.totalUsers} />
        <StatCard title="✅ Usuários Ativos" value={data.activeUsers} />
        <StatCard title="📁 Jobs Criados" value={data.totalJobs} />
        <StatCard title="🎬 Vídeos Gerados" value={data.videosGenerated} />
        <StatCard title="🎧 Áudios Gerados" value={data.audiosGenerated} />
        <StatCard
          title="💾 Armazenamento (GB)"
          value={data.storageUsedGB ? data.storageUsedGB.toFixed(2) : "0.00"}
        />
      </div>
    </section>
  );
}

function StatCard({ title, value }: { title: string; value: number | string }) {
  return (
    <div className="p-4 border border-[var(--color-accent)] bg-black/70 rounded-lg shadow text-center">
      <h2 className="text-lg font-semibold mb-1">{title}</h2>
      <p className="text-2xl font-bold text-[var(--color-accent)]">{value}</p>
    </div>
  );
}
