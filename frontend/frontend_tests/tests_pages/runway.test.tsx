import { render } from "@testing-library/react";
import Runway from "@/pages/runway";

describe("runway.tsx", () => {
  it("deve renderizar corretamente", () => {
    const { container } = render(<Runway />);
    expect(container).toBeTruthy();
  });
});
