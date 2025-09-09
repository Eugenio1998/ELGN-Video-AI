import { render } from "@testing-library/react";
import LogsPage from "@/pages/admin/logs";

describe("Admin Logs Page", () => {
  it("deve renderizar corretamente", () => {
    const { getByText } = render(<LogsPage />);
    expect(getByText(/logs/i)).toBeInTheDocument();
  });
});
