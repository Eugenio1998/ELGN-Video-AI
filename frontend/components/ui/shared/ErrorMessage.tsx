// 📁 components/ui/shared/ErrorMessage.tsx

interface ErrorMessageProps {
  message: string;
  className?: string;
}

export function ErrorMessage({ message, className = "" }: ErrorMessageProps) {
  return (
    <p
      className={`text-sm text-red-400 mt-1 ${className}`}
      role="alert"
      aria-live="assertive"
    >
      ❌ {message}
    </p>
  );
}
