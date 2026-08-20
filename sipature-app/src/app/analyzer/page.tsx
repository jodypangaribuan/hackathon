import type { Metadata } from "next";
import AnalyzerClient from "@/components/AnalyzerClient";

export const metadata: Metadata = {
  title: "Analisis Ulasan — SIPATURE",
  description: "Ekstraksi aspek dan klasifikasi sentimen ulasan pariwisata Toba secara real-time.",
};

export default function AnalyzerPage() {
  return (
    <div className="space-y-4">
      <section>
        <h1 className="text-[22px] font-semibold tracking-tight">
          Analisis Ulasan Real-Time
        </h1>
        <p className="mt-1 max-w-3xl text-[13px] leading-relaxed text-ink-2">
          Uji teks ulasan wisatawan untuk mengekstraksi 14 aspek pariwisata dan arah sentimen secara instan menggunakan pipeline model inferensi produksi TF-IDF.
        </p>
      </section>
      <AnalyzerClient />
    </div>
  );
}
