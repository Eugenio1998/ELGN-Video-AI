// 📁 components/ui/shared/Switch.tsx
"use client";

import * as React from "react";

interface SwitchProps {
  enabled: boolean;
  onToggle: (checked: boolean) => void;
  label?: string;
  id?: string;
  className?: string;
}

export function Switch({
  enabled,
  onToggle,
  label,
  id,
  className = "",
}: SwitchProps) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onToggle(!enabled);
    }
  };

  return (
    <label
      htmlFor={id}
      className={`flex items-center space-x-3 cursor-pointer ${className}`}
    >
      <div
        role="switch"
        id={id}
        aria-checked={enabled}
        tabIndex={0}
        onKeyDown={handleKeyDown}
        onClick={() => onToggle(!enabled)}
        className={`w-10 h-5 flex items-center rounded-full p-1 transition-colors duration-300 outline-none focus:ring-2 focus:ring-[var(--color-accent)] ${
          enabled ? "bg-[var(--color-accent)]" : "bg-gray-600"
        }`}
      >
        <div
          className={`bg-white w-4 h-4 rounded-full shadow transform duration-300 ${
            enabled ? "translate-x-5" : "translate-x-0"
          }`}
        />
      </div>
      {label && <span className="text-sm text-white">{label}</span>}
    </label>
  );
}
