// 📁 components/ui/shared/Modal.tsx
import { useEffect, useRef } from "react";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
  titleId?: string;
}

export function Modal({
  open,
  onClose,
  children,
  titleId = "modal-title",
}: ModalProps) {
  const overlayRef = useRef(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  const handleClickOutside = (e: React.MouseEvent) => {
    if (e.target === overlayRef.current) {
      onClose();
    }
  };

  if (!open) return null;

  return (
    <div
      ref={overlayRef}
      onClick={handleClickOutside}
      className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center"
      role="dialog"
      aria-modal="true"
      aria-labelledby={titleId}
    >
      <div className="bg-gray-800 rounded-lg p-6 shadow-xl relative">
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-white"
          aria-label="Fechar modal"
        >
          ✖
        </button>
        {children}
      </div>
    </div>
  );
}
