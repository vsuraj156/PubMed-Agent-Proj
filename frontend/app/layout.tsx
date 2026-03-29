import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PubMed Research Agent",
  description: "AI-powered clinical literature search",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-white text-gray-900 antialiased">{children}</body>
    </html>
  );
}
