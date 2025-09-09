// 📁 components/ui/shared/ProtectedSection.tsx
import React from "react";

interface ProtectedSectionProps {
  hasAccess: boolean;
  fallback?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

export function ProtectedSection({
  hasAccess,
  fallback = null,
  children,
  className = "",
}: ProtectedSectionProps) {
  return <div className={className}>{hasAccess ? children : fallback}</div>;
}

ProtectedSection.displayName = "ProtectedSection";
