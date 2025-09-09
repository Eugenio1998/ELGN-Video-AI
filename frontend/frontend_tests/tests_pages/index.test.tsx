import { render } from "@testing-library/react";
import Index from "@/pages/index";

describe("index.tsx", () => {
  it("deve renderizar corretamente", () => {
    const { container } = render(<Index />);
    expect(container).toBeTruthy();
  });
});
