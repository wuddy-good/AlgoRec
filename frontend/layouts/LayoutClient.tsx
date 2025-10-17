'use client';

import { usePathname } from "next/navigation";
import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import Footer from "@/components/Footer";

export default function LayoutClient({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const isHomePage = pathname === '/';

  return (
    <>
      <Header />
      {isHomePage ? (
        <main className="flex-1">
          {children}
        </main>
      ) : (
        <div className="flex flex-1">
          <Sidebar />
          <main className="flex-1">
            {children}
          </main>
        </div>
      )}
      <Footer />
    </>
  );
}
