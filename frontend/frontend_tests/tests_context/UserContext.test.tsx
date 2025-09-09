// 📁 frontend_tests/tests_context/UserContext.test.tsx
import { renderHook, act } from "@testing-library/react";
import { UserProvider, useUser } from "@/context/UserContext";

// mock da função fetchUser
vi.mock("@/utils/fetchUser", () => ({
  fetchUser: vi.fn(() =>
    Promise.resolve({
      id: "123",
      username: "Test",
      plan: "Premium",
    })
  ),
}));

describe("UserContext", () => {
  it("deve buscar e definir o usuário corretamente", async () => {
    localStorage.setItem("token", "fake-token");

    const { result } = renderHook(() => useUser(), {
      wrapper: ({ children }) => <UserProvider>{children}</UserProvider>,
    });

    await act(async () => {
      await result.current.refreshUser();
    });

    expect(result.current.user?.id).toBe("123");
    expect(result.current.user?.username).toBe("Test");
    expect(result.current.user?.normalizedPlan).toBe("premium");
  });
});
