// 📂 components/ui/input.tsx
import * as React from "react";
import clsx from "clsx";

export const Input = React.forwardRef<
  HTMLInputElement,
  React.InputHTMLAttributes<HTMLInputElement>
>(({ className, disabled, readOnly, type = "text", ...rest }, ref) => {
  return (
    <input
      ref={ref}
      type={type}
      {...rest}
      className={clsx(
        "w-full rounded-md border px-3 py-2 text-sm shadow-sm transition",
        "bg-gray-800 border-gray-600 text-white placeholder-gray-400",
        "focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]",
        disabled && "opacity-50 cursor-not-allowed",
        readOnly && "bg-gray-700 text-gray-400",
        className
      )}
      aria-disabled={disabled || undefined}
      aria-readonly={readOnly || undefined}
    />
  );
});

Input.displayName = "Input";
