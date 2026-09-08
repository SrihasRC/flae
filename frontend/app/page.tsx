import Link from "next/link";
import { ArrowRight, FileText, Sparkles, Scale } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import Grainient from "@/components/Grainient";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-28 pb-20 md:pt-42 md:pb-38">
        {/* Grainient background */}
        <div className="absolute inset-0 -z-10 pointer-events-none overflow-hidden opacity-60">
          <Grainient
            color1="#FAF9F5"
            color2="#CC785C"
            color3="#EFE9DE"
          />
        </div>

        <div className="container mx-auto max-w-5xl px-4 sm:px-6 flex flex-col items-center text-center">
          {/* Main Headline */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-foreground max-w-4xl leading-[1.15]">
            Reconcile Conflicting Corporate Filings with{" "}
            <span className="underline decoration-primary/65 decoration-wavy underline-offset-8">
              Mathematical Precision
            </span>
          </h1>

          {/* Subheading */}
          <p className="mt-6 text-base sm:text-lg md:text-xl text-muted-foreground max-w-3xl leading-relaxed">
            Extract atomic, machine-verifiable facts with rigorous 6-dimensional context envelopes
            (temporal scope, Ind-AS accounting standard, standalone vs. consolidated). Adjudicate
            contradictions across annual reports, presentations, and prospectus filings with verifiable
            evidence citations.
          </p>

          {/* Action CTAs */}
          <div className="mt-8 flex flex-col sm:flex-row items-center gap-3 w-full sm:w-auto">
            <Link
              href="/workspaces"
              className={cn(
                buttonVariants({ size: "lg" }),
                "h-11 px-6 font-medium gap-2 w-full sm:w-auto"
              )}
            >
              <span>Open Workspaces</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          {/* Metrics Strip */}
          {/* <div className="mt-8 w-full grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6 border-y border-white/80 py-8">
            <div className="flex flex-col items-center">
              <span className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground font-mono">
                3,618+
              </span>
              <span className="text-xs text-muted-foreground mt-1">Extracted Facts</span>
            </div>
            <div className="flex flex-col items-center">
              <span className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground font-mono">
                100%
              </span>
              <span className="text-xs text-muted-foreground mt-1">Verbatim Citations</span>
            </div>
            <div className="flex flex-col items-center">
              <span className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground font-mono">
                6-D
              </span>
              <span className="text-xs text-muted-foreground mt-1">Context Enveloping</span>
            </div>
            <div className="flex flex-col items-center">
              <span className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground font-mono">
                3 Cases
              </span>
              <span className="text-xs text-muted-foreground mt-1">Automated Arbitration</span>
            </div>
          </div> */}
        </div>
      </section>

      {/* Paradigm Comparison Strip: Traditional RAG vs FLAE (AKBC) */}
      <section className="py-16 md:py-20 bg-canvas border-t border-hairline">
        <div className="container mx-auto max-w-5xl px-4 sm:px-6">
          <div className="flex flex-col items-center text-center mb-12">
            <Badge variant="pill" className="text-xs font-mono mb-3">
              Theoretical Foundation &amp; Architecture
            </Badge>
            <h2 className="text-3xl sm:text-4xl font-serif font-bold tracking-tight text-ink">
              Beyond Naive Chunk-and-Retrieve RAG
            </h2>
            <p className="mt-3 text-sm text-muted-claude max-w-2xl leading-relaxed">
              Standard RAG systems delay reasoning until query time, producing hallucinations when filings
              contain apparent contradictions. FLAE is built upon <strong>Automated Knowledge Base Construction (AKBC)</strong> and
              the <strong>Extended FEVER</strong> paradigm, resolving conflicts during ingestion.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Standard RAG Card */}
            <Card variant="canvas" className="p-6 border border-hairline/80 shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-semibold uppercase tracking-wider text-muted-claude">
                  Standard Chunk &amp; Retrieve RAG
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-sm bg-muted-soft text-muted">
                  Probabilistic
                </span>
              </div>
              <ul className="space-y-3 text-xs text-muted-claude leading-relaxed">
                <li className="flex items-start gap-2">
                  <span className="text-destructive font-mono text-sm leading-none">•</span>
                  <span><strong>Blind Text Chunks:</strong> Slices documents into arbitrary token windows without recognizing financial table structures or reporting perimeters.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-destructive font-mono text-sm leading-none">•</span>
                  <span><strong>Binary FEVER Failure:</strong> Classic NLI models treat Q1 vs FY or Standalone vs Consolidated numbers as irreconcilable refutations.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-destructive font-mono text-sm leading-none">•</span>
                  <span><strong>Zero Lineage Ledger:</strong> Outputs synthetic generated summaries with no permanent audit trail or immutable evidence verification.</span>
                </li>
              </ul>
            </Card>

            {/* FLAE Epistemic Ledger Card */}
            <Card variant="cream" className="p-6 border border-coral/30 shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-semibold uppercase tracking-wider text-coral">
                  FLAE Epistemic Fact Ledger (AKBC)
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-sm bg-coral/15 text-coral font-medium">
                  Deterministic
                </span>
              </div>
              <ul className="space-y-3 text-xs text-ink leading-relaxed">
                <li className="flex items-start gap-2">
                  <span className="text-accent-teal font-mono text-sm leading-none">✓</span>
                  <span><strong>Structured Ingestion Pipeline:</strong> Normalizes claims into atomic tuples <code>(Subject, Metric, Value, ContextEnvelope, Evidence)</code> at ingestion time.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-accent-teal font-mono text-sm leading-none">✓</span>
                  <span><strong>Extended FEVER Paradigm:</strong> 6-D context envelopes prevent false contradictions by accounting for temporal periods, accounting rules, and organizational scope.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-accent-teal font-mono text-sm leading-none">✓</span>
                  <span><strong>Data Fusion &amp; LLM-as-a-Judge:</strong> The Arbiter agent clusters candidate pairs via bi-encoder blocking and generates formal reasoning proofs.</span>
                </li>
              </ul>
            </Card>
          </div>
        </div>
      </section>

      {/* Core Architectural Pillars */}
      <section id="architecture" className="py-16 md:py-24 bg-surface-card/40 border-t border-hairline">
        <div className="container mx-auto max-w-5xl px-4 sm:px-6">
          <div className="flex flex-col items-center text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-serif font-bold tracking-tight text-ink">
              Engineered for Statutory Rigor &amp; Auditability
            </h2>
            <p className="mt-3 text-sm text-muted-claude max-w-2xl leading-relaxed">
              FLAE treats financial filings as observer-bound, timeline-bound knowledge claims rather than
              universal strings.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Pillar 1: Epistemic Knowledge Claim */}
            <Card variant="cream" className="p-6 space-y-2.5">
              <div className="h-8 w-8 rounded-sm bg-surface-soft border border-hairline flex items-center justify-center mb-1">
                <FileText className="h-4 w-4 text-coral" />
              </div>
              <h3 className="text-base font-semibold text-ink font-serif">1. Epistemic Knowledge</h3>
              <p className="text-xs text-muted-claude leading-relaxed">
                Handles the philosophy of <em>how we know what is true</em>. Instead of treating text as absolute
                facts, every claim is formally scoped to its observer, fiscal period, and reporting boundary.
              </p>
            </Card>

            {/* Pillar 2: Fact-Ledger */}
            <Card variant="cream" className="p-6 space-y-2.5">
              <div className="h-8 w-8 rounded-sm bg-surface-soft border border-hairline flex items-center justify-center mb-1">
                <Sparkles className="h-4 w-4 text-coral" />
              </div>
              <h3 className="text-base font-semibold text-ink font-serif">2. Fact-Ledger</h3>
              <p className="text-xs text-muted-claude leading-relaxed">
                A single, append-only, structured ledger that acts as the global source of truth. Every claim
                is permanently stamped with absolute provenance: Document ID, Page Number, and verbatim excerpt.
              </p>
            </Card>

            {/* Pillar 3: Arbiter Agent */}
            <Card variant="cream" className="p-6 space-y-2.5">
              <div className="h-8 w-8 rounded-sm bg-surface-soft border border-hairline flex items-center justify-center mb-1">
                <Scale className="h-4 w-4 text-coral" />
              </div>
              <h3 className="text-base font-semibold text-ink font-serif">3. The Arbiter Agent</h3>
              <p className="text-xs text-muted-claude leading-relaxed">
                A deterministic LLM-as-a-Judge role acting as judge, jury, and classifier. It performs multi-attribute
                data fusion, evaluating whether incoming claims corroborate, contradict, or reconcile.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* 4-Stage Ingestion Flow */}
      <section className="py-16 md:py-24 bg-canvas border-t border-hairline">
        <div className="container mx-auto max-w-5xl px-4 sm:px-6">
          <div className="flex flex-col items-center text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-serif font-bold tracking-tight text-ink">
              From Raw PDF to Verified Arbitration Graph
            </h2>
            <p className="mt-3 text-sm text-muted-claude max-w-2xl leading-relaxed">
              Every ingested document passes through four automated stages before entering the immutable audit ledger.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Step 1 */}
            <div className="p-4 rounded-sm border border-hairline bg-surface-card space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-coral">STAGE 01</span>
                <span className="text-[10px] font-mono text-muted-soft">PDF Ingestion</span>
              </div>
              <h4 className="font-semibold text-xs text-ink">Parser &amp; Coordinate Tracking</h4>
              <p className="text-[11px] text-muted-claude leading-relaxed">
                Extracts financial disclosures, structured balance sheets, and narrative footnotes with page-level bounding.
              </p>
            </div>

            {/* Step 2 */}
            <div className="p-4 rounded-sm border border-hairline bg-surface-card space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-coral">STAGE 02</span>
                <span className="text-[10px] font-mono text-muted-soft">Information Extraction</span>
              </div>
              <h4 className="font-semibold text-xs text-ink">Atomic Fact Schemas</h4>
              <p className="text-[11px] text-muted-claude leading-relaxed">
                Deconstructs text into canonical tuples with numerical values, units, and 6-D context envelopes.
              </p>
            </div>

            {/* Step 3 */}
            <div className="p-4 rounded-sm border border-hairline bg-surface-card space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-coral">STAGE 03</span>
                <span className="text-[10px] font-mono text-muted-soft">Record Linkage</span>
              </div>
              <h4 className="font-semibold text-xs text-ink">Candidate Clustering</h4>
              <p className="text-[11px] text-muted-claude leading-relaxed">
                Uses bi-encoder vector similarity in ChromaDB to block and cluster related claims, avoiding O(N²) scaling.
              </p>
            </div>

            {/* Step 4 */}
            <div className="p-4 rounded-sm border border-hairline bg-surface-card space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-coral">STAGE 04</span>
                <span className="text-[10px] font-mono text-muted-soft">LLM-as-a-Judge</span>
              </div>
              <h4 className="font-semibold text-xs text-ink">Epistemic Arbitration</h4>
              <p className="text-[11px] text-muted-claude leading-relaxed">
                The Arbiter adjudicates disputes, classifies relationships, and writes persistent step-by-step reasoning proofs.
              </p>
            </div>
          </div>

          <div className="mt-12 text-center">
            <Link
              href="/docs"
              className={cn(
                buttonVariants({ variant: "outline", size: "sm" }),
                "text-xs font-medium px-4 gap-1.5"
              )}
            >
              <span>View Full Academic Grounding &amp; Architecture Docs</span>
              <ArrowRight className="h-3 w-3" />
            </Link>
          </div>
        </div>
      </section>

      {/* Decision Matrix: 3 Epistemic Outcomes */}
      <section className="py-16 md:py-24 bg-surface-soft/40 border-t border-hairline">
        <div className="container mx-auto max-w-5xl px-4 sm:px-6">
          <div className="flex flex-col items-center text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-serif font-bold tracking-tight text-ink">
              The Three Epistemic Resolutions
            </h2>
            <p className="mt-3 text-sm text-muted-claude max-w-2xl leading-relaxed">
              How the Arbiter resolves pairwise claims across corporate filings.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Corroborated */}
            <Card variant="canvas" className="p-6 border border-hairline shadow-xs">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-sm text-ink font-serif">Corroborated</span>
              </div>
              <p className="text-xs text-muted-claude leading-relaxed">
                Claims state identical numbers and assertions under matching context scopes. Verified by dual verbatim citations across separate filings.
              </p>
            </Card>

            {/* Contradicted */}
            <Card variant="canvas" className="p-6 border border-hairline shadow-xs">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-sm text-ink font-serif">Contradicted</span>
              </div>
              <p className="text-xs text-muted-claude leading-relaxed">
                Claims describe the exact same entity, period, and accounting standard, but assert irreconcilably conflicting numbers or qualitative states.
              </p>
            </Card>

            {/* Reconciled */}
            <Card variant="canvas" className="p-6 border border-hairline shadow-xs">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-sm text-ink font-serif">Context Reconciled</span>
              </div>
              <p className="text-xs text-muted-claude leading-relaxed">
                Apparent discrepancies (e.g. ₹74,540M vs ₹81,415M) are proven mathematically valid once organizational boundary or temporal qualifier divergence is identified.
              </p>
            </Card>
          </div>

          <div className="mt-10 flex items-center justify-center gap-3">
            <Link
              href="/workspaces"
              className={cn(
                buttonVariants({ variant: "coral", size: "sm" }),
                "text-xs font-medium px-4 gap-1.5"
              )}
            >
              <span>Explore Active Workspaces</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Comprehensive Proper Footer */}
      <footer className="border-t border-hairline bg-surface-card/60 pt-12 pb-8 text-xs text-muted-claude">
        <div className="container mx-auto max-w-5xl px-4 sm:px-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 pb-10 border-b border-hairline/80">
            {/* Col 1: Brand & Overview */}
            <div className="space-y-3 md:col-span-1">
              <div className="flex items-center gap-2">
                <span className="font-serif font-bold text-base text-ink tracking-tight">
                  FLAE
                </span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded-xs bg-surface-soft border border-hairline text-muted-claude">
                  v1.0
                </span>
              </div>
              <p className="text-xs text-muted-claude leading-relaxed">
                Fact Ledger &amp; Arbitration Engine. Automated Knowledge Base Construction and multi-document
                epistemic adjudication for regulatory disclosures.
              </p>
            </div>

            {/* Col 2: Product & System */}
            <div className="space-y-2.5">
              <h5 className="font-mono font-semibold text-[11px] text-ink uppercase tracking-wider">
                System
              </h5>
              <ul className="space-y-2 text-xs">
                <li>
                  <Link href="/workspaces" className="hover:text-ink transition-colors">
                    Workspaces Hub
                  </Link>
                </li>
                <li>
                  <Link href="/docs" className="hover:text-ink transition-colors">
                    Architecture &amp; Specifications
                  </Link>
                </li>
                <li>
                  <Link href="/workspaces/b097fafc-4e75-442d-8065-b4cee73091b9" className="hover:text-ink transition-colors">
                    Delhivery Test Dossier
                  </Link>
                </li>
              </ul>
            </div>

            {/* Col 3: Academic Foundations */}
            <div className="space-y-2.5">
              <h5 className="font-mono font-semibold text-[11px] text-ink uppercase tracking-wider">
                Paradigms
              </h5>
              <ul className="space-y-2 text-xs">
                <li>
                  <span className="text-muted-claude">Auto Knowledge Base (AKBC)</span>
                </li>
                <li>
                  <span className="text-muted-claude">Extended FEVER Framework</span>
                </li>
                <li>
                  <span className="text-muted-claude">Data Fusion &amp; Conflict Resolution</span>
                </li>
                <li>
                  <span className="text-muted-claude">LLM-as-a-Judge Arbitration</span>
                </li>
              </ul>
            </div>

            {/* Col 4: Audit & Lineage */}
            <div className="space-y-2.5">
              <h5 className="font-mono font-semibold text-[11px] text-ink uppercase tracking-wider">
                Audit Guarantees
              </h5>
              <ul className="space-y-2 text-xs">
                <li>
                  <span className="text-muted-claude">100% Verbatim Citation Lineage</span>
                </li>
                <li>
                  <span className="text-muted-claude">Immutable Event-Sourced Ledger</span>
                </li>
                <li>
                  <span className="text-muted-claude">6-D Context Envelope Scoping</span>
                </li>
                <li>
                  <a
                    href="https://github.com/SrihasRC/flae"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-coral hover:underline inline-flex items-center gap-1"
                  >
                    <span>GitHub</span>
                    <ArrowRight className="h-3 w-3" />
                  </a>
                </li>
              </ul>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="pt-6 flex flex-col sm:flex-row items-center justify-center gap-4 text-[11px] text-muted-soft">
            <span>
              FLAE - Fact Ledger &amp; Arbitration Engine
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
