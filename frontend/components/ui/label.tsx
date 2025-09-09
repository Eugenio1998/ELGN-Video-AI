// 📂 components/ui/label.tsx
import * as React from "react";
import clsx from "clsx";

export const Label = React.forwardRef<
  HTMLLabelElement,
  React.LabelHTMLAttributes<HTMLLabelElement>
>(({ className, ...props }, ref) => {
  return (
    <label
      ref={ref}
      {...props}
      className={clsx(
        "block text-sm font-semibold text-gray-300 mb-1",
        className
      )}
    />
  );
});

Label.displayName = "Label";
