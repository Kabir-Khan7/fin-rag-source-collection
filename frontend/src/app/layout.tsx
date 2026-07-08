import type { Metadata } from "next";
import { Toaster } from "@/components/ui/sonner";
import { ActivityProvider } from "@/context/ActivityContext";
import "./globals.css";

export const metadata: Metadata = {
  title: "Local RAG System",
  description: "Source Collection portal",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <ActivityProvider>
          {children}
          <Toaster richColors position="top-right" />
        </ActivityProvider>
      </body>
    </html>
  );
}