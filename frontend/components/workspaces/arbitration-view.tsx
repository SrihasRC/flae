"use client";

import { useEffect, useState } from "react";
import {
  RefreshCw,
  Play,
  CheckCircle2,
  AlertTriangle,
  GitCompare,
  FileSearch,
} from "lucide-react";
import {
  ArbitrationRead,
  ArbitrationRelationship,
  CaseExplorerResponse,
} from "@/lib/types";
import {
  getArbitrationCases,
  listArbitrations,
  triggerArbitration,
} from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface ArbitrationViewProps {
  workspaceId: string;
}

export function ArbitrationView({ workspaceId }: ArbitrationViewProps) {
  const [viewMode, setViewMode] = useState<"showcase" | "all">("showcase");
  const [activeCase, setActiveCase] = useState<"1" | "2" | "3" | "4">("1");
  const [casesData, setCasesData] = useState<CaseExplorerResponse | null>(null);

  // All arbitrations list
  const [arbitrations, setArbitrations] = useState<ArbitrationRead[]>([]);
  const [total, setTotal] = useState(0);
  const [relationshipFilter, setRelationshipFilter] = useState<string>("");
  const [loading, setLoading] = useState(true);

  // Triggering arbitration
  const [running, setRunning] = useState(false);
  const [forceRerun, setForceRerun] = useState(false);
  const [runMessage, setRunMessage] = useState<string | null>(null);

  const [refreshTrigger, setRefreshTrigger] = useState(0);

  useEffect(() => {
    let active = true;

    getArbitrationCases(workspaceId)
      .then((data) => {
        if (active) setCasesData(data);
      })
      .catch(() => {});

    listArbitrations(workspaceId, {
      relationship: relationshipFilter || undefined,
      limit: 100,
    })
      .then((res) => {
        if (!active) return;
        setArbitrations(res.arbitrations || []);
        setTotal(res.total || 0);
        setLoading(false);
      })
      .catch(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [workspaceId, relationshipFilter, refreshTrigger]);

  const handleRunArbitration = async () => {
    setRunning(true);
    setRunMessage(null);
    try {
      const res = await triggerArbitration(workspaceId, forceRerun);
      setRunMessage(res.message || "Arbitration job dispatched successfully.");
      setTimeout(() => {
        setRefreshTrigger((r) => r + 1);
      }, 3000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setRunMessage(`Error: ${msg}`);
    } finally {
      setRunning(false);
    }
  };

  const getRelationshipBadge = (rel: ArbitrationRelationship) => {
    switch (rel) {
      case "CORROBORATED":
        return (
          <Badge className="bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border-emerald-500/30 text-xs gap-1 font-semibold">
            <CheckCircle2 className="h-3 w-3" />
            CORROBORATED
          </Badge>
        );
      case "CONTRADICTED":
        return (
          <Badge variant="destructive" className="text-xs gap-1 font-semibold">
            <AlertTriangle className="h-3 w-3" />
            CONTRADICTED
          </Badge>
        );
      case "RECONCILED":
        return (
          <Badge className="bg-indigo-500/15 text-indigo-700 dark:text-indigo-400 border-indigo-500/30 text-xs gap-1 font-semibold">
            <GitCompare className="h-3 w-3" />
            RECONCILED
          </Badge>
        );
      default:
        return (
          <Badge variant="outline" className="text-xs">
            {rel}
          </Badge>
        );
    }
  };

  // Render showcase items for Case 1, 2, 3, or Case 4 note
  const getActiveShowcaseList = (): ArbitrationRead[] => {
    if (!casesData) return [];
    if (activeCase === "1") return casesData.case_1_corroborated || [];
    if (activeCase === "2") return casesData.case_2_contradicted || [];
    if (activeCase === "3") return casesData.case_3_reconciled || [];
    return [];
  };

  const currentDisplayList =
    viewMode === "showcase" ? getActiveShowcaseList() : arbitrations;

  return (
    <div className="space-y-6">
      {/* Top action header */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 p-4 rounded-xl border border-border/70 bg-card">
        <div>
          <h3 className="text-sm font-bold text-foreground">
            Cross-Document Fact Arbitration Engine
          </h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            Pairwise semantic matching across documents to identify corroboration, contradiction,
            or epistemic reconciliation.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <label className="flex items-center gap-1.5 text-xs text-muted-foreground cursor-pointer">
            <input
              type="checkbox"
              checked={forceRerun}
              onChange={(e) => setForceRerun(e.target.checked)}
              className="rounded border-border"
            />
            <span>Force Rerun</span>
          </label>

          <Button
            size="sm"
            onClick={handleRunArbitration}
            disabled={running}
            className="text-xs font-medium gap-1.5"
          >
            {running ? (
              <RefreshCw className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Play className="h-3.5 w-3.5" />
            )}
            <span>{running ? "Dispatching..." : "Run Arbitration"}</span>
          </Button>
        </div>
      </div>

      {runMessage && (
        <div className="p-3 rounded-lg bg-secondary/50 border border-border text-xs text-foreground flex items-center justify-between">
          <span>{runMessage}</span>
          <Button
            variant="ghost"
            size="sm"
            className="h-6 text-xs px-2"
            onClick={() => setRefreshTrigger((r) => r + 1)}
          >
            Refresh Now
          </Button>
        </div>
      )}

      {/* Mode Switcher */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="flex items-center gap-1 bg-muted p-1 rounded-lg">
          <Button
            variant={viewMode === "showcase" ? "default" : "ghost"}
            size="sm"
            className="h-7 text-xs font-medium px-3"
            onClick={() => setViewMode("showcase")}
          >
            Case 1–4 Showcase
          </Button>
          <Button
            variant={viewMode === "all" ? "default" : "ghost"}
            size="sm"
            className="h-7 text-xs font-medium px-3"
            onClick={() => setViewMode("all")}
          >
            All Results ({total})
          </Button>
        </div>

        {viewMode === "all" ? (
          <div className="flex items-center gap-1.5">
            {["", "CORROBORATED", "CONTRADICTED", "RECONCILED"].map((rel) => (
              <Button
                key={rel || "ALL"}
                variant={relationshipFilter === rel ? "secondary" : "outline"}
                size="sm"
                className="h-7 text-[11px] px-2.5"
                onClick={() => setRelationshipFilter(rel)}
              >
                {rel || "ALL"}
              </Button>
            ))}
          </div>
        ) : (
          <div className="flex flex-wrap items-center gap-1.5">
            <Button
              variant={activeCase === "1" ? "secondary" : "outline"}
              size="sm"
              className="h-7 text-xs px-2.5 gap-1"
              onClick={() => setActiveCase("1")}
            >
              Case 1: Corroborated
            </Button>
            <Button
              variant={activeCase === "2" ? "secondary" : "outline"}
              size="sm"
              className="h-7 text-xs px-2.5 gap-1"
              onClick={() => setActiveCase("2")}
            >
              Case 2: Contradicted
            </Button>
            <Button
              variant={activeCase === "3" ? "secondary" : "outline"}
              size="sm"
              className="h-7 text-xs px-2.5 gap-1"
              onClick={() => setActiveCase("3")}
            >
              Case 3: Reconciled
            </Button>
            <Button
              variant={activeCase === "4" ? "secondary" : "outline"}
              size="sm"
              className="h-7 text-xs px-2.5 gap-1"
              onClick={() => setActiveCase("4")}
            >
              Case 4: Failure Audits
            </Button>
          </div>
        )}
      </div>

      {/* Case 4 special explainer */}
      {viewMode === "showcase" && activeCase === "4" && (
        <Card className="border border-border/80 bg-muted/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <FileSearch className="h-4 w-4 text-foreground" />
              Case 4: Extraction & Reasoning Failure Analysis (Audit Trail)
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground space-y-2">
            <p>
              In strict regulatory auditing, extraction failures (e.g. unparseable scanned tables,
              ambiguous currency abbreviations, or unresolvable temporal windows) are not discarded.
              They are logged with explicit failure diagnostics.
            </p>
            <p>
              Check the <strong>Documents</strong> tab or view document ingestion status logs to inspect
              any malformed records or boundary mismatch audits.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Arbitration items list */}
      {loading && viewMode === "all" ? (
        <div className="p-12 text-center text-xs text-muted-foreground">
          Loading arbitration results...
        </div>
      ) : currentDisplayList.length === 0 && !(viewMode === "showcase" && activeCase === "4") ? (
        <div className="p-12 text-center rounded-xl border border-dashed border-border/80 bg-card space-y-3">
          <p className="text-xs text-muted-foreground">
            {viewMode === "showcase"
              ? "No arbitration cases registered for this category yet. Click 'Run Arbitration' above to generate cross-document comparisons."
              : "No arbitration results found."}
          </p>
          <Button
            size="sm"
            onClick={handleRunArbitration}
            disabled={running}
            className="text-xs font-medium"
          >
            Trigger Arbitration Job
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          {currentDisplayList.map((item) => (
            <Card key={item.arbitration_id} className="border border-border/80 shadow-xs">
              <CardHeader className="pb-3 pt-4 px-4 border-b border-border/40">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    {getRelationshipBadge(item.relationship)}
                    {item.divergence_factor && (
                      <Badge variant="outline" className="text-[11px] font-mono">
                        {item.divergence_factor}
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary" className="text-[10px] font-mono">
                      Confidence: {(item.confidence_score * 100).toFixed(0)}%
                    </Badge>
                    <span className="text-[10px] text-muted-foreground font-mono">
                      ID: {item.arbitration_id.slice(0, 8)}
                    </span>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="p-4 space-y-4 text-xs">
                {/* Evidence Comparison Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="p-3 rounded-lg bg-muted/40 border border-border/50 space-y-1.5">
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="font-semibold text-foreground uppercase tracking-wider text-[10px]">
                        Fact A Evidence
                      </span>
                      <Badge variant="outline" className="text-[10px] font-mono">
                        Page {item.evidence_comparison?.fact_a_page}
                      </Badge>
                    </div>
                    <blockquote className="italic text-foreground/90 leading-relaxed text-[11px]">
                      &ldquo;{item.evidence_comparison?.fact_a_quote}&rdquo;
                    </blockquote>
                  </div>

                  <div className="p-3 rounded-lg bg-muted/40 border border-border/50 space-y-1.5">
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="font-semibold text-foreground uppercase tracking-wider text-[10px]">
                        Fact B Evidence
                      </span>
                      <Badge variant="outline" className="text-[10px] font-mono">
                        Page {item.evidence_comparison?.fact_b_page}
                      </Badge>
                    </div>
                    <blockquote className="italic text-foreground/90 leading-relaxed text-[11px]">
                      &ldquo;{item.evidence_comparison?.fact_b_quote}&rdquo;
                    </blockquote>
                  </div>
                </div>

                {/* Reasoning Trace */}
                <div className="space-y-1 pt-1 border-t border-border/40">
                  <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
                    Arbiter Reasoning Trace
                  </span>
                  <p className="text-xs text-foreground/90 leading-relaxed bg-muted/20 p-2.5 rounded-md border border-border/40">
                    {item.reasoning_trace}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
