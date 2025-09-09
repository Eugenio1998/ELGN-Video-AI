import { render } from "@testing-library/react";
import JobsPage from "@/pages/admin/jobs";

describe("Admin Jobs Page", () => {
  it("deve renderizar corretamente", () => {
    const { getByText } = render(<JobsPage />);
    expect(getByText(/jobs/i)).toBeInTheDocument();
  });
});
