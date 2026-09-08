"use client";

import { use, useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { DocumentRead, Workspace } from "@/lib/types";
import { getWorkspace, listDocuments } from "@/lib/api";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { WorkspaceSidebar } from "@/components/workspaces/workspace-sidebar";
import { FactLedgerTable } from "@/components/workspaces/fact-ledger-table";
import { ArbitrationView } from "@/components/workspaces/arbitration-view";
import { DocumentDossierTab } from "@/components/workspaces/document-dossier-tab";
import { SemanticQueryTab } from "@/components/workspaces/semantic-query-tab";

interface WorkspaceDetailPageProps {
  params: Promise<{ id: string }>;
}

function WorkspaceDetailContent({ workspaceId }: { workspaceId: string }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const currentTab = searchParams.get("tab") || "ledger";

  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [documents, setDocuments] = useState<DocumentRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const fetchWorkspaceData = () => {
    setRefreshTrigger((r) => r + 1);
  };

  useEffect(() => {
    let active = true;

    Promise.all([
      getWorkspace(workspaceId),
      listDocuments(workspaceId),
    ])
      .then(([ws, docsRes]) => {
        if (!active) return;
        setWorkspace(ws);
        setDocuments(docsRes.documents || []);
        setError(null);
        setLoading(false);
      })
      .catch((err: unknown) => {
        if (!active) return;
        setError(err instanceof Error ? err.message : "Failed to load workspace data");
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [workspaceId, refreshTrigger]);

  const handleTabChange = (value: string | number | null) => {
    if (!value) return;
    const strVal = String(value);
    const params = new URLSearchParams(searchParams.toString());
    params.set("tab", strVal);
    router.replace(`?${params.toString()}`);
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center p-12 pt-28 text-xs text-muted-foreground">
        Loading workspace dossier...
      </div>
    );
  }

  if (error || !workspace) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-12 pt-28 space-y-3">
        <div className="text-sm font-semibold text-destructive">
          {error || "Workspace not found"}
        </div>
        <button
          onClick={() => router.push("/workspaces")}
          className="text-xs text-foreground underline"
        >
          Return to Workspaces Hub
        </button>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col lg:flex-row min-h-screen pt-20">
      {/* Left Sidebar in 'active' mode */}
      <WorkspaceSidebar
        mode="active"
        activeWorkspace={workspace}
        documents={documents}
        onRefreshDocuments={fetchWorkspaceData}
      />

      {/* Right Side 4-Tab Classified Layout */}
      <main className="flex-1 p-4 lg:p-6 bg-muted/10 overflow-y-auto">
        <div className="max-w-6xl mx-auto space-y-6">
          <Tabs
            value={currentTab}
            onValueChange={handleTabChange}
            className="w-full space-y-4"
          >
            {/* Tab navigation strip */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-border/60 pb-3">
              <div>
                <h1 className="text-xl font-bold tracking-tight text-foreground font-mono">
                  {workspace.name}
                </h1>
                <p className="text-xs text-muted-foreground mt-0.5">
                  FLAE Epistemic Fact Knowledge Base & Multi-Document Adjudication
                </p>
              </div>

              <TabsList className="h-9 p-1">
                <TabsTrigger value="ledger" className="text-xs px-3 font-medium">
                  Fact Ledger
                </TabsTrigger>
                <TabsTrigger value="arbitration" className="text-xs px-3 font-medium">
                  Arbitration
                </TabsTrigger>
                <TabsTrigger value="documents" className="text-xs px-3 font-medium">
                  Documents ({documents.length})
                </TabsTrigger>
                <TabsTrigger value="query" className="text-xs px-3 font-medium">
                  Query Search
                </TabsTrigger>
              </TabsList>
            </div>

            {/* Tab 1: Atomic Fact Ledger */}
            <TabsContent value="ledger" className="mt-0">
              <FactLedgerTable workspaceId={workspace.id} documents={documents} />
            </TabsContent>

            {/* Tab 2: Arbitration & Discrepancies */}
            <TabsContent value="arbitration" className="mt-0">
              <ArbitrationView workspaceId={workspace.id} />
            </TabsContent>

            {/* Tab 3: Document Dossier */}
            <TabsContent value="documents" className="mt-0">
              <DocumentDossierTab
                workspaceId={workspace.id}
                documents={documents}
                onRefresh={fetchWorkspaceData}
              />
            </TabsContent>

            {/* Tab 4: Semantic Query Explorer */}
            <TabsContent value="query" className="mt-0">
              <SemanticQueryTab workspaceId={workspace.id} />
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  );
}

export default function WorkspaceDetailPage({ params }: WorkspaceDetailPageProps) {
  const unwrappedParams = use(params);

  return (
    <Suspense
      fallback={
        <div className="flex-1 flex items-center justify-center p-12 text-xs text-muted-foreground">
          Loading workspace...
        </div>
      }
    >
      <WorkspaceDetailContent workspaceId={unwrappedParams.id} />
    </Suspense>
  );
}
