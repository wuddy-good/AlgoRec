import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import LayoutClient from "@/layouts/LayoutClient";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "RecoMind - Personalized Recommendations",
  description: "Discover your next favorite books and movies with AI-powered recommendations",
  icons: {
    icon: [
      { url: "/logo2.svg?v=1", type: "image/svg+xml" },
      { url: "/logo2.svg?v=1" },
    ],
    shortcut: "/logo2.svg?v=1",
    apple: "/logo2.svg?v=1",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} min-h-screen flex flex-col`}>
        <LayoutClient>{children}</LayoutClient>
      </body>
    </html>
  );
}
