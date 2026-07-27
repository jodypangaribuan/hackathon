/**
 * Layar 1 — Peta Friksi (halaman utama).
 * Server component: memuat data di server, mengirim versi RAMPING ke client.
 */
import type { Metadata } from "next";
import FrictionExplorer, { type MapPlace } from "@/components/FrictionExplorer";
import { headlineStats, kabupatenList, places } from "@/lib/data";
import { num } from "@/lib/format";
import { StatTile } from "@/components/ui";

export const metadata: Metadata = {
  title: "Regional Overview — SIPATURE",
  description:
    "320 tempat di kawasan Danau Toba, diwarnai menurut tingkat friksi wisatawan.",
};

export default function HomePage() {
  const stats = headlineStats();

  const mapPlaces: MapPlace[] = places.map((p) => ({
    id: p.id,
    name: p.name,
    kind: p.kind,
    lat: p.lat,
    lon: p.lon,
    kabupaten: p.kabupaten,
    frictionScore: p.frictionScore,
    confidence: p.confidence,
    topAspects: p.topAspects,
    nReviewsText: p.nReviewsText,
    rank: p.rank,
  }));

  return (
    <div className="space-y-5">
      <section>
        <h1 className="text-[22px] font-semibold tracking-tight">
          Masalah destinasi mana yang harus diverifikasi lebih dulu?
        </h1>
        <p className="mt-1 max-w-3xl text-[13px] leading-relaxed text-ink-2">
          SIPATURE mengubah {num(stats.reviews)} ulasan menjadi sinyal peringatan dini
          yang dapat dijelaskan dan antrean intervensi bagi pengelola destinasi, BPODT,
          dan pemerintah daerah.
        </p>
      </section>

      <section className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatTile
          value={stats.duration !== null ? String(stats.duration).replace(".", ",") : "–"}
          label="Regional tourism health proxy"
          sub="Indikator konteks durasi kunjungan dari dataset panitia; bukan pengukuran kausal."
        />
        <StatTile
          value={num(stats.visits)}
          label="Eksposur kunjungan tahunan"
          sub="Digunakan sebagai konteks prioritas, bukan satu-satunya penentu."
        />
        <StatTile
          value={num(stats.reviewsWithText)}
          label="Ulasan berteks dianalisis"
          sub={`Dari ${num(stats.reviews)} ulasan · ${num(stats.placesGeocoded)} tempat berkoordinat.`}
        />
        <StatTile
          value={num(stats.ranked)}
          label="Destinasi dalam antrean prioritas"
          sub={`${num(stats.noData)} tempat tanpa ulasan ditampilkan sebagai prioritas survei lapangan.`}
        />
      </section>

      <FrictionExplorer places={mapPlaces} kabupatenList={kabupatenList} />
    </div>
  );
}
