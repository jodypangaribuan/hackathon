import type { Metadata } from "next";
import SimulatorExplorer from "@/components/SimulatorExplorer";
import { rankedPlaces } from "@/lib/data";
import { buildRankLadder } from "@/lib/simulate";

export const metadata: Metadata = { title: "Simulator Intervensi — SIPATURE" };

export default function SimulatorPage() {
  const candidates = rankedPlaces.filter((place) => place.topAspects.length > 0).slice(0, 80);
  const ladder = buildRankLadder(rankedPlaces.map((place) => place.frictionScore));
  return (
    <div className="space-y-5">
      <section>
        <h1 className="text-[22px] font-semibold tracking-tight">Simulator Intervensi</h1>
        <p className="mt-1 max-w-3xl text-[13px] leading-relaxed text-ink-2">
          Uji skenario penanganan keluhan per destinasi. Hasil adalah batas atas berbasis asumsi,
          bukan jaminan dampak atau prediksi kausal.
        </p>
      </section>
      <SimulatorExplorer places={candidates} ladder={ladder} />
    </div>
  );
}
