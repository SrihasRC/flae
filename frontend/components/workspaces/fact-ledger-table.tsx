"use client";

import { useEffect, useState } from "react";
import { Search, ChevronLeft, ChevronRight, Filter, X } from "lucide-react";
import { DocumentRead, FactRead } from "@/lib/types";
import { listFacts } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cleanText, formatAttribute, formatValue } from "@/lib/formatters";
import { FactDetailModal } from "./fact-detail-modal";
import { cn } from "@/lib/utils";

interface FactLedgerTableProps {
  workspaceId: string;
  documents: DocumentRead[];
}

export function FactLedgerTable({ workspaceId, documents }: FactLedgerTableProps) {
  const [facts, setFacts] = useState<FactRead[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters & pagination
  const [searchInput, setSearchInput] = useState("");
  const [activeSearch, setActiveSearch] = useState("");
  const [selectedDocId, setSelectedDocId] = useState<string>("");
  const [page, setPage] = useState(0);
  const limit = 25;

  // Selected fact for detail modal
  const [selectedFact, setSelectedFact] = useState<FactRead | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);

  useEffect(() => {
    let active = true;
    listFacts(workspaceId, {
      document_id: selectedDocId || undefined,
      query: activeSearch.trim() || undefined,
      skip: page * limit,
      limit,
    })
      .then((res) => {
        if (!active) return;
        setFacts(res.facts || []);
        setTotal(res.total || 0);
        setError(null);
        setLoading(false);
      })
      .catch((err: unknown) => {
        if (!active) return;
        setError(err instanceof Error ? err.message : "Failed to load facts");
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [workspaceId, selectedDocId, page, activeSearch]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setPage(0);
    setActiveSearch(searchInput);
  };

  const handleClearSearch = () => {
    setSearchInput("");
    setActiveSearch("");
    setPage(0);
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="space-y-4">
      {/* Top filter toolbar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 bg-surface-card p-3 rounded-sm border border-hairline shadow-xs">
        <form onSubmit={handleSearchSubmit} className="flex-1 flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-claude" />
            <Input
              placeholder="Search across metrics, attributes, values (e.g. Revenue, EBITDA, Options)..."
              value={searchInput}
              onChange={(e) => {
                setSearchInput(e.target.value);
                if (e.target.value === "" && activeSearch !== "") {
                  setActiveSearch("");
                  setPage(0);
                }
              }}
              className="pl-8 pr-8 h-8 text-xs w-full rounded-sm border-hairline bg-canvas text-ink"
            />
            {searchInput && (
              <button
                type="button"
                onClick={handleClearSearch}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-claude hover:text-ink transition-colors"
                title="Clear search"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            )}
          </div>
          <Button type="submit" size="sm" variant="secondary" className="h-8 text-xs font-medium px-3 rounded-sm border border-hairline">
            Search
          </Button>
          {activeSearch && (
            <Button
              type="button"
              size="sm"
              variant="ghost"
              onClick={handleClearSearch}
              className="h-8 text-xs font-medium px-2 text-muted-claude hover:text-ink rounded-sm"
            >
              Reset
            </Button>
          )}
        </form>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 text-xs text-muted-claude font-medium">
            <Filter className="h-3.5 w-3.5" />
            <span className="hidden md:inline">Document:</span>
          </div>
          <select
            value={selectedDocId}
            onChange={(e) => {
              setSelectedDocId(e.target.value);
              setPage(0);
            }}
            className="h-8 text-xs rounded-sm border border-hairline bg-canvas px-2.5 py-1 text-ink focus:outline-none focus:ring-1 focus:ring-ring"
          >
            <option value="">All Documents ({documents.length})</option>
            {documents.map((doc) => (
              <option key={doc.id} value={doc.id}>
                {doc.filename.length > 35 ? `${doc.filename.slice(0, 35)}...` : doc.filename}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Summary count */}
      <div className="flex items-center justify-between px-1">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-ink font-mono">Atomic Fact Ledger</span>
          <Badge variant="outline" className="text-[10px] font-mono rounded-xs">
            {total.toLocaleString()} facts
          </Badge>
          {activeSearch && (
            <span className="text-[11px] text-muted-claude">
              matching &quot;{activeSearch}&quot;
            </span>
          )}
        </div>
        <span className="text-[11px] text-muted-claude font-mono">
          Showing {total === 0 ? 0 : page * limit + 1}–{Math.min((page + 1) * limit, total)} of {total}
        </span>
      </div>

      {/* Table container */}
      <div className="rounded-sm border border-hairline bg-canvas overflow-hidden shadow-xs">
        {loading ? (
          <div className="p-12 text-center text-xs text-muted-claude">
            Loading facts from ledger...
          </div>
        ) : error ? (
          <div className="p-8 text-center text-xs text-destructive">
            {error}
          </div>
        ) : facts.length === 0 ? (
          <div className="p-12 text-center text-xs text-muted-claude">
            No facts found matching query or document filter.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <Table className="table-fixed w-full min-w-[700px]">
              <TableHeader className="bg-surface-soft/60 text-muted-claude border-b border-hairline">
                <TableRow className="hover:bg-transparent">
                  <TableHead className="w-[18%] text-xs font-semibold text-ink">Subject</TableHead>
                  <TableHead className="w-[32%] text-xs font-semibold text-ink">Attribute / Assertion</TableHead>
                  <TableHead className="w-[22%] text-xs font-semibold text-ink">Extracted Value</TableHead>
                  <TableHead className="w-[18%] text-xs font-semibold text-ink">Context Envelope</TableHead>
                  <TableHead className="w-[10%] text-xs font-semibold text-ink text-right">Evidence</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {facts.map((fact) => {
                  const cleanSubj = cleanText(fact.subject);
                  const cleanAttr = formatAttribute(fact.attribute);
                  const formattedVal = formatValue(fact.value_raw, fact.value_numeric, fact.unit);                    return (
                      <TableRow
                        key={fact.fact_id}
                        className="cursor-pointer hover:bg-surface-soft/50 transition-colors border-b border-hairline/60"
                        onClick={() => {
                          setSelectedFact(fact);
                          setDetailOpen(true);
                        }}
                      >
                        <TableCell className="w-[18%] max-w-0 font-medium text-xs text-ink truncate" title={cleanSubj}>
                          {cleanSubj}
                        </TableCell>
                        <TableCell className="w-[32%] max-w-0 text-xs text-muted-claude whitespace-normal overflow-hidden">
                          <span className="line-clamp-2 break-words font-medium text-ink leading-snug" title={cleanAttr}>
                            {cleanAttr}
                          </span>
                        </TableCell>
                        <TableCell className="w-[22%] max-w-0 text-xs whitespace-normal overflow-hidden">
                          <div className="space-y-0.5 max-w-full overflow-hidden">
                            <span
                              className={cn(
                                "text-xs text-ink block break-words",
                                formattedVal.isNumeric
                                  ? "font-bold font-mono truncate"
                                  : "font-medium line-clamp-2 leading-snug"
                              )}
                              title={formattedVal.primary}
                            >
                              {formattedVal.primary}
                            </span>
                            {formattedVal.secondary && (
                              <span
                                className="text-[10px] font-mono text-muted-claude truncate block"
                                title={formattedVal.secondary}
                              >
                                {formattedVal.secondary}
                              </span>
                            )}
                          </div>
                        </TableCell>
                        <TableCell className="w-[18%] max-w-0 text-xs whitespace-normal overflow-hidden">
                          {fact.context_envelope?.temporal_period ||
                          fact.context_envelope?.entity_scope ||
                          fact.context_envelope?.accounting_methodology ||
                          fact.context_envelope?.geography ? (
                            <div className="flex flex-wrap items-center gap-1 overflow-hidden">
                              {fact.context_envelope?.temporal_period && (
                                <Badge variant="secondary" className="text-[10px] px-1.5 py-0 truncate max-w-full">
                                  {fact.context_envelope.temporal_period}
                                </Badge>
                              )}
                              {fact.context_envelope?.entity_scope && (
                                <Badge variant="outline" className="text-[10px] px-1.5 py-0 uppercase font-mono truncate max-w-full">
                                  {fact.context_envelope.entity_scope}
                                </Badge>
                              )}
                              {fact.context_envelope?.accounting_methodology && (
                                <span className="text-[10px] text-muted-claude font-mono truncate max-w-full">
                                  {fact.context_envelope.accounting_methodology.replace("reported_", "").toUpperCase()}
                                </span>
                              )}
                              {fact.context_envelope?.geography && (
                                <span className="text-[10px] text-muted-claude truncate max-w-full">
                                  {fact.context_envelope.geography}
                                </span>
                              )}
                            </div>
                          ) : (
                            <span className="text-xs text-muted-claude/50 font-mono pl-1">—</span>
                          )}
                        </TableCell>
                        <TableCell className="w-[10%] text-right text-xs whitespace-nowrap">
                          <Badge variant="outline" className="text-[10px] font-mono">
                            p. {fact.evidence?.page_number || "—"}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    );
                })}
              </TableBody>
            </Table>
          </div>
        )}
      </div>

      {/* Pagination controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-1">
          <Button
            variant="outline"
            size="sm"
            className="h-8 text-xs gap-1"
            disabled={page === 0 || loading}
            onClick={() => setPage((p) => Math.max(0, p - 1))}
          >
            <ChevronLeft className="h-3.5 w-3.5" />
            <span>Previous</span>
          </Button>
          <span className="text-xs text-muted-foreground font-mono">
            Page {page + 1} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            className="h-8 text-xs gap-1"
            disabled={page >= totalPages - 1 || loading}
            onClick={() => setPage((p) => p + 1)}
          >
            <span>Next</span>
            <ChevronRight className="h-3.5 w-3.5" />
          </Button>
        </div>
      )}

      {/* Fact Detail Modal */}
      <FactDetailModal
        fact={selectedFact}
        open={detailOpen}
        onOpenChange={setDetailOpen}
      />
    </div>
  );
}
