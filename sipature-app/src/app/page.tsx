import type { Metadata } from "next";
import FrictionExplorer, { type MapPlace } from "@/components/FrictionExplorer";
import {
  corpus,
  headlineStats,
  kabupatenList,
  mappablePlaces,
} from "@/lib/data";
import { dateTime, num } from "@/lib/format";
import { StatTile } from "@/components/ui";
export const metadata: Metadata = {
  title: "Regional Overview — SIPATURE",
  description: "Sinyal prioritas SIPATURE untuk destinasi kawasan Danau Toba.",
};
export default function HomePage() {
  const stats = headlineStats();
  const mapPlaces: MapPlace[] = mappablePlaces.map((place) => ({
    id: place.id,
    name: place.name,
    kind: place.kind,
    lat: place.lat,
    lon: place.lon,
    kabupaten: place.kabupaten,
    priority: place.priority,
    priorityScore: place.priorityScore,
    dataConfidence: place.dataConfidence,
    topAspects: place.topAspects,
    textReviewCount: place.textReviewCount,
    allReviewCount: place.allReviewCount,
    rank: place.rank,
  }));
  return (
    <div className="space-y-5">
      <section>
        <h1 className="text-[22px] font-semibold tracking-tight">
          Masalah destinasi mana yang harus diverifikasi lebih dulu?
        </h1>
        <p className="mt-1 max-w-3xl text-[13px] leading-relaxed text-ink-2">
          SIPATURE mengubah {num(stats.reviews)} review bersih menjadi
          early-warning signal dan antrean verifikasi yang dapat dijelaskan.
        </p>
        <p className="mt-1 text-[11px] text-muted">
          Model {corpus.modelVersion} · generated {dateTime(corpus.generatedAt)}
        </p>
      </section>
      <section className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatTile
          value={num(stats.reviewsWithText)}
          label="Review berteks dianalisis"
          sub={`${num(corpus.reviewsWithPredictions)} review memiliki prediksi aspek.`}
        />
        <StatTile
          value={num(corpus.aspectPredictions)}
          label="Prediksi aspek"
          sub={`${num(corpus.destinationsWithSignals)} destinasi memiliki sinyal.`}
        />
        <StatTile
          value={num(stats.ranked)}
          label="Destinasi actionable"
          sub={`${num(stats.actionableIssues)} isu lolos evidence gate.`}
        />
        <StatTile
          value={num(stats.placesGeocoded)}
          label="Destinasi berkoordinat"
          sub={`${num(stats.canonicalPlaces)} canonical destination · ${num(stats.noData)} lokasi unresolved.`}
        />
      </section>
      <FrictionExplorer places={mapPlaces} kabupatenList={kabupatenList} />
    </div>
  );
}
