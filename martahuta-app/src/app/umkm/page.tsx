/**
 * Layar 3 — Peluang UMKM.
 * Peluang usaha diturunkan dari keluhan nyata pada ulasan, bukan survei pasar.
 */
import type { Metadata } from "next";
import OpportunityList from "@/components/OpportunityList";
import { Note } from "@/components/ui";
import { opportunities } from "@/lib/data";
import { num } from "@/lib/format";

export const metadata: Metadata = {
  title: "Peluang UMKM — MARTAHUTA",
  description:
    "Peluang usaha di kawasan Danau Toba yang diturunkan dari keluhan nyata wisatawan.",
};

export default function UmkmPage() {
  const kabupatenList = Array.from(
    new Set(opportunities.map((o) => o.kabupaten)),
  ).sort();

  return (
    <div className="space-y-4">
      <section>
        <h1 className="text-[22px] font-semibold tracking-tight">Peluang UMKM</h1>
        <p className="mt-1 max-w-3xl text-[13px] leading-relaxed text-ink-2">
          Setiap keluhan berulang adalah permintaan pasar yang belum dilayani.
          {" "}{num(opportunities.length)} peluang di bawah diturunkan langsung dari
          pola keluhan pada ulasan — setiap kartu membawa bukti kutipannya
          sendiri.
        </p>
      </section>

      <OpportunityList
        opportunities={opportunities}
        kabupatenList={kabupatenList}
      />

      <Note>
        Perkiraan modal adalah rentang kasar untuk diskusi awal, bukan studi
        kelayakan. Proksi pasar dihitung dari volume ulasan dan kunjungan
        kabupaten — validasi lapangan tetap diperlukan sebelum berinvestasi.
      </Note>
    </div>
  );
}
