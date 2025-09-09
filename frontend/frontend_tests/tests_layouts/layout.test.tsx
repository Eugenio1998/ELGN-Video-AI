import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import RootLayout from "@/layouts/layout";
import * as useGlobalLoadingHook from "@/hooks/useGlobalLoading";

// 🛠️ Corrige mocks com `default`
vi.mock("@/components/Navbar", () => ({
  default: () => <nav>Navbar</nav>,
}));
vi.mock("@/components/Footer", () => ({
  default: () => <footer>Footer</footer>,
}));
vi.mock("@/components/ui/shared/LoadingOverlay", () => ({
  LoadingOverlay: () => <div>Loading...</div>,
}));
vi.mock("@/context/AppProviders", () => ({
  AppProviders: ({ children }: { children: React.ReactNode }) => (
    <>{children}</>
  ),
}));
vi.mock("@/i18n", () => ({}));

describe("RootLayout", () => {
  it("deve renderizar o conteúdo filho com navbar e footer", () => {
    vi.spyOn(useGlobalLoadingHook, "useGlobalLoading").mockReturnValue({
      loading: false,
    });

    const LayoutWithChildren = () => (
      <RootLayout>
        <div>Conteúdo de Teste</div>
      </RootLayout>
    );

    render(<LayoutWithChildren />);

    expect(screen.getByText("Navbar")).toBeInTheDocument();
    expect(screen.getByText("Footer")).toBeInTheDocument();
    expect(screen.getByText("Conteúdo de Teste")).toBeInTheDocument();
  });

  it("deve exibir o LoadingOverlay quando loading for true", () => {
    vi.spyOn(useGlobalLoadingHook, "useGlobalLoading").mockReturnValue({
      loading: true,
    });

    const LayoutWithLoading = () => (
      <RootLayout>
        <div>Conteúdo de Teste</div>
      </RootLayout>
    );

    render(<LayoutWithLoading />);

    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });
});
