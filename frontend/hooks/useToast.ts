// 📁 hooks/useToast.ts
import { useUI } from "../context/UIContext";

export function useToast() {
  const { showToast } = useUI();
  return showToast;
}
