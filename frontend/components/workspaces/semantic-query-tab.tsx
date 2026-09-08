"use client";

import { useState } from "react";
import { Search, Sparkles } from "lucide-react";
import { FactRead } from "@/lib/types";
import { listFacts } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FactDetailModal } from "./fact-detail-modal";

interface SemanticQueryTabProps {
  workspaceId: string;
}

export function SemanticQueryTab({ workspaceId }: SemanticQueryTabProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<FactRead[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasQueried, setHasQueried] = useState(false);
  const [selectedFact, setSelectedFact] = useState<FactRead | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);

  const sampleQueries = [
    "Revenue",
    "Spoton",
    "Shipment",
    "EBITDA",
    "Directors",
    "Subsidiary",
  ];

  const handleSearch = async (term: string) => {
    if (!term.trim()) return;
    setLoading(true);
    setHasQueried(true);
    try {
      const res = await listFacts(workspaceId, {
        attribute: term.trim(),
        limit: 20,
      });
      setResults(res.facts || []);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card className="border border-border/80 shadow-xs">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-semibold flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-foreground" />
            <span>Epistemic Fact Search & Knowledge Query</span>
          </CardTitle>
          <p className="text-xs text-muted-foreground">
            Query attributes, subjects, and financial metrics across all documents in this workspace.
          </p>
        </CardHeader>
        <CardContent className="space-y-3">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSearch(query);
            }}
            className="flex items-center gap-2"
          >
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
              <Input
                placeholder="Search across all facts (e.g. Revenue from Operations, Spoton Logistics)..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="pl-8 h-9 text-xs"
              />
            </div>
            <Button type="submit" size="sm" className="h-9 text-xs font-medium px-4" disabled={loading}>
              {loading ? "Searching..." : "Search"}
            </Button>
          </form>

          {/* Quick query chips */}
          <div className="flex flex-wrap items-center gap-1.5 pt-1">
            <span className="text-[11px] text-muted-foreground">Quick queries:</span>
            {sampleQueries.map((term) => (
              <Button
                key={term}
                variant="outline"
                size="sm"
                className="h-6 text-[11px] px-2 py-0"
                onClick={() => {
                  setQuery(term);
                  handleSearch(term);
                }}
              >
                {term}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      {hasQueried && (
        <div className="space-y-3">
          <div className="flex items-center justify-between px-1">
            <span className="text-xs font-semibold text-foreground">
              Search Results ({results.length} found)
            </span>
          </div>

          {results.length === 0 ? (
            <div className="p-10 text-center rounded-xl border border-dashed border-border/80 text-xs text-muted-foreground">
              No facts matched the search query. Try broader keywords like &apos;Revenue&apos; or &apos;FY24&apos;.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {results.map((fact) => (
                <div
                  key={fact.fact_id}
                  onClick={() => {
                    setSelectedFact(fact);
                    setDetailOpen(true);
                  }}
                  className="p-3.5 rounded-xl border border-border/80 bg-card hover:bg-muted/30 cursor-pointer transition-colors space-y-2"
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="font-semibold text-xs text-foreground line-clamp-1">
                      {fact.attribute}
                    </span>
                    <Badge variant="outline" className="text-[10px] font-mono shrink-0">
                      p. {fact.evidence?.page_number || "—"}
                    </Badge>
                  </div>

                  <div className="text-xs font-mono text-foreground font-semibold line-clamp-2">
                    {fact.value_raw}
                  </div>

                  <div className="flex flex-wrap items-center gap-1.5 text-[10px]">
                    {fact.context_envelope?.temporal_period && (
                      <Badge variant="secondary" className="px-1.5 py-0">
                        {fact.context_envelope.temporal_period}
                      </Badge>
                    )}
                    {fact.context_envelope?.entity_scope && (
                      <Badge variant="outline" className="px-1.5 py-0 uppercase">
                        {fact.context_envelope.entity_scope}
                      </Badge>
                    )}
                    <span className="text-muted-foreground ml-auto">
                      Subject: {fact.subject}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <FactDetailModal
        fact={selectedFact}
        open={detailOpen}
        onOpenChange={setDetailOpen}
      />
    </div>
  );
}
