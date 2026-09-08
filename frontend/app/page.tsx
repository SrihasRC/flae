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
      <section className="relative overflow-hidden pt-12 pb-20 md:pt-8 md:pb-32">
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
            <span className="underline decoration-border decoration-wavy underline-offset-8">
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
          <div className="mt-16 w-full grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6 border-y border-border/70 py-8">
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
          </div>
        </div>
      </section>

      {/* Feature & Architecture Pillars Section */}
      <section id="architecture" className="py-16 md:py-24 bg-canvas border-t border-hairline">
        <div className="container mx-auto max-w-5xl px-4 sm:px-6">
          <div className="flex flex-col items-center text-center mb-12">
            <Badge variant="pill" className="text-xs font-mono mb-3">
              Core Capabilities
            </Badge>
            <h2 className="text-3xl sm:text-4xl font-serif font-bold tracking-tight text-ink">
              Engineered for Auditability, Traceability &amp; Rigor
            </h2>
            <p className="mt-3 text-sm text-muted-claude max-w-2xl leading-relaxed">
              Generic LLM summarizers hallucinate when corporate reports disagree. FLAE enforces
              strict epistemic bounds before comparing claims.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Card 1: Fact Extraction */}
            <Card variant="cream" className="p-6 space-y-2.5">
              <div className="h-8 w-8 rounded-lg bg-surface-soft border border-hairline flex items-center justify-center mb-1">
                <FileText className="h-4 w-4 text-coral" />
              </div>
              <h3 className="text-base font-semibold text-ink">Atomic Fact Ledger</h3>
              <p className="text-xs text-muted-claude leading-relaxed">
                Decomposes complex corporate disclosures into discrete, typed claims with numerical
                normalization, raw strings, units, and verbatim paragraph excerpts.
              </p>
            </Card>

            {/* Card 2: Context Envelope */}
            <Card variant="cream" className="p-6 space-y-2.5">
              <div className="h-8 w-8 rounded-lg bg-surface-soft border border-hairline flex items-center justify-center mb-1">
                <Sparkles className="h-4 w-4 text-coral" />
              </div>
              <h3 className="text-base font-semibold text-ink">6-D Context Envelopes</h3>
              <p className="text-xs text-muted-claude leading-relaxed">
                Prevents false conflicts by explicitly binding claims to temporal periods, statutory
                accounting rules, and organizational scope (Standalone vs Consolidated).
              </p>
            </Card>

            {/* Card 3: Arbitration Engine */}
            <Card variant="cream" className="p-6 space-y-2.5">
              <div className="h-8 w-8 rounded-lg bg-surface-soft border border-hairline flex items-center justify-center mb-1">
                <Scale className="h-4 w-4 text-coral" />
              </div>
              <h3 className="text-base font-semibold text-ink">Epistemic Arbiter</h3>
              <p className="text-xs text-muted-claude leading-relaxed">
                Pairwise semantic matching classifies claims into Corroborated, Contradicted, or
                Reconciled with comprehensive step-by-step reasoning traces.
              </p>
            </Card>
          </div>

          <div className="mt-10 text-center">
            <Link
              href="/docs"
              className={cn(
                buttonVariants({ variant: "outline", size: "sm" }),
                "text-xs font-medium px-4 gap-1.5"
              )}
            >
              <span>Explore Complete Architecture &amp; System Docs</span>
              <ArrowRight className="h-3 w-3" />
            </Link>
          </div>
        </div>
      </section>

      {/* Epistemic Showcase Section */}
      <section id="cases" className="py-16 md:py-24 border-t border-hairline bg-surface-soft/50">
        <div className="container mx-auto max-w-5xl px-4 sm:px-6">
          <div className="flex flex-col items-center text-center mb-12">
            <Badge variant="pill" className="text-xs font-mono mb-3">
              Case Study Explorer
            </Badge>
            <h2 className="text-3xl sm:text-4xl font-serif font-bold tracking-tight text-ink">
              Demonstrated on Delhivery Limited Filings
            </h2>
            <p className="mt-3 text-sm text-muted-claude max-w-2xl leading-relaxed">
              Inspect how the engine processes real-world filings including the FY24 Annual Report
              and Q4 FY24 Earnings Presentation.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card variant="canvas" className="p-6 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-sm text-ink">
                  Case 1 &amp; 2: Corroboration &amp; Contradiction
                </span>
                <Badge variant="teal" className="text-[10px] font-mono">
                  Verified
                </Badge>
              </div>
              <p className="text-xs text-muted-claude leading-relaxed">
                Identifies claims that corroborate identically across filings (e.g. shipment volume,
                network scale) and surfaces genuine contradictions (e.g. board member counts or
                conflicting revisions) with juxtaposed quote excerpts.
              </p>
            </Card>

            <Card variant="canvas" className="p-6 space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-sm text-ink">
                  Case 3: Epistemic Reconciliation
                </span>
                <Badge variant="amber" className="text-[10px] font-mono">
                  Context Aware
                </Badge>
              </div>
              <p className="text-xs text-muted-claude leading-relaxed">
                Resolves apparent discrepancies such as Standalone Revenue (₹74,540 M) versus
                Consolidated Revenue (₹81,415 M) by demonstrating that organizational boundary divergence
                explains the mathematical delta.
              </p>
            </Card>
          </div>

          <div className="mt-12 flex items-center justify-center gap-3">
            <Link
              href="/cases"
              className={cn(
                buttonVariants({ variant: "outline", size: "sm" }),
                "text-xs font-medium px-4"
              )}
            >
              Read Detailed Case Studies
            </Link>
            <Link
              href="/workspaces/b097fafc-4e75-442d-8065-b4cee73091b9?tab=arbitration"
              className={cn(
                buttonVariants({ variant: "coral", size: "sm" }),
                "text-xs font-medium px-4"
              )}
            >
              Open Delhivery Live Console
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-hairline py-8 text-center text-xs text-muted-claude bg-canvas">
        <div className="container mx-auto max-w-5xl px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <span className="font-serif font-semibold text-sm text-ink">
            FLAE — Epistemic Truth Discovery &amp; Fact Arbitration
          </span>
          <span className="font-mono text-[11px] text-muted-soft">
            Enterprise Dossier Protocol • Deterministic Audit Engine
          </span>
        </div>
      </footer>
    </div>
  );
}
