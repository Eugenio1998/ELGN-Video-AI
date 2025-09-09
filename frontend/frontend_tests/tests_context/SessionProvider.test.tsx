import { render } from "@testing-library/react";
import { SessionProvider } from "@/context/SessionProvider";

describe("SessionProvider", () => {
  it("deve renderizar sem erro", () => {
    const { container } = render(
      <SessionProvider>
        <div>Teste</div>
      </SessionProvider>
    );
    expect(container).toBeTruthy();
  });
});
