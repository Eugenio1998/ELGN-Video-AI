// frontend_tests/tests_hooks/usePlan.test.ts
import { renderHook } from "@testing-library/react";
import { usePlan } from "@/hooks/usePlan";
import { UIProvider } from "@/context/UIContext";

describe("usePlan", () => {
  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <UIProvider>{children}</UIProvider>
  );

  it("deve retornar um plano válido", () => {
    const { result } = renderHook(() => usePlan(), { wrapper });
    expect(result.current).toBeDefined();
    expect(typeof result.current).toBe("object");
  });
});
