import { render } from "@testing-library/react";
import LoginPage from "@/pages/login";
import { vi } from "vitest";

vi.mock("next/router", () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

describe("login.tsx", () => {
  it("deve renderizar corretamente", () => {
    const { getByText } = render(<LoginPage />);
    expect(getByText(/entrar/i)).toBeInTheDocument();
  });
});