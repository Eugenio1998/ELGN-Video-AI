// 📁 context/ModalProvider.tsx
"use client";

import { createContext, useContext, useState, ReactNode } from "react";

type ModalContextType = {
  modal: ReactNode | null;
  showModal: (content: ReactNode) => void;
  closeModal: () => void;
};

const ModalContext = createContext<ModalContextType | undefined>(undefined);

export const ModalProvider = ({ children }: { children: ReactNode }) => {
  const [modal, setModal] = useState<ReactNode | null>(null);

  const showModal = (content: ReactNode) => setModal(content);
  const closeModal = () => setModal(null);

  return (
    <ModalContext.Provider value={{ modal, showModal, closeModal }}>
      {children}

      {/* Modal global */}
      {modal && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 bg-black/60 flex justify-center items-center"
        >
          <div className="bg-gray-800 p-6 rounded-xl shadow-xl max-w-lg w-full mx-4">
            {modal}
          </div>
        </div>
      )}
    </ModalContext.Provider>
  );
};

export const useModal = () => {
  const context = useContext(ModalContext);
  if (!context)
    throw new Error("useModal deve ser usado dentro de <ModalProvider>");
  return context;
};
