import type { Metadata } from "next";
import AnalyzerClient from "@/components/AnalyzerClient";
export const metadata: Metadata = {
  title: "Analisis Review — SIPATURE",
  description: "Analisis aspek dan sentimen untuk satu review pariwisata.",
};
export default function AnalyzerPage() {
  return (
    <div className="space-y-4">
      <section>
        <h1 className="text-[22px] font-semibold tracking-tight">
          Analisis Review
        </h1>
        <p className="mt-1 max-w-3xl text-[13px] leading-relaxed text-ink-2">
          Tempel satu review untuk melihat aspek dan sentimen yang terdeteksi.
          Antarmuka ini telah disiapkan untuk model final; selama finalisasi,
          hasil masih diberi label baseline secara eksplisit.
        </p>
      </section>
      <AnalyzerClient />
    </div>
  );
}
