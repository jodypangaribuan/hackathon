import type { Metadata } from "next";
import FrictionExplorer, { type MapPlace } from "@/components/FrictionExplorer";
import {
  getCorpus,
  getHeadlineStats,
  getKabupatenList,
  getMappablePlaces,
} from "@/lib/data";
import { num } from "@/lib/format";
import { StatTile } from "@/components/ui";

export const metadata: Metadata = {
  title: "Regional Overview — SIPATURE",
  description: "Sistem Pemantauan Kualitas dan Rekomendasi Tindak Lanjut Pariwisata Danau Toba.",
};

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const [corpus, stats, mappablePlaces, kabupatenList] = await Promise.all([
    getCorpus(),
    getHeadlineStats(),
    getMappablePlaces(),
    getKabupatenList(),
  ]);

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
    <div className="space-y-6">
      {/* Hero Section */}
      <section
        className="border-b pb-4"
        style={{ borderColor: "var(--hairline)" }}
      >
        <h1 className="text-[24px] font-semibold tracking-tight sm:text-[28px]">
          Masalah destinasi mana yang harus diperbaiki lebih dulu?
        </h1>
      </section>

      {/* Metric Tiles */}
      <section className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatTile
          value={num(stats.reviewsWithText)}
          label="Ulasan Wisatawan Dianalisis"
          sub="Ulasan nyata wisatawan Danau Toba"
        />
        <StatTile
          value={num(corpus.aspectPredictions)}
          label="Masalah/Topik Terpetakan"
          sub={`${num(corpus.destinationsWithSignals)} lokasi memiliki sinyal aktif`}
        />
        <StatTile
          value={num(stats.ranked)}
          label="Destinasi Perlu Perhatian"
          sub={`${num(stats.actionableIssues)} keluhan berulang siap ditindaklanjuti`}
        />
        <StatTile
          value={num(stats.placesGeocoded)}
          label="Lokasi Wisata Terdata"
          sub="Tersebar di 8 kabupaten lingkar Toba"
        />
      </section>

      {/* Main Interactive Map */}
      <FrictionExplorer places={mapPlaces} kabupatenList={kabupatenList} />
    </div>
  );
}
