import { render } from "@testing-library/react";
import Thanks from "@/pages/thanks";

describe("thanks.tsx", () => {
  it("deve renderizar corretamente", () => {
    const { container } = render(<Thanks />);
    expect(container).toBeTruthy();
  });
});
