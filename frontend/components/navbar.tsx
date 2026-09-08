"use client";

import { Suspense } from "react";
import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { HugeiconsIcon } from "@hugeicons/react";
import { GithubIcon } from "@hugeicons/core-free-icons";
import { Badge } from "@/components/ui/badge";
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
      <div className="flex items-center justify-between px-5 py-2.5 rounded-xl border border-[#e6dfd8] bg-[#faf9f5]/90 dark:bg-[#181715]/90 backdrop-blur-md shadow-xs">
        {isWorkspaceDetail ? (
          <>
            {/* Workspace Mode: Left side with Back button */}
            <div className="flex items-center gap-3">
              <Link
                href="/workspaces"
                className={cn(
                  buttonVariants({ variant: "ghost", size: "sm" }),
                  "h-8 px-2.5 text-xs font-medium gap-1.5 text-[#6c6a64] hover:text-[#141413] dark:hover:text-[#faf9f5]"
                )}
              >
                <ArrowLeft className="h-3.5 w-3.5" />
                <span>Workspaces</span>
              </Link>
              <div className="h-4 w-px bg-hairline hidden sm:block" />
              <div className="hidden sm:flex items-center gap-1.5">
                <AnthropicRadialSpike className="h-3 w-3 text-coral" />
                <span className="font-semibold text-xs tracking-tight text-[#141413] dark:text-[#faf9f5]">
                  Dossier Console
                </span>
                <Badge variant="pill" className="text-[10px] py-0 px-1.5 font-mono">
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
                    ? "bg-[#efe9de] text-[#141413] font-semibold dark:bg-[#252320] dark:text-[#faf9f5]"
                    : "text-[#6c6a64] hover:text-[#141413] dark:hover:text-[#faf9f5]"
                }`}
              >
                Fact Ledger
              </Link>
              <Link
                href={`${pathname}?tab=arbitration`}
                className={`text-xs px-3 py-1.5 rounded-md font-medium transition-colors ${
                  currentTab === "arbitration"
                    ? "bg-[#efe9de] text-[#141413] font-semibold dark:bg-[#252320] dark:text-[#faf9f5]"
                    : "text-[#6c6a64] hover:text-[#141413] dark:hover:text-[#faf9f5]"
                }`}
              >
                Arbitration
              </Link>
              <Link
                href={`${pathname}?tab=documents`}
                className={`text-xs px-3 py-1.5 rounded-md font-medium transition-colors ${
                  currentTab === "documents"
                    ? "bg-[#efe9de] text-[#141413] font-semibold dark:bg-[#252320] dark:text-[#faf9f5]"
                    : "text-[#6c6a64] hover:text-[#141413] dark:hover:text-[#faf9f5]"
                }`}
              >
                Documents
              </Link>
              <Link
                href={`${pathname}?tab=query`}
                className={`text-xs px-3 py-1.5 rounded-md font-medium transition-colors hidden sm:inline-block ${
                  currentTab === "query"
                    ? "bg-[#efe9de] text-[#141413] font-semibold dark:bg-[#252320] dark:text-[#faf9f5]"
                    : "text-[#6c6a64] hover:text-[#141413] dark:hover:text-[#faf9f5]"
                }`}
              >
                Query
              </Link>
            </nav>

            {/* Workspace Mode: Right side actions */}
            <div className="flex items-center gap-2">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="GitHub Repository"
                className={cn(
                  buttonVariants({ variant: "ghost", size: "icon" }),
                  "h-8 w-8 text-[#6c6a64] hover:text-[#141413] dark:hover:text-[#faf9f5]"
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
                <AnthropicRadialSpike className="h-4 w-4 text-[#cc785c]" />
                <span className="font-extrabold text-sm tracking-tight text-[#141413] dark:text-[#faf9f5] font-mono">
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
                    ? "text-[#141413] dark:text-[#faf9f5] font-semibold"
                    : "text-[#6c6a64] hover:text-[#141413] dark:hover:text-[#faf9f5]"
                }`}
              >
                Overview
              </Link>
              <Link
                href="/workspaces"
                className={`text-xs font-medium transition-colors ${
                  pathname.startsWith("/workspaces")
                    ? "text-[#141413] dark:text-[#faf9f5] font-semibold"
                    : "text-[#6c6a64] hover:text-[#141413] dark:hover:text-[#faf9f5]"
                }`}
              >
                Workspaces
              </Link>
              <Link
                href="/docs"
                className={`text-xs font-medium transition-colors ${
                  pathname === "/docs"
                    ? "text-[#141413] dark:text-[#faf9f5] font-semibold"
                    : "text-[#6c6a64] hover:text-[#141413] dark:hover:text-[#faf9f5]"
                }`}
              >
                Architecture & Docs
              </Link>
              <Link
                href="/cases"
                className={`text-xs font-medium transition-colors ${
                  pathname === "/cases"
                    ? "text-[#141413] dark:text-[#faf9f5] font-semibold"
                    : "text-[#6c6a64] hover:text-[#141413] dark:hover:text-[#faf9f5]"
                }`}
              >
                Case Studies
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
                  "h-8 w-8 text-[#6c6a64] hover:text-[#141413] dark:hover:text-[#faf9f5]"
                )}
              >
                <HugeiconsIcon icon={GithubIcon} size={18} strokeWidth={1.5} />
              </a>
              <Link
                href="/workspaces"
                className={cn(
                  buttonVariants({ variant: "coral", size: "sm" }),
                  "h-8 text-xs font-medium px-3.5 shadow-xs"
                )}
              >
                Launch Console
              </Link>
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
          <div className="flex items-center justify-between px-5 py-2.5 rounded-xl border border-[#e6dfd8] bg-[#faf9f5]/90 backdrop-blur-md shadow-xs">
            <span className="font-extrabold text-sm tracking-tight text-[#141413] font-mono">
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
