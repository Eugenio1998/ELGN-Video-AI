import { renderHook, act } from "@testing-library/react";
import { useDownloadLimit } from "@/hooks/useDownloadLimit";

describe("useDownloadLimit", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("deve retornar valor inicial do localStorage ou 0", () => {
    localStorage.setItem("downloadCount", "3");
    const { result } = renderHook(() => useDownloadLimit());
    expect(result.current.count).toBe(3);
  });

  it("deve permitir download se abaixo do limite", () => {
    const { result } = renderHook(() => useDownloadLimit());
    expect(result.current.canDownload).toBe(true);
  });

  it("deve registrar download e incrementar contador", () => {
    const { result } = renderHook(() => useDownloadLimit());
    act(() => result.current.registerDownload());
    expect(result.current.count).toBe(1);
  });

  it("deve impedir download se limite atingido", () => {
    const { result } = renderHook(() => useDownloadLimit(1));
    act(() => result.current.registerDownload());
    act(() => result.current.registerDownload());
    expect(result.current.count).toBe(1); // limite atingido
    expect(result.current.canDownload).toBe(false);
  });

  it("deve resetar contador", () => {
    const { result } = renderHook(() => useDownloadLimit());
    act(() => result.current.registerDownload());
    act(() => result.current.resetDownloadCount());
    expect(result.current.count).toBe(0);
  });
});
