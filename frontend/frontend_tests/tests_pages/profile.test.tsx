import { render } from "@testing-library/react";
import Profile from "@/pages/profile";

describe("profile.tsx", () => {
  it("deve renderizar corretamente", () => {
    const { container } = render(<Profile />);
    expect(container).toBeTruthy();
  });
});
