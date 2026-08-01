import type { Metadata } from "next";
import OpportunityList from "@/components/OpportunityList";
import { interventions } from "@/lib/data";
import { num } from "@/lib/format";
export const metadata: Metadata = {
  title: "Kandidat Intervensi — SIPATURE",
  description: "Kandidat tindakan dari reported issues A9.",
};
export default function CandidatePage() {
  const kabupatenList = Array.from(
    new Set(interventions.map((item) => item.kabupaten)),
  ).sort();
  return (
    <div className="space-y-4">
      <section>
        <h1 className="text-[22px] font-semibold tracking-tight">
          Kandidat Intervensi
        </h1>
        <p className="mt-1 max-w-3xl text-[13px] leading-relaxed text-ink-2">
          {num(interventions.length)} kandidat tindakan diturunkan dari isu
          evidence-gated A9. Halaman blueprint “Peluang UMKM” diselaraskan
          karena preliminary belum menghasilkan studi pasar atau kelayakan
          investasi.
        </p>
      </section>
      <OpportunityList
        interventions={interventions}
        kabupatenList={kabupatenList}
      />
    </div>
  );
}
