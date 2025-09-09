// 📁 components/ui/icons/CheckIcon.tsx
import { motion } from "framer-motion";

interface CheckIconProps {
  className?: string;
  colorClass?: string;
  sizeClass?: string;
}

export function CheckIcon({
  className = "",
  colorClass = "text-green-400",
  sizeClass = "h-6 w-6",
}: CheckIconProps) {
  return (
    <motion.svg
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ type: "spring", stiffness: 400, damping: 20 }}
      xmlns="http://www.w3.org/2000/svg"
      className={`${sizeClass} ${colorClass} ${className}`}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={3}
        d="M5 13l4 4L19 7"
      />
    </motion.svg>
  );
}
