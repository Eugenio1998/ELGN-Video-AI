// 📁 pages/admin/jobs.tsx

import { useEffect, useState } from "react";
import { Card, CardContent } from "../../components/ui/card";
import { Spinner } from "../../components/ui/shared/Spinner";

interface Job {
  id: string;
  user: string;
  status: string;
  createdAt: string;
  outputUrl?: string;
}

export default function AdminJobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/admin/jobs")
      .then((res) => res.json())
      .then((data) => setJobs(data.jobs || []))
      .finally(() => setLoading(false));
    // Em produção, pode ser interessante adicionar tratamento de erros com try/catch
  }, []);

  return (
    <section className="p-6 max-w-6xl mx-auto text-white">
      <h1 className="text-2xl font-bold mb-6 text-[var(--color-accent)]">
        📼 Processamentos Recentes
      </h1>

      {loading ? (
        <div className="flex justify-center items-center h-40">
          <Spinner />
        </div>
      ) : jobs.length === 0 ? (
        <p className="text-gray-400 text-center">Nenhum job encontrado.</p>
      ) : (
        <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6">
          {jobs.map((job) => (
            <Card
              key={job.id}
              className="border border-white/20 bg-zinc-900 rounded-xl shadow-lg hover:shadow-xl transition"
            >
              <CardContent className="p-5 space-y-2">
                <p className="text-sm text-gray-400">👤 Usuário: {job.user}</p>
                <p className="text-sm">
                  🆔 ID: <span className="text-white">{job.id}</span>
                </p>
                <p className="text-sm">
                  📅 Criado em: {new Date(job.createdAt).toLocaleString()}
                </p>
                <p className="text-sm">
                  📦 Status: <span className="font-semibold">{job.status}</span>
                </p>
                {job.outputUrl && (
                  <a
                    href={job.outputUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block mt-2 text-sm text-cyan-400 underline"
                    aria-label="Ver vídeo processado"
                  >
                    🔗 Ver vídeo
                  </a>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </section>
  );
}
