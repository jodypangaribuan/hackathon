import type { Metadata } from "next";
import AnalyzerClient from "@/components/AnalyzerClient";
export const metadata: Metadata = {
  title: "Analyzer Sandbox — SIPATURE",
  description: "Demo leksikal terpisah dari batch A9.",
};
export default function AnalyzerPage() {
  return (
    <div className="space-y-4">
      <section>
        <h1 className="text-[22px] font-semibold tracking-tight">
          Analyzer Sandbox
        </h1>
        <p className="mt-1 max-w-3xl text-[13px] leading-relaxed text-ink-2">
          A9 preliminary adalah batch inference, bukan endpoint model real-time.
          Sandbox ini dipertahankan mengikuti blueprint UI untuk
          mendemonstrasikan taxonomy, dengan label metode yang eksplisit.
        </p>
      </section>
      <AnalyzerClient />
    </div>
  );
}
