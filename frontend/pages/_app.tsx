// 📁 pages/_app.tsx
import type { AppProps } from "next/app";
import "../src/app/globals.css";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "../i18n/i18n";

import { AppProviders } from "../context/AppProviders";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

export default function MyApp({ Component, pageProps }: AppProps) {
  return (
    <AppProviders>
      <div className="min-h-screen flex flex-col bg-black text-white transition-colors duration-300">
        <Navbar />
        <main className="flex-grow">
          <Component {...pageProps} />
        </main>
        <Footer />
        <ToastContainer position="top-right" autoClose={3000} hideProgressBar />
      </div>
    </AppProviders>
  );
}
