import type { Metadata } from "next";
import SimulatorExplorer from "@/components/SimulatorExplorer";
import { getRankedPlaces } from "@/lib/data";

export const metadata: Metadata = { title: "Simulator Intervensi — SIPATURE" };
export const dynamic = "force-dynamic";

export default async function SimulatorPage() {
  const rankedPlaces = await getRankedPlaces();
  const candidates = rankedPlaces
    .filter((place) => place.topAspects.length > 0)
    .slice(0, 80);
  return (
    <div className="space-y-5">
      <section>
        <h1 className="text-[22px] font-semibold tracking-tight">
          Simulator Intervensi
        </h1>
        <p className="mt-1 max-w-3xl text-[13px] leading-relaxed text-ink-2">
          Uji skenario penanganan keluhan per destinasi. Hasil adalah batas atas
          berbasis asumsi, bukan jaminan dampak atau prediksi kausal.
        </p>
      </section>
      <SimulatorExplorer places={candidates} />
    </div>
  );
}
