import type { Metadata } from "next";
import OpportunityList from "@/components/OpportunityList";
import { getInterventions } from "@/lib/data";
import { num } from "@/lib/format";

export const metadata: Metadata = {
  title: "Rekomendasi Tindakan & Fasilitas — SIPATURE",
  description: "Katalog rekomendasi intervensi operasional pariwisata Toba.",
};

export const dynamic = "force-dynamic";

export default async function CandidatePage() {
  const interventions = await getInterventions();
  const kabupatenList = Array.from(
    new Set(interventions.map((item) => item.kabupaten)),
  ).sort();

  return (
    <div className="space-y-5">
      <section>
        <h1 className="text-[22px] font-semibold tracking-tight">
          Rekomendasi Tindakan &amp; Fasilitas
        </h1>
        <p className="mt-1 max-w-3xl text-[13px] leading-relaxed text-ink-2">
          Katalog <strong>{num(interventions.length)}</strong> rekomendasi intervensi fisik dan tata kelola yang diturunkan dari isu terverifikasi bukti ulasan. Setiap usulan dipetakan ke 4 pilar operasional untuk mempermudah perencanaan aksi lapangan dan alokasi anggaran BPODT.
        </p>
      </section>
      <OpportunityList
        interventions={interventions}
        kabupatenList={kabupatenList}
      />
    </div>
  );
}
