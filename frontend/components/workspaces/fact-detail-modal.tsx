"use client";

import { FactRead } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface FactDetailModalProps {
  fact: FactRead | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function FactDetailModal({ fact, open, onOpenChange }: FactDetailModalProps) {
  if (!fact) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="outline" className="text-[10px] font-mono">
              Fact ID: {fact.fact_id.slice(0, 8)}...
            </Badge>
            {fact.context_envelope?.temporal_period && (
              <Badge variant="secondary" className="text-[10px]">
                {fact.context_envelope.temporal_period}
              </Badge>
            )}
            {fact.context_envelope?.entity_scope && (
              <Badge variant="outline" className="text-[10px] uppercase font-mono">
                {fact.context_envelope.entity_scope}
              </Badge>
            )}
          </div>
          <DialogTitle className="text-lg font-bold">{fact.attribute}</DialogTitle>
          <DialogDescription className="text-xs">
            Subject: <strong className="text-foreground">{fact.subject}</strong>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2 text-xs">
          {/* Values Section */}
          <div className="p-3 rounded-lg bg-muted/40 border border-border/60 grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <span className="text-[11px] text-muted-foreground uppercase tracking-wider block mb-0.5">
                Raw Extracted Value
              </span>
              <span className="text-sm font-semibold text-foreground font-mono">
                {fact.value_raw}
              </span>
            </div>
            <div>
              <span className="text-[11px] text-muted-foreground uppercase tracking-wider block mb-0.5">
                Normalized Numeric & Unit
              </span>
              <span className="text-sm font-semibold text-foreground font-mono">
                {fact.value_numeric !== null && fact.value_numeric !== undefined
                  ? fact.value_numeric.toLocaleString()
                  : "N/A"}
                {fact.unit ? ` (${fact.unit})` : ""}
              </span>
            </div>
          </div>

          {/* Context Envelope */}
          <div className="space-y-2">
            <h4 className="font-semibold text-xs text-foreground uppercase tracking-wider">
              6-D Context Envelope
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
              <div className="p-2 rounded border border-border/60 bg-card">
                <span className="text-[10px] text-muted-foreground block">Temporal Period</span>
                <span className="font-medium text-foreground">
                  {fact.context_envelope?.temporal_period || "Unspecified"}
                </span>
              </div>
              <div className="p-2 rounded border border-border/60 bg-card">
                <span className="text-[10px] text-muted-foreground block">Period Type</span>
                <span className="font-medium text-foreground">
                  {fact.context_envelope?.period_type || "Unspecified"}
                </span>
              </div>
              <div className="p-2 rounded border border-border/60 bg-card">
                <span className="text-[10px] text-muted-foreground block">Entity Scope</span>
                <span className="font-medium text-foreground">
                  {fact.context_envelope?.entity_scope || "Unspecified"}
                </span>
              </div>
              <div className="p-2 rounded border border-border/60 bg-card">
                <span className="text-[10px] text-muted-foreground block">Accounting Standard</span>
                <span className="font-medium text-foreground">
                  {fact.context_envelope?.accounting_methodology || "Unspecified"}
                </span>
              </div>
              <div className="p-2 rounded border border-border/60 bg-card">
                <span className="text-[10px] text-muted-foreground block">Geography</span>
                <span className="font-medium text-foreground">
                  {fact.context_envelope?.geography || "Unspecified"}
                </span>
              </div>
              <div className="p-2 rounded border border-border/60 bg-card">
                <span className="text-[10px] text-muted-foreground block">Qualifiers</span>
                <span className="font-medium text-foreground truncate block">
                  {fact.context_envelope?.additional_qualifiers || "None"}
                </span>
              </div>
            </div>
          </div>

          {/* Verbatim Evidence Quote */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <h4 className="font-semibold text-xs text-foreground uppercase tracking-wider">
                Verbatim Evidence Quote
              </h4>
              <Badge variant="outline" className="text-[10px] font-mono">
                Page {fact.evidence?.page_number || "N/A"}
              </Badge>
            </div>
            <div className="p-3 rounded-lg bg-muted/50 border border-border/80 italic text-foreground leading-relaxed">
              &ldquo;{fact.evidence?.verbatim_quote || "No verbatim citation recorded."}&rdquo;
            </div>
            {fact.evidence?.section_title && (
              <p className="text-[11px] text-muted-foreground">
                Section: {fact.evidence.section_title}
              </p>
            )}
          </div>

          {/* Raw JSON Trace */}
          <div className="space-y-1 pt-2">
            <span className="text-[10px] text-muted-foreground font-mono">Raw Fact JSON</span>
            <pre className="p-2.5 rounded bg-muted/60 border border-border/50 text-[10px] font-mono overflow-x-auto max-h-40">
              {JSON.stringify(fact, null, 2)}
            </pre>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
