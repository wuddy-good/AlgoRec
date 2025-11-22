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
  
  // Show sidebar for all pages except home page
  // This includes 404, profile, dashboard, catalog, etc.
  const showSidebar = !isHomePage;

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      {showSidebar ? (
        <div className="flex flex-1">
          <Sidebar />
          <main className="flex-1">
            {children}
          </main>
        </div>
      ) : (
        <main className="flex-1">
          {children}
        </main>
      )}
      <Footer />
    </div>
  );
}
