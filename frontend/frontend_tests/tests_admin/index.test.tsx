import { render } from "@testing-library/react";
import AdminHome from "@/pages/admin";

describe("Admin Index Page", () => {
  it("deve renderizar corretamente", () => {
    const { getByText } = render(<AdminHome />);
    expect(getByText(/admin/i)).toBeInTheDocument();
  });
});
