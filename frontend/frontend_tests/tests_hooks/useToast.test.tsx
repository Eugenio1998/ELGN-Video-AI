import { renderHook } from "@testing-library/react";
import { useToast } from "@/hooks/useToast";
import { UIProvider } from "@/context/UIContext";

describe("useToast", () => {
  it("deve ter função showToast", () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <UIProvider>{children}</UIProvider>
    );

    const { result } = renderHook(() => useToast(), { wrapper });
    expect(typeof result.current).toBe("function");
  });
});
