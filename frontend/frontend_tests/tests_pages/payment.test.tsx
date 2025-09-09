import { render } from "@testing-library/react";
import Payment from "@/pages/payment";

describe("payment.tsx", () => {
  it("deve renderizar corretamente", () => {
    const { container } = render(<Payment />);
    expect(container).toBeTruthy();
  });
});
