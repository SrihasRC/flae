import Link from "next/link";
import { ArrowRight, FileText, Sparkles, Scale } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 md:pt-20 md:pb-32">
        {/* Subtle background glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-foreground/[0.02] dark:bg-foreground/[0.04] blur-3xl rounded-full pointer-events-none -z-10" />

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
      <section id="architecture" className="py-16 md:py-24 bg-muted/20 border-t border-border/60">
        <div className="container mx-auto max-w-5xl px-4 sm:px-6">
          <div className="flex flex-col items-center text-center mb-12">
            <Badge variant="outline" className="text-xs font-mono mb-3">
              Core Capabilities
            </Badge>
            <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
              Engineered for Auditability, Traceability & Rigor
            </h2>
            <p className="mt-2 text-sm text-muted-foreground max-w-2xl">
              Generic LLM summarizers hallucinate when corporate reports disagree. Our engine enforces
              epistemic bounds before comparing claims.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Card 1: Fact Extraction */}
            <Card className="border border-border/80 shadow-xs">
              <CardHeader className="pb-3">
                <div className="h-8 w-8 rounded-lg bg-secondary flex items-center justify-center mb-2">
                  <FileText className="h-4 w-4 text-foreground" />
                </div>
                <CardTitle className="text-base font-semibold">Atomic Fact Ledger</CardTitle>
                <CardDescription className="text-xs">
                  Immutable claims anchored to exact page citations.
                </CardDescription>
              </CardHeader>
              <CardContent className="text-xs text-muted-foreground leading-relaxed">
                Decomposes PDF filings into discrete, typed claims with numerical normalization, raw
                strings, units, and verbatim paragraph excerpts for tamper-evident review.
              </CardContent>
            </Card>

            {/* Card 2: Context Envelope */}
            <Card className="border border-border/80 shadow-xs">
              <CardHeader className="pb-3">
                <div className="h-8 w-8 rounded-lg bg-secondary flex items-center justify-center mb-2">
                  <Sparkles className="h-4 w-4 text-foreground" />
                </div>
                <CardTitle className="text-base font-semibold">6-D Context Envelopes</CardTitle>
                <CardDescription className="text-xs">
                  Temporal, organizational, and accounting boundaries.
                </CardDescription>
              </CardHeader>
              <CardContent className="text-xs text-muted-foreground leading-relaxed">
                Prevents false conflicts by tagging temporal period (FY24 vs Q4), accounting rules
                (Ind-AS reported vs pro-forma), and entity scope (Standalone vs Consolidated).
              </CardContent>
            </Card>

            {/* Card 3: Arbitration Engine */}
            <Card className="border border-border/80 shadow-xs">
              <CardHeader className="pb-3">
                <div className="h-8 w-8 rounded-lg bg-secondary flex items-center justify-center mb-2">
                  <Scale className="h-4 w-4 text-foreground" />
                </div>
                <CardTitle className="text-base font-semibold">Epistemic Arbiter</CardTitle>
                <CardDescription className="text-xs">
                  Automated pairwise contradiction resolution.
                </CardDescription>
              </CardHeader>
              <CardContent className="text-xs text-muted-foreground leading-relaxed">
                Cross-document matching classifies pairs into Corroborated, Contradicted, or
                Reconciled with comprehensive step-by-step reasoning traces and confidence metrics.
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Epistemic Showcase Section */}
      <section id="cases" className="py-16 md:py-24 border-t border-border/60">
        <div className="container mx-auto max-w-5xl px-4 sm:px-6">
          <div className="flex flex-col items-center text-center mb-12">
            <Badge variant="outline" className="text-xs font-mono mb-3">
              Case Study Explorer
            </Badge>
            <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
              Demonstrated on Delhivery Limited Filings
            </h2>
            <p className="mt-2 text-sm text-muted-foreground max-w-2xl">
              Inspect how the engine processes real-world filings including the FY24 Annual Report
              and Q4 FY24 Earnings Presentation.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-5 rounded-xl border border-border/80 bg-card">
              <div className="flex items-center justify-between mb-3">
                <span className="font-semibold text-sm">Case 1 & 2: Corroboration & Contradiction</span>
                <Badge variant="secondary" className="text-[10px] font-mono">
                  Direct Verification
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Identifies claims that corroborate identically across filings (e.g. shipment volume,
                network scale) and surfaces genuine contradictions (e.g. board member counts or
                conflicting revisions) with juxtaposed quote excerpts.
              </p>
            </div>

            <div className="p-5 rounded-xl border border-border/80 bg-card">
              <div className="flex items-center justify-between mb-3">
                <span className="font-semibold text-sm">Case 3: Epistemic Reconciliation</span>
                <Badge variant="secondary" className="text-[10px] font-mono">
                  Context Aware
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Resolves apparent discrepancies such as Standalone Revenue (₹74,540 M) versus
                Consolidated Revenue (₹81,415 M) by demonstrating that organizational boundary divergence
                explains the mathematical delta.
              </p>
            </div>
          </div>

          <div className="mt-12 text-center">
            <Link
              href="/workspaces/b097fafc-4e75-442d-8065-b4cee73091b9?tab=arbitration"
              className={cn(
                buttonVariants({ size: "lg" }),
                "h-10 px-6 text-xs font-medium inline-flex items-center"
              )}
            >
              View Arbitration Showcase
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/60 py-8 text-center text-xs text-muted-foreground">
        <div className="container mx-auto max-w-5xl px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <span>FLAE — Epistemic Knowledge Discovery & Fact Arbitration</span>
          <span className="font-mono text-[11px]">Next.js 16 • FastAPI • ChromaDB</span>
        </div>
      </footer>
    </div>
  );
}
