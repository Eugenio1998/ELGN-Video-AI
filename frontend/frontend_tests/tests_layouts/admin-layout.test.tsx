// frontend_tests/tests_layouts/admin-layout.test.tsx
import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import AdminLayout from "@/layouts/admin-layout";
import { GlobalLoadingProvider } from "@/context/GlobalLoadingContext";

describe("AdminLayout", () => {
  it("deve renderizar o conteúdo filho", () => {
    render(
      <GlobalLoadingProvider>
        <AdminLayout>
          <div>Conteúdo Admin</div>
        </AdminLayout>
      </GlobalLoadingProvider>
    );

    expect(screen.getByText("Conteúdo Admin")).toBeInTheDocument();
  });
});
