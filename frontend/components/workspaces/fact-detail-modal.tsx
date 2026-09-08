"use client";

import { useState } from "react";
import { FactRead } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  cleanText,
  formatAttribute,
  formatValue,
  formatEvidenceQuote,
  getFactCategory,
} from "@/lib/formatters";
import { ChevronDown, ChevronRight, Copy, Check, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface FactDetailModalProps {
  fact: FactRead | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function FactDetailModal({ fact, open, onOpenChange }: FactDetailModalProps) {
  const [jsonExpanded, setJsonExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!fact) return null;

  const cleanAttr = formatAttribute(fact.attribute);
  const formattedVal = formatValue(fact.value_raw, fact.value_numeric, fact.unit);
  const cleanQuote = formatEvidenceQuote(fact.evidence?.verbatim_quote);
  const cat = getFactCategory(fact.attribute, fact.subject, fact.unit);

  const handleCopyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(fact, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl w-[95vw] sm:w-full max-h-[88vh] overflow-y-auto overflow-x-hidden p-6 space-y-5 bg-canvas border border-hairline shadow-lg">
        <DialogHeader className="space-y-2 border-b border-hairline pb-4 text-left">
          <div className="flex flex-wrap items-center gap-1.5">
            <span
              className={cn(
                "text-[10px] font-mono px-2 py-0.5 rounded-xs border uppercase tracking-wider font-semibold",
                cat.badgeVariant === "teal" && "bg-accent-teal/10 text-accent-teal border-accent-teal/30",
                cat.badgeVariant === "coral" && "bg-coral/10 text-coral border-coral/30",
                cat.badgeVariant === "amber" && "bg-accent-amber/10 text-accent-amber border-accent-amber/30",
                cat.badgeVariant === "outline" && "bg-surface-soft text-muted-claude border-hairline"
              )}
            >
              {cat.label}
            </span>
            {cat.isHeadline && (
              <span className="text-[10px] font-mono font-bold text-coral px-1.5 py-0.5 rounded-xs bg-coral/10 border border-coral/30 flex items-center gap-1">
                <Star className="h-3 w-3 fill-coral text-coral" />
                <span>Headline KPI</span>
              </span>
            )}
            <Badge variant="pill" className="text-[10px] font-mono">
              ID: {fact.fact_id.slice(0, 8)}
            </Badge>
            {fact.evidence?.page_number && (
              <Badge variant="outline" className="text-[10px] font-mono">
                Page {fact.evidence.page_number}
              </Badge>
            )}
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

          <DialogTitle className="text-xl font-serif font-bold text-ink leading-snug break-words">
            {cleanAttr}
          </DialogTitle>

          <DialogDescription className="text-xs text-muted-claude space-y-1 block">
            <span className="block">
              Entity Subject: <strong className="text-ink">{cleanText(fact.subject)}</strong>
            </span>
            <span className="block text-[11px] text-body">
              Domain Scope: <span className="font-medium text-ink">{cat.definition}</span>
            </span>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 text-xs">
          {/* Primary Value Card */}
          <div className="p-4 rounded-xl bg-surface-card border border-hairline space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-semibold text-muted-claude uppercase tracking-wider">
                Extracted Fact Value
              </span>
              {fact.unit && (
                <Badge variant="pill" className="text-[10px] font-mono">
                  Unit: {fact.unit}
                </Badge>
              )}
            </div>

            <div
              className={cn(
                "text-ink tracking-tight break-words",
                formattedVal.isNumeric
                  ? "text-2xl sm:text-3xl font-bold font-mono"
                  : "text-sm sm:text-base font-medium leading-relaxed font-sans"
              )}
            >
              {formattedVal.primary}
            </div>

            {formattedVal.breakdown && formattedVal.breakdown.length > 1 && (
              <div className="pt-2 border-t border-hairline/60">
                <span className="text-[10px] text-muted-claude uppercase tracking-wider block mb-1.5">
                  Sub-Values / Multi-Period Breakdown:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {formattedVal.breakdown.map((item, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 rounded bg-canvas border border-hairline text-ink font-mono text-[11px] break-words"
                    >
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* 6-Dimensional Context Envelope Grid */}
          <div className="space-y-2">
            <h4 className="font-semibold text-xs text-ink uppercase tracking-wider">
              6-Dimensional Context Envelope
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              <div className="p-2.5 rounded-lg border border-hairline bg-surface-soft/60">
                <span className="text-[10px] text-muted-claude uppercase block">Temporal Period</span>
                <span className="font-medium text-ink break-words">
                  {fact.context_envelope?.temporal_period || "Unspecified"}
                </span>
              </div>
              <div className="p-2.5 rounded-lg border border-hairline bg-surface-soft/60">
                <span className="text-[10px] text-muted-claude uppercase block">Period Type</span>
                <span className="font-medium text-ink break-words capitalize">
                  {fact.context_envelope?.period_type || "Unspecified"}
                </span>
              </div>
              <div className="p-2.5 rounded-lg border border-hairline bg-surface-soft/60">
                <span className="text-[10px] text-muted-claude uppercase block">Entity Scope</span>
                <span className="font-medium text-ink break-words capitalize">
                  {fact.context_envelope?.entity_scope || "Unspecified"}
                </span>
              </div>
              <div className="p-2.5 rounded-lg border border-hairline bg-surface-soft/60">
                <span className="text-[10px] text-muted-claude uppercase block">Accounting Standard</span>
                <span className="font-medium text-ink break-words">
                  {fact.context_envelope?.accounting_methodology
                    ? fact.context_envelope.accounting_methodology.replace(/_/g, " ").toUpperCase()
                    : "Unspecified"}
                </span>
              </div>
              <div className="p-2.5 rounded-lg border border-hairline bg-surface-soft/60">
                <span className="text-[10px] text-muted-claude uppercase block">Geography</span>
                <span className="font-medium text-ink break-words">
                  {fact.context_envelope?.geography || "India"}
                </span>
              </div>
              <div className="p-2.5 rounded-lg border border-hairline bg-surface-soft/60">
                <span className="text-[10px] text-muted-claude uppercase block">Qualifiers</span>
                <span className="font-medium text-ink break-words">
                  {fact.context_envelope?.additional_qualifiers || "None"}
                </span>
              </div>
            </div>
          </div>

          {/* Verbatim Citation Section */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <h4 className="font-semibold text-xs text-ink uppercase tracking-wider">
                Verbatim Evidence Citation
              </h4>
              <Badge variant="outline" className="text-[10px] font-mono">
                Page {fact.evidence?.page_number ?? "N/A"}
              </Badge>
            </div>
            <div className="p-3.5 rounded-xl bg-canvas border border-hairline italic text-body text-xs leading-relaxed break-words">
              &ldquo;{cleanQuote}&rdquo;
            </div>
            {fact.evidence?.section_title && (
              <p className="text-[11px] text-muted-claude">
                Section: {cleanText(fact.evidence.section_title)}
              </p>
            )}
          </div>

          {/* Collapsible Clean Raw JSON Trace */}
          <div className="border border-hairline rounded-xl overflow-hidden">
            <div
              onClick={() => setJsonExpanded(!jsonExpanded)}
              className="flex items-center justify-between p-3 bg-surface-soft/70 cursor-pointer hover:bg-surface-soft transition-colors select-none"
            >
              <div className="flex items-center gap-1.5 text-xs font-medium text-ink">
                {jsonExpanded ? (
                  <ChevronDown className="h-3.5 w-3.5 text-muted-claude" />
                ) : (
                  <ChevronRight className="h-3.5 w-3.5 text-muted-claude" />
                )}
                <span>Inspect Immutable Fact Record (JSON)</span>
              </div>
              <Button
                variant="ghost"
                size="xs"
                onClick={(e) => {
                  e.stopPropagation();
                  handleCopyJson();
                }}
                className="h-6 text-[11px] gap-1 text-muted-claude hover:text-ink"
              >
                {copied ? (
                  <>
                    <Check className="h-3 w-3 text-emerald-600" />
                    <span>Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="h-3 w-3" />
                    <span>Copy JSON</span>
                  </>
                )}
              </Button>
            </div>

            {jsonExpanded && (
              <div className="p-3 bg-surface-dark text-canvas border-t border-hairline max-h-56 overflow-y-auto">
                <pre className="text-[11px] font-mono leading-relaxed whitespace-pre-wrap break-all">
                  {JSON.stringify(fact, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
