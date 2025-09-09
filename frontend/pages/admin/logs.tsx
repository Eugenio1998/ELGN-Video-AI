// 📁 pages/admin/logs.tsx

"use client";

import { useEffect, useState } from "react";

interface LogEntry {
  timestamp: string;
  level: "INFO" | "ERROR" | "WARN" | string;
  message: string;
}

export default function AdminLogsPage() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/admin/logs")
      .then((res) => res.json())
      .then(setLogs)
      .catch((err) => {
        console.error("Erro ao carregar logs:", err);
        setLogs([]);
      })
      .finally(() => setLoading(false));
  }, []);

  const getLevelColor = (level: string) => {
    switch (level.toUpperCase()) {
      case "INFO":
        return "text-blue-400";
      case "ERROR":
        return "text-red-500";
      case "WARN":
        return "text-yellow-400";
      default:
        return "text-gray-300";
    }
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  return (
    <section className="p-8 max-w-6xl mx-auto text-white">
      <h1 className="text-2xl font-bold mb-6 text-[var(--color-accent)]">
        📝 Logs do Sistema
      </h1>

      {loading && <p>⏳ Carregando logs...</p>}

      {!loading && logs.length === 0 && (
        <p className="text-gray-400">Nenhum log disponível.</p>
      )}

      {!loading && logs.length > 0 && (
        <div className="bg-black/60 border border-gray-700 rounded-lg overflow-auto max-h-[70vh] text-sm">
          <table className="w-full text-left table-auto">
            <thead className="bg-gray-800 border-b border-gray-700 sticky top-0 z-10">
              <tr>
                <th className="px-4 py-2">🕒 Data/Hora</th>
                <th className="px-4 py-2">📛 Nível</th>
                <th className="px-4 py-2">💬 Mensagem</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log, index) => (
                <tr
                  key={index}
                  className="border-b border-gray-700 hover:bg-gray-800 transition"
                >
                  <td className="px-4 py-2 text-gray-300">
                    {formatDate(log.timestamp)}
                  </td>
                  <td
                    className={`px-4 py-2 font-bold uppercase ${getLevelColor(
                      log.level
                    )}`}
                  >
                    {log.level}
                  </td>
                  <td className="px-4 py-2 text-gray-200 whitespace-pre-wrap">
                    {log.message}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
