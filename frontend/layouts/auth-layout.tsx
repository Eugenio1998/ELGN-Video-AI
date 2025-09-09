// 📁 layouts/auth-layout.tsx
"use client";

import "@/src/app/globals.css";
import { AppProviders } from "../context/AppProviders";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import Head from "next/head";
import { metadata } from "../layouts/metadata";
import { useGlobalLoading } from "../hooks/useGlobalLoading";
import { LoadingOverlay } from "../components/ui/shared/LoadingOverlay";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { loading } = useGlobalLoading();

  return (
    <AppProviders>
      <Head>
        <title>{metadata.title} - Acesso</title>
        <meta name="description" content={metadata.description} />
        <meta property="og:title" content={`${metadata.title} - Login`} />
        <meta property="og:description" content={metadata.description} />
        <meta property="og:image" content={metadata.openGraph.images[0].url} />
      </Head>
      <div className="dark bg-black text-white min-h-screen flex items-center justify-center p-4">
        <div className="w-full max-w-md space-y-6">{children}</div>
        <ToastContainer position="top-right" autoClose={3000} hideProgressBar />
        {loading && <LoadingOverlay />}
      </div>
    </AppProviders>
  );
}
