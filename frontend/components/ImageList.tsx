"use client";

import { useEffect, useState } from "react";

export default function ImageList() {
  const [images, setImages] = useState<
    { title: string; date: string; status: string; url?: string }[]
  >([]);

  useEffect(() => {
    const token = localStorage.getItem("token");
    fetch("/api/list/images", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => setImages(data || []))
      .catch(() => setImages([]));
  }, []);

  return (
    <div className="space-y-6">
      <ul className="space-y-2">
        {images.map((img, i) => (
          <li
            key={`image-${i}`}
            className="flex justify-between items-center border-b border-gray-800 pb-2"
          >
            <div>
              <p className="font-semibold">{img.title}</p>
              <p className="text-gray-400 text-sm">{img.date}</p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-blue-400 font-bold">{img.status}</span>
              {img.url && (
                <a
                  href={img.url}
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
      {images.length === 0 && (
        <p className="text-gray-400 text-sm">Nenhuma imagem gerada ainda.</p>
      )}
    </div>
  );
}
