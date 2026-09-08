"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Workspace } from "@/lib/types";
import { listWorkspaces } from "@/lib/api";
import { buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { WorkspaceSidebar } from "@/components/workspaces/workspace-sidebar";
import { cn } from "@/lib/utils";

export default function WorkspacesPage() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);

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

    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="min-h-screen bg-canvas pt-28 sm:pt-32 pb-16 px-4 sm:px-6 lg:px-8 flex justify-center">
      <div className="w-full max-w-6xl flex flex-col lg:flex-row gap-8 items-start">
        {/* Left Sidebar in 'list' mode */}
        <WorkspaceSidebar
          mode="list"
          workspaces={workspaces}
          onRefreshWorkspaces={fetchWorkspaces}
        />

        {/* Right Side Dashboard */}
        <main className="flex-1 min-w-0 space-y-8">
          {/* Welcome Header */}
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground font-serif">
              Select or Create a Workspace
            </h1>
            <p className="text-xs sm:text-sm text-muted-foreground mt-1 max-w-2xl">
              Each workspace maintains an isolated fact ledger, high-dimensional semantic vector index,
              and pairwise arbitration graph. Select an existing workspace from the sidebar or dossier cards below.
            </p>
          </div>

          {/* Dynamic Workspace Cards */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-muted-claude uppercase tracking-wider font-mono">
                Active Dossiers ({workspaces.length})
              </span>
              <span className="text-[11px] text-muted-soft font-mono">
                Total Filings: {workspaces.reduce((acc, w) => acc + (w.document_count || 0), 0)}
              </span>
            </div>

            {workspaces.length === 0 ? (
              <Card className="border border-dashed border-hairline shadow-xs bg-surface-card/60 p-8 text-center space-y-3">
                <p className="text-sm font-medium text-foreground">No workspaces found</p>
                <p className="text-xs text-muted-foreground max-w-md mx-auto">
                  Create your first workspace using the &quot;New Workspace&quot; button in the sidebar to ingest filings and generate an atomic fact ledger.
                </p>
              </Card>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {workspaces.map((ws) => {
                  const docCount = ws.document_count ?? 0;
                  const factCount = ws.fact_count ?? 0;

                  return (
                    <Card
                      key={ws.id}
                      className="border border-border/80 shadow-xs bg-card hover:border-ink/20 transition-all group"
                    >
                      <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                          <span className="text-[11px] text-muted-foreground font-mono">
                            {docCount} Document{docCount === 1 ? "" : "s"}
                          </span>
                          <span className="text-[11px] text-muted-soft font-mono">
                            Created {new Date(ws.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        <CardTitle className="text-base font-bold font-mono text-foreground mt-1 group-hover:text-ink">
                          {ws.name}
                        </CardTitle>
                        <p className="text-xs text-muted-foreground">
                          {ws.description || "Isolated domain partition for regulatory filings and fact arbitration."}
                        </p>
                      </CardHeader>
                      <CardContent className="pt-0 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                        <div className="text-xs text-muted-foreground">
                          {docCount === 0 ? (
                            <span>No filings ingested yet. Upload corporate reports or presentations to extract atomic facts.</span>
                          ) : factCount > 0 ? (
                            <span>
                              Contains <strong>{factCount.toLocaleString()}</strong> atomic facts ready for ledger inspection and cross-document epistemic arbitration.
                            </span>
                          ) : (
                            <span>
                              Contains {docCount} document{docCount === 1 ? "" : "s"} ready for ledger inspection and arbitration.
                            </span>
                          )}
                        </div>
                        <Link
                          href={`/workspaces/${ws.id}`}
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
                  );
                })}
              </div>
            )}
          </div>

          {/* Workflow guide */}
          <div className="p-5 rounded-xl border border-border/70 bg-card space-y-3">
            <h3 className="text-sm font-semibold text-foreground">Next Steps:</h3>
            <ol className="list-decimal list-inside text-xs text-muted-foreground space-y-1.5 leading-relaxed">
              <li>
                Click on any workspace above or in the sidebar to view extracted facts and arbitration results.
              </li>
              <li>
                Upload additional PDFs via the <strong>Upload PDF</strong> button in the active workspace sidebar.
              </li>
              <li>
                Run arbitration to compare claims across documents with full reasoning traces.
              </li>
            </ol>
          </div>
        </main>
      </div>
    </div>
  );
}
