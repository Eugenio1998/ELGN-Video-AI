// frontend_tests/tests_hooks/useDebounce.test.ts
/* eslint-env jest */
import { renderHook, act } from "@testing-library/react";
import { useDebounce } from "@/hooks/useDebounce";

jest.useFakeTimers();

describe("useDebounce", () => {
  it("deve debounciar o valor corretamente", () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 500),
      {
        initialProps: { value: "a" },
      }
    );

    expect(result.current).toBe("a");

    rerender({ value: "ab" });
    act(() => {
      jest.advanceTimersByTime(300);
    });
    expect(result.current).toBe("a"); // ainda não atualizou

    act(() => {
      jest.advanceTimersByTime(300);
    });
    expect(result.current).toBe("ab"); // atualizado após 600ms
  });
});
