/**
 * Layar 4 — Live Analyzer.
 * Server component tipis: mengambil contoh ulasan dari lexicon.json lalu
 * menyerahkan interaksi ke AnalyzerClient.
 */
import type { Metadata } from "next";
import AnalyzerClient from "@/components/AnalyzerClient";
import { lexicon } from "@/lib/data";

export const metadata: Metadata = {
  title: "Live Analyzer — MARTAHUTA",
  description:
    "Tempel ulasan apa pun, lihat ekstraksi aspek dan sentimen berjalan.",
};

export default function AnalyzerPage() {
  return (
    <div className="space-y-4">
      <section>
        <h1 className="text-[22px] font-semibold tracking-tight">Live Analyzer</h1>
        <p className="mt-1 max-w-3xl text-[13px] leading-relaxed text-ink-2">
          Satu-satunya bagian aplikasi yang menganalisis secara langsung. Tempel
          ulasan apa pun — atau klik contoh asli dari dataset — dan lihat aspek,
          sentimen, serta buktinya diekstrak seketika lewat{" "}
          <code className="text-[12px]">POST /api/analyze</code>.
        </p>
      </section>

      <AnalyzerClient samples={lexicon.samples} />
    </div>
  );
}
