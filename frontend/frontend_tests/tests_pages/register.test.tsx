import { render } from "@testing-library/react";
import RegisterPage from "@/pages/register";
import { vi } from "vitest";

vi.mock("next/router", () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

describe("register.tsx", () => {
  it("deve renderizar corretamente", () => {
    const { getByText } = render(<RegisterPage />);
    expect(getByText(/registrar/i)).toBeInTheDocument();
  });
});
