import { render } from "@testing-library/react";
import Dashboard from "@/pages/dashboard";

describe("dashboard.tsx", () => {
  it("deve renderizar corretamente", () => {
    const { container } = render(<Dashboard />);
    expect(container).toBeTruthy();
  });
});
