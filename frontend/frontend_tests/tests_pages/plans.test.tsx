import { render } from "@testing-library/react";
import PlanosPage from "@/pages/plans";
import { vi } from "vitest";

vi.mock("next/router", () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

describe("plans.tsx", () => {
  it("deve renderizar corretamente", () => {
    const { getByText } = render(<PlanosPage />);
    expect(getByText(/planos/i)).toBeInTheDocument();
  });
});