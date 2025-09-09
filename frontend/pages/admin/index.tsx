import Link from "next/link";

// 🔐 Proteção por role será aplicada futuramente (ex: apenas admins)
export const getServerSideProps = async () => {
  return { props: {} };
};

export default function AdminDashboard() {
  return (
    <section className="p-8 text-white max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-[var(--color-accent)]">
        🛠️ Painel Administrativo
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        <Link
          href="/admin/users"
          aria-label="Gerenciar usuários"
          className="bg-gray-800 p-6 rounded-xl shadow-lg hover:scale-[1.02] transition-transform duration-300 border border-white/20"
        >
          <h2 className="text-xl font-semibold">👥 Usuários</h2>
          <p className="text-sm text-gray-400">
            Visualize e gerencie todos os usuários cadastrados.
          </p>
        </Link>

        <Link
          href="/admin/jobs"
          aria-label="Acompanhar processamentos"
          className="bg-gray-800 p-6 rounded-xl shadow-lg hover:scale-[1.02] transition-transform duration-300 border border-white/20"
        >
          <h2 className="text-xl font-semibold">📦 Processamentos</h2>
          <p className="text-sm text-gray-400">
            Acompanhe os vídeos processados e em andamento.
          </p>
        </Link>

        <Link
          href="/admin/plans"
          aria-label="Ver planos e assinaturas"
          className="bg-gray-800 p-6 rounded-xl shadow-lg hover:scale-[1.02] transition-transform duration-300 border border-white/20"
        >
          <h2 className="text-xl font-semibold">💳 Planos</h2>
          <p className="text-sm text-gray-400">
            Verifique assinaturas ativas e histórico de pagamentos.
          </p>
        </Link>

        <Link
          href="/software"
          aria-label="Acessar editor de vídeos"
          className="bg-gradient-to-r from-blue-600 via-indigo-500 to-purple-600 p-6 rounded-xl shadow-lg hover:scale-[1.02] transition-transform duration-300 border border-white/30"
        >
          <h2 className="text-xl font-semibold text-white">
            🎞️ Editor de Vídeos
          </h2>
          <p className="text-sm text-white/80">
            Acesse o editor completo do software ELGN.
          </p>
        </Link>

        <Link
          href="/runway"
          aria-label="Acessar criador com IA"
          className="bg-gradient-to-r from-pink-600 via-fuchsia-500 to-violet-600 p-6 rounded-xl shadow-lg hover:scale-[1.02] transition-transform duration-300 border border-white/30"
        >
          <h2 className="text-xl font-semibold text-white">
            🧠 Criador com IA
          </h2>
          <p className="text-sm text-white/80">
            Crie vídeos, áudios e imagens com IA.
          </p>
        </Link>
      </div>
    </section>
  );
}
