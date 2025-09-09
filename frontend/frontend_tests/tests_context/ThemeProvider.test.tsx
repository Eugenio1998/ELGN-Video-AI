import { render } from "@testing-library/react";
import { ThemeProvider } from "@/context/ThemeProvider";

describe("ThemeProvider", () => {
  it("deve renderizar corretamente", () => {
    const { container } = render(
      <ThemeProvider>
        <div>Conteúdo</div>
      </ThemeProvider>
    );
    expect(container).toBeTruthy();
  });
});
