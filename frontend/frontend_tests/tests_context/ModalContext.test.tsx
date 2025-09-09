import { renderHook, act } from "@testing-library/react";
import { ModalProvider, useModal } from "@/context/ModalContext";
import { ReactNode } from "react";

describe("ModalContext", () => {
  it("deve mostrar e fechar o modal corretamente", () => {
    const { result } = renderHook(() => useModal(), {
      wrapper: ({ children }) => <ModalProvider>{children}</ModalProvider>,
    });

    const dummyContent: ReactNode = <div>Conteúdo do modal</div>;

    act(() => {
      result.current.showModal(dummyContent);
    });
    expect(result.current.modal).toEqual(dummyContent);

    act(() => {
      result.current.closeModal();
    });
    expect(result.current.modal).toBeNull();
  });
});
