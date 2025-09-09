// 📁 components/ui/shared/Toast.tsx
"use client";

import { useEffect, useState } from "react";
import clsx from "clsx";

interface ToastProps {
  message: string;
  type?: "success" | "error" | "info";
  duration?: number;
  className?: string;
  onClose?: () => void;
}

export function Toast({
  message,
  type = "info",
  duration = 2500,
  className = "",
  onClose,
}: ToastProps) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setVisible(false);
      if (onClose) onClose();
    }, duration);
    return () => clearTimeout(timeout);
  }, [duration, onClose]);

  if (!visible) return null;

  return (
    <div
      role="alert"
      aria-live="assertive"
      className={clsx(
        "fixed bottom-6 left-1/2 -translate-x-1/2 px-4 py-2 rounded-md shadow text-sm font-medium z-50 transition-all duration-300",
        type === "success" && "bg-green-500 text-white",
        type === "error" && "bg-red-500 text-white",
        type === "info" && "bg-blue-500 text-white",
        className
      )}
    >
      {message}
    </div>
  );
}
