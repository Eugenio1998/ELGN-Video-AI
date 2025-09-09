// 📁 components/ui/shared/Skeleton.tsx
interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className = "h-4 w-full" }: SkeletonProps) {
  return (
    <div
      className={`animate-pulse rounded bg-gray-700 ${className}`}
      aria-hidden="true"
    />
  );
}
