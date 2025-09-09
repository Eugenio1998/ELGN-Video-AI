// frontend_tests/tests_pages/_app.test.tsx

import { render } from "@testing-library/react";
import MyApp from "@/pages/_app";
import { describe, expect, it, vi } from "vitest";
import { NextRouter } from "next/router";

// 🔁 Mock completo do NextRouter
const mockRouter: NextRouter = {
  basePath: "",
  pathname: "/",
  route: "/",
  asPath: "/",
  query: {},
  push: vi.fn(),
  replace: vi.fn(),
  reload: vi.fn(),
  back: vi.fn(),
  forward: vi.fn(),
  prefetch: vi.fn().mockResolvedValue(undefined),
  beforePopState: vi.fn(),
  events: {
    on: vi.fn(),
    off: vi.fn(),
    emit: vi.fn(),
  },
  isFallback: false,
  isReady: true,
  isLocaleDomain: false,
  isPreview: false,
};

// ✅ Substitui o hook do Next.js por nosso mock
vi.mock("next/router", () => ({
  useRouter: () => mockRouter,
}));

const DummyComponent = () => <div>App Renderizado</div>;

describe("_app.tsx", () => {
  it("deve renderizar corretamente", () => {
    const pageProps = {};
    const { getByText } = render(
      <MyApp Component={DummyComponent} pageProps={pageProps} />
    );
    expect(getByText("App Renderizado")).toBeInTheDocument();
  });
});
