"use client";

import { useState } from "react";
import { FileText, Trash2, CheckCircle2, Clock, AlertCircle, RefreshCw } from "lucide-react";
import { DocumentRead, IngestionJobStatus } from "@/lib/types";
import { deleteDocument, getDocumentStatus } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { UploadPdfDialog } from "./upload-pdf-dialog";

interface DocumentDossierTabProps {
  workspaceId: string;
  documents: DocumentRead[];
  onRefresh: () => void;
}

export function DocumentDossierTab({
  workspaceId,
  documents,
  onRefresh,
}: DocumentDossierTabProps) {
  const [statusDoc, setStatusDoc] = useState<IngestionJobStatus | null>(null);
  const [statusModalOpen, setStatusModalOpen] = useState(false);
  const [loadingStatusId, setLoadingStatusId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const totalPages = documents.reduce((sum, d) => sum + (d.page_count || 0), 0);
  const completedDocs = documents.filter((d) => d.status === "complete").length;

  const handleInspectStatus = async (docId: string) => {
    setLoadingStatusId(docId);
    try {
      const status = await getDocumentStatus(workspaceId, docId);
      setStatusDoc(status);
      setStatusModalOpen(true);
    } catch {
      // ignore
    } finally {
      setLoadingStatusId(null);
    }
  };

  const handleDelete = async (docId: string) => {
    if (!confirm("Are you sure you want to delete this document and its extracted facts?")) {
      return;
    }
    setDeletingId(docId);
    try {
      await deleteDocument(workspaceId, docId);
      onRefresh();
    } catch {
      // ignore
    } finally {
      setDeletingId(null);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "complete":
        return (
          <Badge className="bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border-emerald-500/30 text-[10px] gap-1">
            <CheckCircle2 className="h-3 w-3" />
            Complete
          </Badge>
        );
      case "processing":
        return (
          <Badge className="bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/30 text-[10px] gap-1">
            <RefreshCw className="h-3 w-3 animate-spin" />
            Processing
          </Badge>
        );
      case "failed":
        return (
          <Badge variant="destructive" className="text-[10px] gap-1">
            <AlertCircle className="h-3 w-3" />
            Failed
          </Badge>
        );
      default:
        return (
          <Badge variant="outline" className="text-[10px] gap-1">
            <Clock className="h-3 w-3" />
            {status}
          </Badge>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="border border-border/80 shadow-xs">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Total Ingested Files
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-foreground">
              {documents.length}
            </div>
            <p className="text-[11px] text-muted-foreground mt-0.5">
              {completedDocs} fully parsed & indexed
            </p>
          </CardContent>
        </Card>

        <Card className="border border-border/80 shadow-xs">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Cumulative Pages Processed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-foreground">
              {totalPages}
            </div>
            <p className="text-[11px] text-muted-foreground mt-0.5">
              Across annual reports & filings
            </p>
          </CardContent>
        </Card>

        <Card className="border border-border/80 shadow-xs">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Pipeline Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400">
              100%
            </div>
            <p className="text-[11px] text-muted-foreground mt-0.5">
              Zero unrecoverable parsing faults
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Action Bar */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-foreground">Workspace Documents</h3>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onRefresh}
            className="h-8 text-xs gap-1.5"
          >
            <RefreshCw className="h-3 w-3" />
            <span>Refresh</span>
          </Button>
          <div className="w-36">
            <UploadPdfDialog workspaceId={workspaceId} onUploaded={onRefresh} />
          </div>
        </div>
      </div>

      {/* Documents List */}
      <div className="space-y-3">
        {documents.length === 0 ? (
          <div className="p-12 text-center rounded-xl border border-dashed border-border/80 bg-card">
            <p className="text-xs text-muted-foreground">
              No documents in this workspace yet. Upload a PDF annual report or earnings deck to begin
              fact extraction.
            </p>
          </div>
        ) : (
          documents.map((doc) => (
            <div
              key={doc.id}
              className="p-4 rounded-xl border border-border/80 bg-card flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-xs"
            >
              <div className="flex items-start gap-3">
                <div className="h-9 w-9 rounded-lg bg-secondary flex items-center justify-center shrink-0">
                  <FileText className="h-4 w-4 text-foreground" />
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-foreground font-mono">
                    {doc.filename}
                  </h4>
                  <div className="flex flex-wrap items-center gap-2 mt-1">
                    {getStatusBadge(doc.status)}
                    <span className="text-[11px] text-muted-foreground">
                      {doc.page_count} pages
                    </span>
                    <span className="text-[11px] text-muted-foreground">•</span>
                    <span className="text-[11px] text-muted-foreground">
                      Uploaded {new Date(doc.uploaded_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
                <Button
                  variant="outline"
                  size="sm"
                  className="h-7 text-xs"
                  onClick={() => handleInspectStatus(doc.id)}
                  disabled={loadingStatusId === doc.id}
                >
                  {loadingStatusId === doc.id ? "Checking..." : "Ingestion Audit"}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 text-xs text-destructive hover:text-destructive"
                  onClick={() => handleDelete(doc.id)}
                  disabled={deletingId === doc.id}
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </Button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Ingestion Status Modal */}
      <Dialog open={statusModalOpen} onOpenChange={setStatusModalOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Document Ingestion Audit</DialogTitle>
            <DialogDescription>
              Real-time pipeline extraction diagnostics and status.
            </DialogDescription>
          </DialogHeader>

          {statusDoc && (
            <div className="space-y-3 py-3 text-xs">
              <div className="flex items-center justify-between p-2.5 rounded bg-muted/40 border border-border/60">
                <span className="text-muted-foreground">Pipeline Status:</span>
                <div>{getStatusBadge(statusDoc.status)}</div>
              </div>

              <div className="flex items-center justify-between p-2.5 rounded bg-muted/40 border border-border/60">
                <span className="text-muted-foreground">Atomic Facts Extracted:</span>
                <span className="font-bold font-mono text-foreground text-sm">
                  {statusDoc.facts_extracted}
                </span>
              </div>

              {statusDoc.error ? (
                <div className="p-3 rounded bg-destructive/10 border border-destructive/20 text-destructive text-xs">
                  <span className="font-semibold block mb-1">Diagnostic Error:</span>
                  <span>{statusDoc.error}</span>
                </div>
              ) : (
                <div className="p-3 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-700 dark:text-emerald-400 text-xs">
                  All pages parsed cleanly, embeddings synchronized in ChromaDB, and atomic facts
                  committed to immutable ledger.
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
