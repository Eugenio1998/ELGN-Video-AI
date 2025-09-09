"use client";

import { createContext, useContext, useState, ReactNode } from "react";

type GlobalLoadingContextType = {
  loading: boolean;
  setLoading: (state: boolean) => void;
};

const GlobalLoadingContext = createContext<
  GlobalLoadingContextType | undefined
>(undefined);

export const GlobalLoadingProvider = ({
  children,
}: {
  children: ReactNode;
}) => {
  const [loading, setLoading] = useState(false);

  return (
    <GlobalLoadingContext.Provider value={{ loading, setLoading }}>
      {children}
    </GlobalLoadingContext.Provider>
  );
};

export const useGlobalLoading = () => {
  const context = useContext(GlobalLoadingContext);
  if (!context)
    throw new Error(
      "useGlobalLoading must be used within GlobalLoadingProvider"
    );
  return context;
};
