import { render } from "@testing-library/react";
import UsersPage from "@/pages/admin/users";

describe("Admin Users Page", () => {
  it("deve renderizar corretamente", () => {
    const { getByText } = render(<UsersPage />);
    expect(getByText(/users/i)).toBeInTheDocument();
  });
});
