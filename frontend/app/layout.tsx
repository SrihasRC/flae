import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { TooltipProvider } from "@/components/ui/tooltip";
import { FloatingNavbar } from "@/components/navbar";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "FLAE — Epistemic Fact-Ledger & Arbitration Engine",
  description:
    "FLAE: Deterministic Atomic Fact Ledger and Cross-Document Arbitration Engine resolving discrepancies across corporate reports, financial dossiers, and filings.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-background text-foreground selection:bg-foreground selection:text-background">
        <TooltipProvider>
          <FloatingNavbar />
          <div className="flex-1 flex flex-col pt-20">{children}</div>
        </TooltipProvider>
      </body>
    </html>
  );
}
