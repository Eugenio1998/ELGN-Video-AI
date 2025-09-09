// frontend_tests/tests_hooks/useCopyToClipboard.test.ts
/* eslint-env jest */
import { renderHook, act } from "@testing-library/react";
import { useCopyToClipboard } from "@/hooks/useCopyToClipboard";

describe("useCopyToClipboard", () => {
  beforeAll(() => {
    Object.assign(navigator, {
      clipboard: {
        writeText: jest.fn().mockResolvedValue(undefined),
      },
    });
  });

  it("deve copiar o texto para a área de transferência", async () => {
    const { result } = renderHook(() => useCopyToClipboard());

    await act(async () => {
      await result.current.copy("texto de teste");
    });

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
      "texto de teste"
    );
  });
});
