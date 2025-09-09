// frontend_tests/tests_hooks/useGlobalLoading.test.ts
import { renderHook, act } from "@testing-library/react";
import { useGlobalLoading } from "@/hooks/useGlobalLoading";
import { GlobalLoadingProvider } from "@/context/GlobalLoadingContext";

describe("useGlobalLoading", () => {
  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <GlobalLoadingProvider>{children}</GlobalLoadingProvider>
  );

  it("deve ativar e desativar corretamente", () => {
    const { result } = renderHook(() => useGlobalLoading(), { wrapper });

    act(() => {
      result.current.setLoading(true);
    });

    expect(result.current.loading).toBe(true);

    act(() => {
      result.current.setLoading(false);
    });

    expect(result.current.loading).toBe(false);
  });
});
