// 📁 pages/admin/users.tsx

"use client";

import { useEffect, useState } from "react";
import { FaUserShield, FaUserTimes } from "react-icons/fa";

type UserData = {
  id: string;
  username: string;
  email: string;
  plan: string;
  status: "ativo" | "inativo" | "pendente";
};

export default function AdminUsersPage() {
  const [users, setUsers] = useState<UserData[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingUserId, setUpdatingUserId] = useState<string | null>(null);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const res = await fetch("/api/admin/users");
        const json = await res.json();
        setUsers(json);
      } catch (error) {
        console.error("Erro ao buscar usuários:", error);
        setUsers([]);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  const changeStatus = async (
    id: string,
    newStatus: "ativo" | "inativo" | "pendente"
  ) => {
    setUpdatingUserId(id);
    try {
      const res = await fetch("/api/admin/users/update-status", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, status: newStatus }),
      });

      if (res.ok) {
        setUsers((prev) =>
          prev.map((user) =>
            user.id === id ? { ...user, status: newStatus } : user
          )
        );
      } else {
        console.warn("Não foi possível atualizar o status.");
      }
    } catch (error) {
      console.error("Erro ao atualizar status:", error);
    } finally {
      setUpdatingUserId(null);
    }
  };

  return (
    <section className="p-8 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold text-[var(--color-accent)] mb-6">
        👥 Gerenciamento de Usuários
      </h1>

      {loading && <p className="text-white">🔄 Carregando usuários...</p>}

      {!loading && users.length === 0 && (
        <p className="text-gray-400">Nenhum usuário encontrado.</p>
      )}

      <div className="bg-black/60 border border-gray-700 rounded-lg overflow-auto max-h-[75vh]">
        <table className="w-full table-auto text-sm text-left">
          <thead className="bg-gray-800 border-b border-gray-700 sticky top-0">
            <tr>
              <th className="px-4 py-2">ID</th>
              <th className="px-4 py-2">Usuário</th>
              <th className="px-4 py-2">Email</th>
              <th className="px-4 py-2">Plano</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2">Ações</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-b border-gray-700">
                <td className="px-4 py-2 text-gray-400">{u.id}</td>
                <td className="px-4 py-2 text-white">{u.username}</td>
                <td className="px-4 py-2 text-gray-300">{u.email}</td>
                <td className="px-4 py-2 text-blue-400 font-semibold">
                  {u.plan}
                </td>
                <td className="px-4 py-2">
                  <span
                    className={`text-xs font-bold px-2 py-1 rounded ${
                      u.status === "ativo"
                        ? "bg-green-600 text-white"
                        : u.status === "inativo"
                        ? "bg-red-600 text-white"
                        : "bg-yellow-600 text-black"
                    }`}
                  >
                    {u.status}
                  </span>
                </td>
                <td className="px-4 py-2 flex gap-2 items-center">
                  <button
                    onClick={() => changeStatus(u.id, "ativo")}
                    disabled={updatingUserId === u.id}
                    className="px-2 py-1 bg-green-600 text-white rounded hover:brightness-110 disabled:opacity-50"
                    title="Ativar usuário"
                    aria-label={`Ativar usuário ${u.username}`}
                  >
                    <FaUserShield />
                  </button>
                  <button
                    onClick={() => changeStatus(u.id, "inativo")}
                    disabled={updatingUserId === u.id}
                    className="px-2 py-1 bg-red-600 text-white rounded hover:brightness-110 disabled:opacity-50"
                    title="Desativar usuário"
                    aria-label={`Desativar usuário ${u.username}`}
                  >
                    <FaUserTimes />
                  </button>
                  {updatingUserId === u.id && (
                    <span className="text-xs text-gray-400">⏳</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
