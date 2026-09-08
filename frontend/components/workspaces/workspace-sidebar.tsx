"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  FileText,
  Trash2,
  RefreshCw,
  Search,
  FolderOpen,
} from "lucide-react";
import { DocumentRead, Workspace } from "@/lib/types";
import { deleteWorkspace } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { CreateWorkspaceDialog } from "./create-workspace-dialog";
import { UploadPdfDialog } from "./upload-pdf-dialog";
import { cn } from "@/lib/utils";

interface WorkspaceSidebarProps {
  mode: "list" | "active";
  workspaces?: Workspace[];
  activeWorkspace?: Workspace | null;
  documents?: DocumentRead[];
  onRefreshWorkspaces?: () => void;
  onRefreshDocuments?: () => void;
}

export function WorkspaceSidebar({
  mode,
  workspaces = [],
  activeWorkspace = null,
  documents = [],
  onRefreshWorkspaces,
  onRefreshDocuments,
}: WorkspaceSidebarProps) {
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [deletingWsId, setDeletingWsId] = useState<string | null>(null);

  const filteredWorkspaces = workspaces.filter((ws) =>
    ws.name.toLowerCase().includes(search.toLowerCase()) ||
    (ws.description && ws.description.toLowerCase().includes(search.toLowerCase()))
  );

  const handleDeleteWorkspace = async (e: React.MouseEvent, wsId: string) => {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm("Delete this workspace and all associated documents, facts, and embeddings?")) {
      return;
    }
    setDeletingWsId(wsId);
    try {
      await deleteWorkspace(wsId);
      if (onRefreshWorkspaces) {
        onRefreshWorkspaces();
      }
      if (activeWorkspace?.id === wsId) {
        router.push("/workspaces");
      }
    } catch {
      // ignore
    } finally {
      setDeletingWsId(null);
    }
  };

  const getStatusIndicator = (status: string) => {
    switch (status) {
      case "complete":
        return (
          <span className="flex items-center gap-1 text-[10px] text-emerald-600 dark:text-emerald-400 font-medium">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            Complete
          </span>
        );
      case "processing":
        return (
          <span className="flex items-center gap-1 text-[10px] text-amber-600 dark:text-amber-400 font-medium">
            <span className="h-1.5 w-1.5 rounded-full bg-amber-500 animate-ping" />
            Processing
          </span>
        );
      case "failed":
        return (
          <span className="flex items-center gap-1 text-[10px] text-destructive font-medium">
            <span className="h-1.5 w-1.5 rounded-full bg-destructive" />
            Failed
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 text-[10px] text-muted-foreground font-medium">
            <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground" />
            {status}
          </span>
        );
    }
  };

  if (mode === "active" && activeWorkspace) {
    // Mode B: Active Workspace selected -> Upload button & uploaded PDFs list
    return (
      <aside className="w-full lg:w-72 xl:w-80 shrink-0 border-r border-border/70 bg-card p-4 flex flex-col gap-4">
        {/* Header with Back button */}
        <div className="flex flex-col gap-2">
          <Link
            href="/workspaces"
            className={cn(
              buttonVariants({ variant: "ghost", size: "sm" }),
              "w-fit -ml-2 h-7 px-2 text-xs font-medium gap-1 text-muted-foreground hover:text-foreground"
            )}
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            <span>All Workspaces</span>
          </Link>

          <div className="flex items-start justify-between gap-2">
            <div>
              <h2 className="text-sm font-bold text-foreground font-mono truncate max-w-[200px]">
                {activeWorkspace.name}
              </h2>
              {activeWorkspace.description && (
                <p className="text-[11px] text-muted-foreground line-clamp-2 mt-0.5">
                  {activeWorkspace.description}
                </p>
              )}
            </div>
            <Badge variant="outline" className="text-[10px] font-mono shrink-0">
              {documents.length} docs
            </Badge>
          </div>
        </div>

        {/* Upload Button */}
        <div className="pt-1">
          <UploadPdfDialog
            workspaceId={activeWorkspace.id}
            onUploaded={onRefreshDocuments}
          />
        </div>

        {/* Documents section */}
        <div className="flex-1 flex flex-col min-h-0">
          <div className="flex items-center justify-between pb-2 border-b border-border/50">
            <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
              Uploaded PDFs ({documents.length})
            </span>
            {onRefreshDocuments && (
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 text-muted-foreground hover:text-foreground"
                onClick={onRefreshDocuments}
                title="Refresh Documents"
              >
                <RefreshCw className="h-3 w-3" />
              </Button>
            )}
          </div>

          <div className="flex-1 overflow-y-auto pt-2 space-y-2 max-h-[calc(100vh-280px)]">
            {documents.length === 0 ? (
              <div className="p-6 text-center rounded-lg border border-dashed border-border text-xs text-muted-foreground">
                No PDFs uploaded yet. Click Upload PDF to ingest annual reports or presentations.
              </div>
            ) : (
              documents.map((doc) => (
                <div
                  key={doc.id}
                  className="p-2.5 rounded-lg border border-border/70 bg-background hover:border-foreground/20 transition-colors text-xs space-y-1.5"
                >
                  <div className="flex items-start gap-2">
                    <FileText className="h-4 w-4 text-foreground shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <p className="font-mono text-[11px] font-medium text-foreground truncate" title={doc.filename}>
                        {doc.filename}
                      </p>
                      <div className="flex items-center justify-between mt-1">
                        {getStatusIndicator(doc.status)}
                        <span className="text-[10px] text-muted-foreground font-mono">
                          {doc.page_count} pgs
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </aside>
    );
  }

  // Mode A: All Workspaces list & Create workspace
  return (
    <aside className="w-full lg:w-72 xl:w-80 shrink-0 border-r border-border/70 bg-card p-4 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FolderOpen className="h-4 w-4 text-foreground" />
          <h2 className="text-sm font-bold text-foreground">Workspaces</h2>
        </div>
        <Badge variant="outline" className="text-[10px] font-mono">
          {workspaces.length} Total
        </Badge>
      </div>

      <CreateWorkspaceDialog onCreated={onRefreshWorkspaces} />

      <div className="relative">
        <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
        <Input
          placeholder="Filter workspaces..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-8 h-8 text-xs"
        />
      </div>

      <div className="flex-1 overflow-y-auto space-y-2 max-h-[calc(100vh-280px)]">
        {filteredWorkspaces.length === 0 ? (
          <div className="p-6 text-center rounded-lg border border-dashed border-border text-xs text-muted-foreground">
            {workspaces.length === 0
              ? "No workspaces created yet. Click 'New Workspace' to begin."
              : "No workspaces match your search."}
          </div>
        ) : (
          filteredWorkspaces.map((ws) => (
            <div
              key={ws.id}
              onClick={() => router.push(`/workspaces/${ws.id}`)}
              className="p-3 rounded-xl border border-border/70 bg-background hover:bg-muted/40 cursor-pointer transition-colors group space-y-1.5 relative"
            >
              <div className="flex items-start justify-between gap-2">
                <span className="font-semibold text-xs font-mono text-foreground group-hover:underline">
                  {ws.name}
                </span>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity text-destructive hover:text-destructive"
                  onClick={(e) => handleDeleteWorkspace(e, ws.id)}
                  disabled={deletingWsId === ws.id}
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>

              {ws.description && (
                <p className="text-[11px] text-muted-foreground line-clamp-2">
                  {ws.description}
                </p>
              )}

              <div className="flex items-center justify-between pt-1 text-[10px] text-muted-foreground">
                <span>{ws.document_count} document{ws.document_count === 1 ? "" : "s"}</span>
                <span className="font-mono">
                  {new Date(ws.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}
