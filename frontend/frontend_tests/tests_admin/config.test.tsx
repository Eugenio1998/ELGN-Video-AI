import { render } from "@testing-library/react";
import ConfigPage from "@/pages/admin/config";

describe("Admin Config Page", () => {
  it("deve renderizar corretamente", () => {
    const { getByText } = render(<ConfigPage />);
    expect(getByText(/config/i)).toBeInTheDocument();
  });
});
