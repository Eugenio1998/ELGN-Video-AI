import { renderHook, act } from "@testing-library/react";
import { GlobalLoadingProvider, useGlobalLoading } from "@/context/GlobalLoadingContext";

describe("GlobalLoadingContext", () => {
  it("deve ativar e desativar o carregamento", () => {
    const { result } = renderHook(() => useGlobalLoading(), {
      wrapper: ({ children }) => <GlobalLoadingProvider>{children}</GlobalLoadingProvider>,
    });

    act(() => result.current.setLoading(true));
    expect(result.current.loading).toBe(true);

    act(() => result.current.setLoading(false));
    expect(result.current.loading).toBe(false);
  });
});
