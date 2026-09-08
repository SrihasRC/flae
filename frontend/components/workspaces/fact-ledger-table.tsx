"use client";

import { useEffect, useState } from "react";
import { Search, ChevronLeft, ChevronRight, Filter } from "lucide-react";
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
import { FactDetailModal } from "./fact-detail-modal";

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
      subject: activeSearch.trim() || undefined,
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

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="space-y-4">
      {/* Top filter toolbar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 bg-card p-3 rounded-xl border border-border/70">
        <form onSubmit={handleSearchSubmit} className="flex-1 flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
            <Input
              placeholder="Search by subject or attribute (e.g. Revenue, Shipment)..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="pl-8 h-8 text-xs w-full"
            />
          </div>
          <Button type="submit" size="sm" variant="secondary" className="h-8 text-xs font-medium px-3">
            Search
          </Button>
        </form>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Filter className="h-3.5 w-3.5" />
            <span className="hidden md:inline">Document:</span>
          </div>
          <select
            value={selectedDocId}
            onChange={(e) => {
              setSelectedDocId(e.target.value);
              setPage(0);
            }}
            className="h-8 text-xs rounded-md border border-input bg-background px-2.5 py-1 text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          >
            <option value="">All Documents</option>
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
          <span className="text-xs font-medium text-foreground">Atomic Fact Ledger</span>
          <Badge variant="outline" className="text-[10px] font-mono">
            {total.toLocaleString()} facts
          </Badge>
        </div>
        <span className="text-[11px] text-muted-foreground">
          Showing {total === 0 ? 0 : page * limit + 1}–{Math.min((page + 1) * limit, total)} of {total}
        </span>
      </div>

      {/* Table container */}
      <div className="rounded-xl border border-border/80 bg-card overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-xs text-muted-foreground">
            Loading facts from ledger...
          </div>
        ) : error ? (
          <div className="p-8 text-center text-xs text-destructive">
            {error}
          </div>
        ) : facts.length === 0 ? (
          <div className="p-12 text-center text-xs text-muted-foreground">
            No facts found matching query or document filter.
          </div>
        ) : (
          <Table>
            <TableHeader className="bg-muted/40 text-muted-foreground">
              <TableRow className="hover:bg-transparent">
                <TableHead className="w-[180px] text-xs font-semibold">Subject</TableHead>
                <TableHead className="w-[220px] text-xs font-semibold">Attribute</TableHead>
                <TableHead className="w-[160px] text-xs font-semibold">Value</TableHead>
                <TableHead className="text-xs font-semibold">Context Envelope</TableHead>
                <TableHead className="w-[100px] text-xs font-semibold text-right">Evidence</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {facts.map((fact) => (
                <TableRow
                  key={fact.fact_id}
                  className="cursor-pointer hover:bg-muted/50 transition-colors"
                  onClick={() => {
                    setSelectedFact(fact);
                    setDetailOpen(true);
                  }}
                >
                  <TableCell className="font-medium text-xs text-foreground">
                    {fact.subject}
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground font-mono">
                    <span className="line-clamp-2" title={fact.attribute}>
                      {fact.attribute}
                    </span>
                  </TableCell>
                  <TableCell className="text-xs font-mono font-medium text-foreground">
                    <span className="line-clamp-2" title={fact.value_raw}>
                      {fact.value_raw}
                    </span>
                  </TableCell>
                  <TableCell className="text-xs">
                    <div className="flex flex-wrap items-center gap-1">
                      {fact.context_envelope?.temporal_period && (
                        <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
                          {fact.context_envelope.temporal_period}
                        </Badge>
                      )}
                      {fact.context_envelope?.entity_scope && (
                        <Badge variant="outline" className="text-[10px] px-1.5 py-0 uppercase">
                          {fact.context_envelope.entity_scope}
                        </Badge>
                      )}
                      {fact.context_envelope?.accounting_methodology && (
                        <span className="text-[10px] text-muted-foreground font-mono">
                          {fact.context_envelope.accounting_methodology.replace("reported_", "")}
                        </span>
                      )}
                    </div>
                  </TableCell>
                  <TableCell className="text-right text-xs">
                    <Badge variant="outline" className="text-[10px] font-mono">
                      p. {fact.evidence?.page_number || "—"}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
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
