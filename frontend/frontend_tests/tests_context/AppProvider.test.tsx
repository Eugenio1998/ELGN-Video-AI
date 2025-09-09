import { render } from "@testing-library/react";
import { AppProviders } from "@/context/AppProviders";

describe("AppProvider", () => {
  it("deve renderizar o AppProvider corretamente", () => {
    const { container } = render(
      <AppProviders>
        <div>Conteúdo de teste</div>
      </AppProviders>
    );
    expect(container).toBeTruthy();
  });
});
