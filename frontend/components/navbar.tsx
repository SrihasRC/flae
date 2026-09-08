"use client";

import { Suspense } from "react";
import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { HugeiconsIcon } from "@hugeicons/react";
import { GithubIcon } from "@hugeicons/core-free-icons";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

function AnthropicRadialSpike({ className = "h-3.5 w-3.5" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2L13.5 8.5L20 10L13.5 11.5L12 18L10.5 11.5L4 10L10.5 8.5L12 2Z" />
    </svg>
  );
}

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
      <div className="flex items-center justify-between px-5 py-2.5 rounded-xl border border-primary/15 bg-canvas/25 dark:bg-surface-dark/25 backdrop-blur-md shadow-xs">
        {isWorkspaceDetail ? (
          <>
            {/* Workspace Mode: Left side with Back button */}
            <div className="flex items-center gap-3">
              <Link
                href="/workspaces"
                className={cn(
                  buttonVariants({ variant: "ghost", size: "sm" }),
                  "h-8 px-2.5 text-xs font-medium gap-1.5 text-muted-claude hover:text-ink dark:hover:text-canvas"
                )}
              >
                <ArrowLeft className="h-3.5 w-3.5" />
                <span>Workspaces</span>
              </Link>
            </div>

            {/* Workspace Mode: Center 3-4 links */}
            <nav className="flex items-center gap-1 md:gap-2">
              <Link
                href={`${pathname}?tab=ledger`}
                className={`text-xs px-3 py-1.5 rounded-md font-medium transition-colors ${
                  currentTab === "ledger"
                    ? "bg-surface-card text-ink font-semibold dark:bg-surface-dark-elevated dark:text-canvas"
                    : "text-muted-claude hover:text-ink dark:hover:text-canvas"
                }`}
              >
                Fact Ledger
              </Link>
              <Link
                href={`${pathname}?tab=arbitration`}
                className={`text-xs px-3 py-1.5 rounded-md font-medium transition-colors ${
                  currentTab === "arbitration"
                    ? "bg-surface-card text-ink font-semibold dark:bg-surface-dark-elevated dark:text-canvas"
                    : "text-muted-claude hover:text-ink dark:hover:text-canvas"
                }`}
              >
                Arbitration
              </Link>
              <Link
                href={`${pathname}?tab=documents`}
                className={`text-xs px-3 py-1.5 rounded-md font-medium transition-colors ${
                  currentTab === "documents"
                    ? "bg-surface-card text-ink font-semibold dark:bg-surface-dark-elevated dark:text-canvas"
                    : "text-muted-claude hover:text-ink dark:hover:text-canvas"
                }`}
              >
                Documents
              </Link>
              <Link
                href={`${pathname}?tab=query`}
                className={`text-xs px-3 py-1.5 rounded-md font-medium transition-colors hidden sm:inline-block ${
                  currentTab === "query"
                    ? "bg-surface-card text-ink font-semibold dark:bg-surface-dark-elevated dark:text-canvas"
                    : "text-muted-claude hover:text-ink dark:hover:text-canvas"
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
                  "h-8 w-8 text-muted-claude hover:text-ink dark:hover:text-canvas"
                )}
              >
                <HugeiconsIcon icon={GithubIcon} size={18} strokeWidth={1.5} />
              </a>
            </div>
          </>
        ) : (
          <>
            {/* Normal Mode: Left side Logo */}
            <div className="flex items-center gap-2.5">
              <Link href="/" className="flex items-center gap-2">
                <AnthropicRadialSpike className="h-4 w-4 text-coral" />
                <span className="font-extrabold text-sm tracking-tight text-ink dark:text-canvas font-mono">
                  FLAE
                </span>
              </Link>
            </div>

            {/* Normal Mode: Center 3-4 links leading to separate pages */}
            <nav className="hidden md:flex items-center gap-6">
              <Link
                href="/"
                className={`text-xs font-medium transition-colors ${
                  pathname === "/"
                    ? "text-ink dark:text-canvas font-semibold"
                    : "text-muted-claude hover:text-ink dark:hover:text-canvas"
                }`}
              >
                Overview
              </Link>
              <Link
                href="/workspaces"
                className={`text-xs font-medium transition-colors ${
                  pathname.startsWith("/workspaces")
                    ? "text-ink dark:text-canvas font-semibold"
                    : "text-muted-claude hover:text-ink dark:hover:text-canvas"
                }`}
              >
                Workspaces
              </Link>
              <Link
                href="/docs"
                className={`text-xs font-medium transition-colors ${
                  pathname === "/docs"
                    ? "text-ink dark:text-canvas font-semibold"
                    : "text-muted-claude hover:text-ink dark:hover:text-canvas"
                }`}
              >
                Architecture & Docs
              </Link>
            </nav>

            {/* Normal Mode: Right side Actions */}
            <div className="flex items-center gap-2.5">
              <a
                href="https://github.com/SrihasRC/flae"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="GitHub Repository"
                className={cn(
                  buttonVariants({ variant: "ghost", size: "icon" }),
                  "h-8 w-8 text-black hover:text-ink dark:hover:text-canvas"
                )}
              >
                <HugeiconsIcon icon={GithubIcon} size={18} strokeWidth={2} />
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
          <div className="flex items-center justify-between px-5 py-2.5 rounded-xl border border-hairline bg-canvas/90 backdrop-blur-md shadow-xs">
            <span className="font-extrabold text-sm tracking-tight text-ink font-mono">
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
