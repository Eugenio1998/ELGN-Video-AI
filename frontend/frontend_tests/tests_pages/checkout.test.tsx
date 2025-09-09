import { render } from "@testing-library/react";
import CheckoutPage from "@/pages/checkout";
import { vi } from "vitest";

vi.mock("next/router", () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

describe("checkout.tsx", () => {
  it("deve renderizar corretamente", () => {
    const { getByText } = render(<CheckoutPage />);
    expect(getByText(/checkout/i)).toBeInTheDocument();
  });
});