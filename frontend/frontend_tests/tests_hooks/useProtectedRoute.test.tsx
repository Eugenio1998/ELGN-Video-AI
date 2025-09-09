// frontend_tests/tests_hooks/useProtectedRoute.test.tsx
import { renderHook } from "@testing-library/react";
import { useProtectedRoute } from "@/hooks/useProtectedRoute";
import { SessionProvider } from "@/context/SessionProvider";

describe("useProtectedRoute", () => {
  it("deve retornar verdadeiro ou falso", () => {
    const { result } = renderHook(() => useProtectedRoute(), {
      wrapper: ({ children }) => <SessionProvider>{children}</SessionProvider>,
    });

    expect(typeof result.current).toBe("boolean");
  });
});
