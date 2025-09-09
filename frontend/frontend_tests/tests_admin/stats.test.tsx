import { render } from "@testing-library/react";
import StatsPage from "@/pages/admin/stats";

describe("Admin Stats Page", () => {
  it("deve renderizar corretamente", () => {
    const { getByText } = render(<StatsPage />);
    expect(getByText(/stats/i)).toBeInTheDocument();
  });
});
