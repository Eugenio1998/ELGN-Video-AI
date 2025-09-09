import { render } from "@testing-library/react";
import Intro from "@/pages/intro";

describe("intro.tsx", () => {
  it("deve renderizar corretamente", () => {
    const { container } = render(<Intro />);
    expect(container).toBeTruthy();
  });
});
