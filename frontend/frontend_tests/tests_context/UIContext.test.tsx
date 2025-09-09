// frontend_tests/tests_context/UIContext.test.tsx
import { renderHook, act } from "@testing-library/react";
import { UIProvider, useUI } from "@/context/UIContext";
import { vi } from "vitest";

describe("UIContext", () => {
  it("deve exibir e limpar o toast corretamente", () => {
    vi.useFakeTimers(); // ⏲️ ativa timers falsos

    const { result } = renderHook(() => useUI(), {
      wrapper: ({ children }) => <UIProvider>{children}</UIProvider>,
    });

    act(() => {
      result.current.showToast("Mensagem de teste", "success", 2000);
    });

    expect(result.current.toast?.message).toBe("Mensagem de teste");

    act(() => {
      vi.advanceTimersByTime(2000); // simula 2s passados
    });

    expect(result.current.toast).toBe(null);

    vi.useRealTimers(); // restaura timers reais
  });
});
