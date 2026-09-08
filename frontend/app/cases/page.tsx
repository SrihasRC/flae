import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export const metadata = {
  title: "Case Studies & Arbitration Showcase — FLAE",
  description: "Exhibits demonstrating Corroboration, Contradiction, Reconciled organizational scope, and Extraction Failure Audits.",
};

export default function CasesPage() {
  return (
    <div className="flex flex-col min-h-screen bg-[#faf9f5]">
      {/* Editorial Header */}
      <section className="pt-12 pb-16 md:pt-16 md:pb-20 border-b border-[#e6dfd8]">
        <div className="container mx-auto max-w-5xl px-4 sm:px-6">
          <div className="flex flex-col items-start max-w-3xl">
            <Badge variant="pill" className="text-xs font-mono mb-3">
              Empirical Dossier Exhibits
            </Badge>
            <h1 className="text-4xl sm:text-5xl font-serif font-bold tracking-tight text-[#141413] leading-tight">
              Case 1–4 Arbitration Showcase
            </h1>
            <p className="mt-4 text-base sm:text-lg text-[#3d3d3a] leading-relaxed">
              Real-world filings from Delhivery Limited (FY24 Annual Report &amp; Q4 FY24 Earnings Presentation)
              demonstrating how FLAE classifies cross-document evidence with mathematical certainty.
            </p>
            <div className="mt-6 flex items-center gap-3">
              <Link
                href="/workspaces/b097fafc-4e75-442d-8065-b4cee73091b9?tab=arbitration"
                className={cn(
                  buttonVariants({ variant: "coral", size: "sm" }),
                  "text-xs font-medium px-4 gap-1.5"
                )}
              >
                <span>Open Delhivery Arbitration Console</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Case Exhibits */}
      <section className="py-16 md:py-20">
        <div className="container mx-auto max-w-5xl px-4 sm:px-6 space-y-12">
          {/* Case 1: Corroborated */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Badge variant="teal" className="text-[11px] font-mono uppercase">
                Case 1: Corroborated
              </Badge>
              <h2 className="text-xl sm:text-2xl font-serif font-semibold text-[#141413]">
                Direct Cross-Filing Verification
              </h2>
            </div>
            <p className="text-xs sm:text-sm text-[#6c6a64] leading-relaxed">
              When distinct statutory documents confirm identical claims, the engine establishes a high-confidence
              corroboration node with cross-document citation anchors.
            </p>

            <Card variant="cream" className="p-5 space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-[#141413]">
                  Express Parcel Shipment Volume (FY24)
                </span>
                <span className="font-mono text-[#6c6a64]">Confidence: 97%</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                <div className="p-3 rounded-lg bg-[#faf9f5] border border-[#e6dfd8] space-y-1">
                  <span className="text-[10px] font-semibold text-[#6c6a64] uppercase block">
                    Document 1 (Annual Report FY24) — Page 44
                  </span>
                  <p className="italic text-[#141413]">
                    &ldquo;Total express parcel volume for FY24 reached 740 million shipments across India.&rdquo;
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-[#faf9f5] border border-[#e6dfd8] space-y-1">
                  <span className="text-[10px] font-semibold text-[#6c6a64] uppercase block">
                    Document 2 (Q4 FY24 Investor Presentation) — Page 12
                  </span>
                  <p className="italic text-[#141413]">
                    &ldquo;Express parcel shipments stood at 740 million parcels for full year FY24.&rdquo;
                  </p>
                </div>
              </div>
              <div className="p-2.5 rounded bg-[#f5f0e8] text-[11px] text-[#3d3d3a] border border-[#e6dfd8]">
                <strong>Arbiter Verdict:</strong> Corroborated. Identical temporal period (FY24), entity scope
                (consolidated network), and volume metric (740 M parcels).
              </div>
            </Card>
          </div>

          {/* Case 2: Contradicted */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Badge variant="destructive" className="text-[11px] font-mono uppercase">
                Case 2: Contradicted
              </Badge>
              <h2 className="text-xl sm:text-2xl font-serif font-semibold text-[#141413]">
                Genuine Discrepancies &amp; Revisions
              </h2>
            </div>
            <p className="text-xs sm:text-sm text-[#6c6a64] leading-relaxed">
              When documents report conflicting figures under the exact same scope without statutory reconciliation,
              the engine flags a critical contradiction requiring audit resolution.
            </p>

            <Card variant="cream" className="p-5 space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-[#141413]">
                  Statutory Board Size &amp; Composition
                </span>
                <span className="font-mono text-[#c64545] font-semibold">Confidence: 94%</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                <div className="p-3 rounded-lg bg-[#faf9f5] border border-[#e6dfd8] space-y-1">
                  <span className="text-[10px] font-semibold text-[#6c6a64] uppercase block">
                    Document 1 — Corporate Governance Note
                  </span>
                  <p className="italic text-[#141413]">
                    &ldquo;The Board comprises 7 directors, of which 4 are independent directors.&rdquo;
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-[#faf9f5] border border-[#e6dfd8] space-y-1">
                  <span className="text-[10px] font-semibold text-[#6c6a64] uppercase block">
                    Document 2 — Shareholder Presentation
                  </span>
                  <p className="italic text-[#141413]">
                    &ldquo;Our leadership team is guided by a Board of 9 directors as of March 31, 2024.&rdquo;
                  </p>
                </div>
              </div>
              <div className="p-2.5 rounded bg-[#f5f0e8] text-[11px] text-[#3d3d3a] border border-[#e6dfd8]">
                <strong>Arbiter Verdict:</strong> Contradicted. Conflicting board headcounts (7 vs 9) cited for the same
                effective reporting date without an explanatory addendum.
              </div>
            </Card>
          </div>

          {/* Case 3: Reconciled */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Badge variant="amber" className="text-[11px] font-mono uppercase">
                Case 3: Reconciled
              </Badge>
              <h2 className="text-xl sm:text-2xl font-serif font-semibold text-[#141413]">
                Scope &amp; Methodology Divergence (Standalone vs. Consolidated)
              </h2>
            </div>
            <p className="text-xs sm:text-sm text-[#6c6a64] leading-relaxed">
              Apparent numerical discrepancies that confuse traditional LLMs are resolved mathematically through
              explicit contextual envelopes.
            </p>

            <Card variant="cream" className="p-5 space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-[#141413]">
                  Revenue from Operations (FY24)
                </span>
                <span className="font-mono text-[#e8a55a] font-semibold">Confidence: 98%</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                <div className="p-3 rounded-lg bg-[#faf9f5] border border-[#e6dfd8] space-y-1">
                  <span className="text-[10px] font-semibold text-[#6c6a64] uppercase block">
                    Document 1 (Standalone P&amp;L) — Page 44
                  </span>
                  <p className="italic text-[#141413]">
                    &ldquo;Revenue from operations on standalone basis for FY24 stood at ₹74,540.82 million.&rdquo;
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-[#faf9f5] border border-[#e6dfd8] space-y-1">
                  <span className="text-[10px] font-semibold text-[#6c6a64] uppercase block">
                    Document 2 (Consolidated P&amp;L) — Page 44
                  </span>
                  <p className="italic text-[#141413]">
                    &ldquo;Revenue from operations on consolidated basis for FY24 stood at ₹81,415.38 million.&rdquo;
                  </p>
                </div>
              </div>
              <div className="p-2.5 rounded bg-[#f5f0e8] text-[11px] text-[#3d3d3a] border border-[#e6dfd8]">
                <strong>Arbiter Verdict:</strong> Reconciled. Divergence Factor:{" "}
                <code className="text-[#cc785c] font-mono">entity_scope: standalone vs consolidated</code>. The delta is
                fully accounted for by operating subsidiaries (Spoton Logistics and foreign branches).
              </div>
            </Card>
          </div>

          {/* Case 4: Extraction & Ingestion Failures */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Badge variant="dark" className="text-[11px] font-mono uppercase">
                Case 4: Failure Auditing
              </Badge>
              <h2 className="text-xl sm:text-2xl font-serif font-semibold text-[#141413]">
                Strict Ingestion Failure Diagnostics
              </h2>
            </div>
            <p className="text-xs sm:text-sm text-[#6c6a64] leading-relaxed">
              In statutory compliance, failed extractions must never be discarded or hallucinated. FLAE captures
              table OCR faults and coordinate ambiguities directly in the immutable audit log.
            </p>

            <Card variant="dark" className="p-5 font-mono text-xs text-[#faf9f5] space-y-2">
              <div className="text-[11px] text-[#a09d96]">FailureAuditRecord.json</div>
              <pre className="text-[#faf9f5] text-[11px] leading-relaxed">
{`{
  "document_id": "b0f6d2f1-451e-461c-80b4-6170bee3543f",
  "status": "failed_extraction",
  "unparsed_region": "Page 19, Table 3.2 (Complex multi-merged cell header)",
  "diagnostic_reason": "Ambiguous header span: temporal qualifiers overlap across column boundaries",
  "action_taken": "Quarantined for human auditor review, omitted from downstream pairwise arbitration"
}`}
              </pre>
            </Card>
          </div>
        </div>
      </section>
    </div>
  );
}
