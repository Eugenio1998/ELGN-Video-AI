import { render } from "@testing-library/react";
import Software from "@/pages/software";

describe("software.tsx", () => {
  it("deve renderizar corretamente", () => {
    const { container } = render(<Software />);
    expect(container).toBeTruthy();
  });
});
