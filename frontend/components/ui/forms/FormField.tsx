// 📁 components/ui/forms/FormField.tsx
import { Label } from "../label";
import { Input } from "../input";
import { ErrorMessage } from "../shared/ErrorMessage";

interface FormFieldProps {
  id: string;
  name?: string;
  label: string;
  value: string;
  placeholder?: string;
  type?: string;
  autoComplete?: string;
  error?: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export function FormField({
  id,
  name,
  label,
  value,
  placeholder,
  onChange,
  error,
  type = "text",
  autoComplete = "off",
}: FormFieldProps) {
  return (
    <div className="mb-4">
      <Label htmlFor={id}>{label}</Label>
      <Input
        id={id}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        type={type}
        autoComplete={autoComplete}
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-error` : undefined}
      />
      {error && <ErrorMessage message={error} />}
    </div>
  );
}
