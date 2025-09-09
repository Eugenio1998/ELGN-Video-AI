// 📂 components/ui/button.tsx
import { ButtonHTMLAttributes, ReactNode } from "react";
import classNames from "classnames";

type ButtonVariant =
  | "default"
  | "primary"
  | "secondary"
  | "accent"
  | "outline"
  | "danger"
  | "ghost";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: ButtonVariant;
  fullWidth?: boolean;
}

export function Button({
  children,
  variant = "primary",
  fullWidth = false,
  className = "",
  ...props
}: ButtonProps) {
  const baseStyle =
    "px-4 py-2 rounded-md font-medium text-sm transition-all focus:outline-none focus:ring-2 focus:ring-offset-2";

  const variants: Record<ButtonVariant, string> = {
    default: "bg-gray-300 text-black hover:bg-gray-400",
    primary: "bg-blue-600 text-white hover:bg-blue-700",
    secondary: "bg-gray-700 text-white hover:bg-gray-800",
    accent: "bg-[var(--color-accent)] text-black hover:brightness-110",
    outline:
      "border border-[var(--color-accent)] text-[var(--color-accent)] bg-transparent hover:bg-[var(--color-accent)] hover:text-black",
    danger: "bg-red-600 text-white hover:bg-red-700",
    ghost: "bg-transparent text-white hover:bg-gray-800",
  };

  return (
    <button
      className={classNames(
        baseStyle,
        variants[variant],
        {
          "w-full": fullWidth,
          "cursor-not-allowed opacity-60": props.disabled,
        },
        className
      )}
      aria-busy={props["aria-busy"] || undefined}
      {...props}
    >
      {children}
    </button>
  );
}
