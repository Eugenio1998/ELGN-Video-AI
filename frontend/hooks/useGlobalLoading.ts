// 📁 hooks/useGlobalLoading.ts
import { useGlobalLoading as useGlobalLoadingContext } from "../context/GlobalLoadingContext";

export function useGlobalLoading() {
  const { loading, setLoading } = useGlobalLoadingContext();
  return { loading, setLoading };
}
