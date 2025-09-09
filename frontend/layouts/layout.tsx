// 📁 app/layout.tsx (App Router)
import "@/src/app/globals.css";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { AppProviders } from "../context/AppProviders";
import "../i18n/i18n";
import { useGlobalLoading } from "../hooks/useGlobalLoading";
import { LoadingOverlay } from "../components/ui/shared/LoadingOverlay";

export const metadata = {
  title: "ELGN Video.AI",
  description: "Editor de vídeo inteligente com IA",
  openGraph: {
    title: "ELGN Video.AI",
    description: "Editor de vídeo com inteligência artificial",
    url: "https://elgn.ai",
    siteName: "ELGN AI",
    locale: "pt_BR",
    images: [{ url: "https://elgn.ai/og-image.jpg" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "ELGN Video.AI",
    description: "Editor de vídeo inteligente",
    image: "https://elgn.ai/twitter-image.jpg",
    site: "@elgnai",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { loading } = useGlobalLoading();

  return (
    <html lang="pt" className="dark">
      <body className="bg-black text-white min-h-screen flex flex-col">
        <AppProviders>
          <Navbar />
          <main className="flex-grow">{children}</main>
          <Footer />
          <ToastContainer
            position="top-right"
            autoClose={3000}
            hideProgressBar
          />
          {loading && <LoadingOverlay />}
        </AppProviders>
      </body>
    </html>
  );
}
