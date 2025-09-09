// 📁 components/VideoList.tsx
"use client";

import { useEffect, useState } from "react";
import { API_BASE_URL } from "../utils/api";

export default function VideoList() {
  const [videos, setVideos] = useState<
    {
      title: string;
      date: string;
      status: string;
      url?: string;
      type?: string;
    }[]
  >([]);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    const token = localStorage.getItem("token");
    fetch(`${API_BASE_URL}/api/v1/videos/processed`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => setVideos(data || []))
      .catch(() => setVideos([]));
  }, []);

  const filteredVideos = videos.filter((v) => {
    if (filter === "all") return true;
    return v.title.toLowerCase().includes(filter);
  });

  const handleRemove = (index: number) => {
    const updated = [...videos];
    updated.splice(index, 1);
    setVideos(updated);
  };

  const handleDownloadZip = async () => {
    const token = localStorage.getItem("token");
    const userPlan = localStorage.getItem("plan") || "basic";
    const downloads = parseInt(localStorage.getItem("downloads") || "0");

    if (["basic", "basic anual"].includes(userPlan) && downloads >= 5) {
      alert("❌ Limite de 5 downloads atingido no plano Basic.");
      return;
    }

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/download/zip`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ videos }),
      });

      if (!res.ok) throw new Error();

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "meus-videos.zip";
      document.body.appendChild(a);
      a.click();
      a.remove();

      localStorage.setItem("downloads", String(downloads + 1));
    } catch {
      alert("Erro ao baixar ZIP.");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex gap-4 items-center mb-4">
        <label className="text-sm">Filtrar por tipo:</label>
        <select
          className="bg-gray-800 text-white px-3 py-1 rounded text-sm"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="all">Todos</option>
          <option value="vídeo">Vídeos</option>
          <option value="shorts">Shorts</option>
          <option value="reels">Reels</option>
          <option value="tiktok">TikTok</option>
        </select>
      </div>

      <ul className="space-y-2">
        {filteredVideos.map((v, i) => (
          <li
            key={`media-${i}`}
            className="flex justify-between items-center border-b border-gray-800 pb-2"
          >
            <div>
              <p className="font-semibold">{v.title}</p>
              <p className="text-gray-400 text-sm">{v.date}</p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-green-500 font-bold">{v.status}</span>
              <button
                onClick={() => handleRemove(i)}
                className="text-red-500 text-sm hover:underline"
              >
                Excluir
              </button>
            </div>
          </li>
        ))}
      </ul>

      {filteredVideos.length > 0 && (
        <button
          onClick={handleDownloadZip}
          className="w-full mt-6 py-2 bg-gradient-to-r from-orange-400 to-yellow-400 text-black font-bold rounded hover:brightness-110 transition"
        >
          ⬇️ Baixar Tudo (ZIP)
        </button>
      )}
    </div>
  );
}
