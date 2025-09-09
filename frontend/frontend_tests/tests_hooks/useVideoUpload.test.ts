import { renderHook } from "@testing-library/react";
import { useVideoUpload } from "@/hooks/useVideoUpload";

describe("useVideoUpload", () => {
  it("deve ter propriedades iniciais", () => {
    const { result } = renderHook(() => useVideoUpload());
    expect(result.current.videoFile).toBeNull();
  });
});
