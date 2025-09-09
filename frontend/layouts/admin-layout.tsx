// 📁 layouts/admin-layout.tsx
"use client";

import { AppProviders } from "../context/AppProviders";
import "@/src/app/globals.css";
import Head from "next/head";
import { metadata } from "../layouts/metadata";
import { useGlobalLoading } from "../hooks/useGlobalLoading";
import { LoadingOverlay } from "../components/ui/shared/LoadingOverlay";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { loading } = useGlobalLoading();

  return (
    <AppProviders>
      <Head>
        <title>{metadata.title} - Admin</title>
        <meta name="description" content={metadata.description} />
        <meta property="og:title" content={`${metadata.title} - Admin`} />
        <meta property="og:description" content={metadata.description} />
        <meta property="og:image" content={metadata.openGraph.images[0].url} />
      </Head>
      <div className="dark bg-[#0a0a0a] text-white min-h-screen flex">
        {/* Você pode adicionar aqui futuramente: <SidebarAdmin /> */}
        <main className="flex-grow p-6">{children}</main>
        {loading && <LoadingOverlay />}
      </div>
    </AppProviders>
  );
}
