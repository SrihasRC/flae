"use client";

import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

function GithubIcon({ className = "h-4 w-4" }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4" />
      <path d="M9 18c-4.51 2-5-2-7-2" />
    </svg>
  );
}

import { Suspense } from "react";

function NavbarContent() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  // Check if we are inside a specific workspace route: /workspaces/[id]
  const isWorkspaceDetail =
    pathname.startsWith("/workspaces/") &&
    pathname.split("/").filter(Boolean).length >= 2;

  const currentTab = searchParams.get("tab") || "ledger";

  return (
    <header className="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-[88%] max-w-6xl transition-all duration-300">
      <div className="flex items-center justify-between px-5 py-2.5 rounded-xl border border-border/70 bg-background/80 backdrop-blur-md shadow-md">
        {isWorkspaceDetail ? (
          <>
            {/* Workspace Mode: Left side with Back button */}
            <div className="flex items-center gap-3">
              <Link
                href="/workspaces"
                className={cn(
                  buttonVariants({ variant: "ghost", size: "sm" }),
                  "h-8 px-2.5 text-xs font-medium gap-1.5 text-muted-foreground hover:text-foreground"
                )}
              >
                <ArrowLeft className="h-3.5 w-3.5" />
                <span>Workspaces</span>
              </Link>
              <div className="h-4 w-[1px] bg-border hidden sm:block" />
              <div className="hidden sm:flex items-center gap-1.5">
                <span className="font-semibold text-sm tracking-tight text-foreground">
                  Workspace Dossier
                </span>
                <Badge variant="outline" className="text-[10px] py-0 px-1.5 font-mono">
                  Live
                </Badge>
              </div>
            </div>

            {/* Workspace Mode: Center 3-4 links */}
            <nav className="flex items-center gap-1 md:gap-2">
              <Link
                href={`${pathname}?tab=ledger`}
                className={`text-xs px-3 py-1.5 rounded-md font-medium transition-colors ${
                  currentTab === "ledger"
                    ? "bg-secondary text-foreground font-semibold"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Fact Ledger
              </Link>
              <Link
                href={`${pathname}?tab=arbitration`}
                className={`text-xs px-3 py-1.5 rounded-md font-medium transition-colors ${
                  currentTab === "arbitration"
                    ? "bg-secondary text-foreground font-semibold"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Arbitration
              </Link>
              <Link
                href={`${pathname}?tab=documents`}
                className={`text-xs px-3 py-1.5 rounded-md font-medium transition-colors ${
                  currentTab === "documents"
                    ? "bg-secondary text-foreground font-semibold"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Documents
              </Link>
              <Link
                href={`${pathname}?tab=query`}
                className={`text-xs px-3 py-1.5 rounded-md font-medium transition-colors hidden sm:inline-block ${
                  currentTab === "query"
                    ? "bg-secondary text-foreground font-semibold"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Query
              </Link>
            </nav>

            {/* Workspace Mode: Right side actions */}
            <div className="flex items-center gap-2">
              <a
                href="https://github.com/SrihasRC/flae"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="GitHub Repository"
                className={cn(
                  buttonVariants({ variant: "ghost", size: "icon" }),
                  "h-8 w-8 text-muted-foreground hover:text-foreground"
                )}
              >
                <GithubIcon className="h-4 w-4" />
              </a>
            </div>
          </>
        ) : (
          <>
            {/* Normal Mode: Left side Logo */}
            <div className="flex items-center gap-2.5">
              <Link href="/" className="flex items-center gap-2">
                <span className="font-extrabold text-sm tracking-tight text-foreground font-mono">
                  FLAE
                </span>
              </Link>
            </div>

            {/* Normal Mode: Center 3-4 links */}
            <nav className="hidden md:flex items-center gap-6">
              <Link
                href="/"
                className={`text-xs font-medium transition-colors ${
                  pathname === "/"
                    ? "text-foreground font-semibold"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Overview
              </Link>
              <Link
                href="/workspaces"
                className={`text-xs font-medium transition-colors ${
                  pathname.startsWith("/workspaces")
                    ? "text-foreground font-semibold"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Workspaces
              </Link>
              <Link
                href="/#architecture"
                className="text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                Architecture
              </Link>
              <Link
                href="/#cases"
                className="text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                Epistemic Cases
              </Link>
            </nav>

            {/* Normal Mode: Right side Actions */}
            <div className="flex items-center gap-2.5">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="GitHub Repository"
                className={cn(
                  buttonVariants({ variant: "ghost", size: "icon" }),
                  "h-8 w-8 text-muted-foreground hover:text-foreground"
                )}
              >
                <GithubIcon className="h-4 w-4" />
              </a>
            </div>
          </>
        )}
      </div>
    </header>
  );
}

export function FloatingNavbar() {
  return (
    <Suspense
      fallback={
        <header className="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-[88%] max-w-6xl">
          <div className="flex items-center justify-between px-5 py-2.5 rounded-xl border border-border/70 bg-background/80 backdrop-blur-md shadow-md">
            <span className="font-extrabold text-sm tracking-tight text-foreground font-mono">
              FLAE
            </span>
          </div>
        </header>
      }
    >
      <NavbarContent />
    </Suspense>
  );
}
