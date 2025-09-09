// frontend_tests/tests_layouts/auth-layout.test.tsx
import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import AuthLayout from "@/layouts/auth-layout";
import { GlobalLoadingProvider } from "@/context/GlobalLoadingContext";

describe("AuthLayout", () => {
  it("deve renderizar o conteúdo filho", () => {
    render(
      <GlobalLoadingProvider>
        <AuthLayout>
          <div>Conteúdo Teste</div>
        </AuthLayout>
      </GlobalLoadingProvider>
    );

    expect(screen.getByText("Conteúdo Teste")).toBeInTheDocument();
  });
});
