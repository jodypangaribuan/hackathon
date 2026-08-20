import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, CheckCircle2, ShieldAlert, Sparkles } from "lucide-react";
import FrictionExplorer, { type MapPlace } from "@/components/FrictionExplorer";
import {
  getCorpus,
  getHeadlineStats,
  getKabupatenList,
  getMappablePlaces,
  getRankedPlaces,
} from "@/lib/data";
import { ASPECT_LABEL, dateTime, levelOfPlace, num, score } from "@/lib/format";
import { AspectIcon } from "@/components/AppIcon";
import { Card, LevelBadge, StatTile } from "@/components/ui";

export const metadata: Metadata = {
  title: "Regional Overview — SIPATURE",
  description: "Sistem Pemantauan Ulasan dan Prioritas Tindak Lanjut Pariwisata Toba.",
};

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const [corpus, stats, mappablePlaces, kabupatenList, rankedPlaces] =
    await Promise.all([
      getCorpus(),
      getHeadlineStats(),
      getMappablePlaces(),
      getKabupatenList(),
      getRankedPlaces(),
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

  const topUrgent = rankedPlaces.slice(0, 4);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <section className="flex flex-col justify-between gap-4 border-b pb-5 lg:flex-row lg:items-end" style={{ borderColor: "var(--hairline)" }}>
        <div>
          <div className="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-[11px] font-medium text-accent" style={{ borderColor: "var(--accent)", background: "rgba(235,108,54,0.06)" }}>
            <Sparkles size={12} />
            <span>SIPATURE Intelligence Engine</span>
          </div>
          <h1 className="mt-2 text-[24px] font-semibold tracking-tight sm:text-[28px]">
            Masalah destinasi mana yang harus diverifikasi lebih dulu?
          </h1>
          <p className="mt-1.5 max-w-3xl text-[13.5px] leading-relaxed text-ink-2">
            Mengubah <strong>{num(stats.reviews)}</strong> ulasan mentah menjadi sinyal operasional terstruktur pada 14 aspek pariwisata Danau Toba untuk mendukung keputusan dan inspeksi lapangan.
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <Link
            href="/destinasi"
            className="inline-flex items-center gap-1.5 rounded-md border px-3 py-2 text-[12.5px] font-medium text-ink transition-colors hover:bg-surface-2"
            style={{ borderColor: "var(--hairline)" }}
          >
            <span>Katalog Destinasi ({num(stats.canonicalPlaces)})</span>
          </Link>
          <Link
            href="/intervensi"
            className="inline-flex items-center gap-1.5 rounded-md bg-ink px-3.5 py-2 text-[12.5px] font-medium text-plane transition-opacity hover:opacity-90"
          >
            <span>Antrean Tindak Lanjut</span>
            <ArrowRight size={13} />
          </Link>
        </div>
      </section>

      {/* Top Metric Tiles */}
      <section className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatTile
          value={num(stats.reviewsWithText)}
          label="Ulasan Berteks Dianalisis"
          sub={`${num(corpus.reviewsWithPredictions)} ulasan memiliki prediksi aspek.`}
        />
        <StatTile
          value={num(corpus.aspectPredictions)}
          label="Prediksi Aspek Terdeteksi"
          sub={`${num(corpus.destinationsWithSignals)} destinasi memiliki sinyal aktif.`}
        />
        <StatTile
          value={num(stats.ranked)}
          label="Destinasi Actionable"
          sub={`${num(stats.actionableIssues)} isu terverifikasi bukti ulasan.`}
        />
        <StatTile
          value={num(stats.placesGeocoded)}
          label="Destinasi Berkoordinat"
          sub={`${num(stats.canonicalPlaces)} kanonikal · ${num(stats.noData)} placeholder.`}
        />
      </section>

      {/* Quick Urgent Triage Bar */}
      <section className="space-y-2.5">
        <div className="flex items-center justify-between">
          <h2 className="text-[14px] font-semibold uppercase tracking-wider text-muted">
            Prioritas Verifikasi Teratas (Top Urgent)
          </h2>
          <Link href="/intervensi" className="text-[12px] text-accent hover:underline">
            Lihat semua {num(stats.ranked)} antrean →
          </Link>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {topUrgent.map((place) => {
            const mainIssue = place.issues.find(
              (i) => i.priority !== "Insufficient Data",
            );
            return (
              <Card key={place.id} className="p-3.5 transition-all hover:border-ink/40">
                <div className="flex items-center justify-between gap-1">
                  <span className="rounded bg-ink/10 px-1.5 py-0.5 text-[11px] font-bold text-ink">
                    #{place.rank}
                  </span>
                  <LevelBadge level={levelOfPlace(place)} size="sm" />
                </div>
                <h3 className="mt-2 text-[13.5px] font-semibold">
                  <Link href={`/destinasi/${place.id}`} className="hover:underline">
                    {place.name}
                  </Link>
                </h3>
                <p className="text-[11px] text-muted">{place.kabupaten}</p>
                {mainIssue ? (
                  <div className="mt-2.5 flex items-center gap-1.5 rounded border px-2 py-1 text-[11px]" style={{ borderColor: "var(--hairline)", background: "var(--surface-2)" }}>
                    <AspectIcon aspect={mainIssue.aspect} />
                    <span className="truncate">{ASPECT_LABEL[mainIssue.aspect]}</span>
                    <span className="ml-auto font-semibold text-accent">
                      {score(place.priorityScore)}
                    </span>
                  </div>
                ) : null}
              </Card>
            );
          })}
        </div>
      </section>

      {/* Main Interactive Map Explorer */}
      <FrictionExplorer places={mapPlaces} kabupatenList={kabupatenList} />
    </div>
  );
}
