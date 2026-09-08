"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { HealthResponse, Workspace } from "@/lib/types";
import { getHealth, listWorkspaces } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { WorkspaceSidebar } from "@/components/workspaces/workspace-sidebar";
import { cn } from "@/lib/utils";

export default function WorkspacesPage() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [health, setHealth] = useState<HealthResponse | null>(null);

  const fetchWorkspaces = () => {
    listWorkspaces()
      .then((res) => setWorkspaces(res.workspaces || []))
      .catch(() => {});
  };

  useEffect(() => {
    let active = true;

    listWorkspaces()
      .then((res) => {
        if (active) setWorkspaces(res.workspaces || []);
      })
      .catch(() => {});

    getHealth()
      .then((res) => {
        if (active) setHealth(res);
      })
      .catch(() => {});

    return () => {
      active = false;
    };
  }, []);

  const delhiveryWs = workspaces.find((w) => w.name.toLowerCase().includes("delhivery"));

  return (
    <div className="flex-1 flex flex-col lg:flex-row min-h-screen pt-20 p-4 lg:p-6 gap-6 bg-canvas">
      {/* Left Sidebar in 'list' mode */}
      <WorkspaceSidebar
        mode="list"
        workspaces={workspaces}
        onRefreshWorkspaces={fetchWorkspaces}
      />

      {/* Right Side Placeholder / Hub Dashboard */}
      <main className="flex-1 min-w-0 overflow-y-auto">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Welcome Header */}
          <div>
            <Badge variant="outline" className="text-xs font-mono mb-2">
              Workspace Central
            </Badge>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
              Select or Create a Workspace
            </h1>
            <p className="text-xs sm:text-sm text-muted-foreground mt-1 max-w-2xl">
              Each workspace maintains an isolated fact ledger, high-dimensional semantic vector index,
              and pairwise arbitration graph. Select an existing workspace from the sidebar or inspect the
              pre-loaded test dossier below.
            </p>
          </div>

          {/* Quick Spotlight Card: Delhivery Dossier */}
          {delhiveryWs && (
            <Card className="border border-border/80 shadow-xs bg-card">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <Badge variant="secondary" className="text-[10px] font-mono">
                    Starter Dataset Pre-loaded
                  </Badge>
                  <span className="text-[11px] text-muted-foreground font-mono">
                    {delhiveryWs.document_count} Documents
                  </span>
                </div>
                <CardTitle className="text-base font-bold font-mono text-foreground mt-1">
                  {delhiveryWs.name}
                </CardTitle>
                <p className="text-xs text-muted-foreground">
                  {delhiveryWs.description || "Delhivery FY24 Annual Report and Earnings Presentation"}
                </p>
              </CardHeader>
              <CardContent className="pt-0 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="text-xs text-muted-foreground">
                  Contains over 3,600 atomic facts ready for ledger inspection and cross-document
                  epistemic arbitration.
                </div>
                <Link
                  href={`/workspaces/${delhiveryWs.id}`}
                  className={cn(
                    buttonVariants({ size: "sm" }),
                    "text-xs font-medium gap-1.5 shrink-0"
                  )}
                >
                  <span>Enter Workspace</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </CardContent>
            </Card>
          )}

          {/* System Health Strip */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card className="border border-border/70 shadow-xs">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Enterprise Core Engine
                </CardTitle>
              </CardHeader>
              <CardContent className="flex items-center justify-between">
                <span className="text-sm font-semibold text-foreground">
                  {health?.service || "fact-ledger-engine"}
                </span>
                <Badge className="bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 text-[10px] border-emerald-500/30">
                  {health?.status || "online"}
                </Badge>
              </CardContent>
            </Card>

            <Card className="border border-border/70 shadow-xs">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Immutable Audit Ledger
                </CardTitle>
              </CardHeader>
              <CardContent className="flex items-center justify-between">
                <span className="text-sm font-semibold text-foreground">Atomic Ledger</span>
                <Badge className="bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 text-[10px] border-emerald-500/30">
                  {health?.database || "connected"}
                </Badge>
              </CardContent>
            </Card>

            <Card className="border border-border/70 shadow-xs">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Semantic Vector Index
                </CardTitle>
              </CardHeader>
              <CardContent className="flex items-center justify-between">
                <span className="text-sm font-semibold text-foreground">Context Index</span>
                <Badge className="bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 text-[10px] border-emerald-500/30">
                  {health?.vector_store || "connected"}
                </Badge>
              </CardContent>
            </Card>
          </div>

          {/* Workflow guide */}
          <div className="p-5 rounded-xl border border-border/70 bg-card space-y-3">
            <h3 className="text-sm font-semibold text-foreground">Next Steps:</h3>
            <ol className="list-decimal list-inside text-xs text-muted-foreground space-y-1.5 leading-relaxed">
              <li>
                Click on <strong>{delhiveryWs?.name || "delhivery"}</strong> in the sidebar to view extracted facts and arbitration results.
              </li>
              <li>
                Upload additional PDFs via the <strong>Upload PDF</strong> button in the active workspace sidebar.
              </li>
              <li>
                Run arbitration to compare claims across documents with full reasoning traces.
              </li>
            </ol>
          </div>
        </div>
      </main>
    </div>
  );
}
