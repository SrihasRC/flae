import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export const metadata = {
  title: "Architecture & Documentation — FLAE",
  description: "Comprehensive system architecture, mathematical epistemic boundaries, and enterprise ledger specifications.",
};

export default function DocsPage() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Editorial Header */}
      <section className="pt-28 pb-16 md:pt-32 md:pb-20 border-b border-hairline bg-canvas">
        <div className="container mx-auto max-w-5xl px-4 sm:px-6">
          <div className="flex flex-col items-start max-w-3xl">
            <Badge variant="pill" className="text-xs font-mono mb-3">
              System Architecture &amp; Specifications
            </Badge>
            <h1 className="text-4xl sm:text-5xl font-serif font-bold tracking-tight text-ink leading-tight">
              Deterministic Truth Discovery Architecture
            </h1>
            <p className="mt-4 text-base sm:text-lg text-body leading-relaxed">
              FLAE replaces subjective probabilistic summaries with an immutable, typed Atomic Fact
              Ledger paired with a multi-document arbitration engine. Built for regulatory filings,
              statutory audits, and corporate financial dossiers.
            </p>
          </div>
        </div>
      </section>

      {/* Main Architecture Content */}
      <section className="py-16 md:py-20 bg-canvas">
        <div className="container mx-auto max-w-5xl px-4 sm:px-6 space-y-16">
          {/* Section 1: Pipeline Overview */}
          <div className="space-y-6">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-coral" />
              <h2 className="text-2xl sm:text-3xl font-serif font-semibold text-ink">
                1. Four-Stage Epistemic Pipeline
              </h2>
            </div>
            <p className="text-sm text-body max-w-3xl leading-relaxed">
              Every document uploaded to a workspace undergoes a strict 4-stage pipeline that
              enforces structural integrity before any claim is matched or arbitrated:
            </p>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card variant="cream" className="p-4 space-y-2">
                <span className="text-[11px] font-mono text-coral font-bold">STAGE 01</span>
                <h3 className="font-semibold text-sm text-ink">Document Parsing</h3>
                <p className="text-xs text-muted-claude leading-relaxed">
                  High-fidelity text and table segmentation preserves tabular structures, headers, and
                  page coordinate anchors.
                </p>
              </Card>

              <Card variant="cream" className="p-4 space-y-2">
                <span className="text-[11px] font-mono text-coral font-bold">STAGE 02</span>
                <h3 className="font-semibold text-sm text-ink">Fact Extraction</h3>
                <p className="text-xs text-muted-claude leading-relaxed">
                  Extracts atomic claims consisting of subject, attribute, numerical normalization,
                  verbatim quote, and context envelope.
                </p>
              </Card>

              <Card variant="cream" className="p-4 space-y-2">
                <span className="text-[11px] font-mono text-coral font-bold">STAGE 03</span>
                <h3 className="font-semibold text-sm text-ink">Vector Indexing</h3>
                <p className="text-xs text-muted-claude leading-relaxed">
                  Semantic embedding of attributes and subjects enables cross-filing similarity matching
                  with cosine distance thresholds.
                </p>
              </Card>

              <Card variant="cream" className="p-4 space-y-2">
                <span className="text-[11px] font-mono text-coral font-bold">STAGE 04</span>
                <h3 className="font-semibold text-sm text-ink">Cross Arbitration</h3>
                <p className="text-xs text-muted-claude leading-relaxed">
                  Pairwise evaluation across documents checks context bounds to classify claims as
                  Corroborated, Contradicted, or Reconciled.
                </p>
              </Card>
            </div>
          </div>

          {/* Section 2: Code Window / Payload Mockup (Dark Navy Surface per design doc) */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-coral" />
                <h2 className="text-2xl sm:text-3xl font-serif font-semibold text-ink">
                  2. 6-Dimensional Context Envelope Specification
                </h2>
              </div>
              <Badge variant="pill" className="text-[10px] font-mono">
                Schema: ContextEnvelope
              </Badge>
            </div>
            <p className="text-sm text-body max-w-3xl leading-relaxed">
              Standard AI summarizers falsely report contradictions when comparing figures that look
              comparable on the surface but differ in accounting methodology, organizational scope, or
              reporting period. FLAE resolves this by isolating each claim within six explicit
              dimensions:
            </p>

            {/* Dark Code Window Card */}
            <Card variant="dark" className="p-6 font-mono text-xs overflow-x-auto space-y-3">
              <div className="flex items-center justify-between border-b border-surface-dark-elevated pb-3 text-on-dark-soft">
                <span>ContextEnvelope.json</span>
                <span className="text-[11px]">Strict Typed Schema</span>
              </div>
              <pre className="text-canvas leading-relaxed text-[11px]">
{`{
  "temporal_period": "FY2023-24",            // e.g., FY24, Q4 FY24, 9M FY24
  "period_type": "duration",                 // duration | point_in_time
  "entity_scope": "consolidated",            // consolidated | standalone | subsidiary | cohort
  "geography": "India",                      // statutory operating geography
  "accounting_methodology": "reported_ind_as",// reported_ind_as | pro_forma | revised_estimate
  "additional_qualifiers": "Full year audited consolidated figures including Spoton Logistics"
}`}
              </pre>
            </Card>
          </div>

          {/* Section 3: Arbitration Classification Matrix */}
          <div className="space-y-6">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-coral" />
              <h2 className="text-2xl sm:text-3xl font-serif font-semibold text-ink">
                3. Arbitration Decision Matrix
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="p-5 rounded-xl border border-hairline bg-surface-card space-y-2">
                <Badge variant="teal" className="text-[10px] font-mono uppercase">
                  CORROBORATED
                </Badge>
                <h3 className="font-semibold text-sm text-ink">Identical Assertions</h3>
                <p className="text-xs text-muted-claude leading-relaxed">
                  Both filings assert mathematically and semantically compatible claims under the same
                  context envelope. Example: identical express parcel volume numbers across the annual
                  report and shareholder presentation.
                </p>
              </div>

              <div className="p-5 rounded-xl border border-hairline bg-surface-card space-y-2">
                <Badge variant="destructive" className="text-[10px] font-mono uppercase">
                  CONTRADICTED
                </Badge>
                <h3 className="font-semibold text-sm text-ink">Genuine Conflict</h3>
                <p className="text-xs text-muted-claude leading-relaxed">
                  Claims disagree under matching context envelopes without a valid statutory reconciliation.
                  Example: conflicting board of director counts or irreconcilable capital expenditure figures.
                </p>
              </div>

              <div className="p-5 rounded-xl border border-hairline bg-surface-card space-y-2">
                <Badge variant="amber" className="text-[10px] font-mono uppercase">
                  RECONCILED
                </Badge>
                <h3 className="font-semibold text-sm text-ink">Divergence Factor Identified</h3>
                <p className="text-xs text-muted-claude leading-relaxed">
                  Apparent numeric differences are fully explained by divergence in organizational scope
                  (Standalone ₹74,540 M vs Consolidated ₹81,415 M) or temporal granularity (FY vs Q4).
                </p>
              </div>
            </div>
          </div>

          {/* Section 4: Enterprise Audit Guarantee */}
          <div className="p-8 rounded-xl bg-coral text-white space-y-4">
            <h2 className="text-2xl sm:text-3xl font-serif font-semibold">
              100% Verbatim Auditability Guarantee
            </h2>
            <p className="text-xs sm:text-sm text-white/90 max-w-3xl leading-relaxed">
              Every atomic fact stored in FLAE requires an exact verbatim quotation, document
              UUID, and page number reference. Probabilistic hallucination is strictly prevented: if a
              claim cannot be tied to an explicit coordinate in the source PDF, the ingestion engine rejects
              the candidate claim into the Failure Audit trail.
            </p>
            <div className="pt-2">
              <Link
                href="/workspaces"
                className={cn(
                  buttonVariants({ variant: "secondary", size: "sm" }),
                  "text-xs font-semibold px-4 text-ink bg-canvas"
                )}
              >
                Explore Live Workspaces
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
