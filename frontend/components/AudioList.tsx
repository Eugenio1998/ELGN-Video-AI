"use client";

import { useEffect, useState } from "react";

export default function AudioList() {
  const [audios, setAudios] = useState<
    { title: string; date: string; status: string; url?: string }[]
  >([]);

  useEffect(() => {
    const token = localStorage.getItem("token");
    fetch("/api/list/audios", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => setAudios(data || []))
      .catch(() => setAudios([]));
  }, []);

  return (
    <div className="space-y-6">
      <ul className="space-y-2">
        {audios.map((audio, i) => (
          <li
            key={`audio-${i}`}
            className="flex justify-between items-center border-b border-gray-800 pb-2"
          >
            <div>
              <p className="font-semibold">{audio.title}</p>
              <p className="text-gray-400 text-sm">{audio.date}</p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-purple-400 font-bold">{audio.status}</span>
              {audio.url && (
                <a
                  href={audio.url}
                  download
                  className="text-green-500 hover:underline text-sm"
                >
                  Download
                </a>
              )}
            </div>
          </li>
        ))}
      </ul>
      {audios.length === 0 && (
        <p className="text-gray-400 text-sm">Nenhum áudio gerado ainda.</p>
      )}
    </div>
  );
}
