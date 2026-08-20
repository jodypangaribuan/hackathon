import type { Metadata } from "next";
import Link from "next/link";
import {
  ArrowRight,
  CheckCircle2,
  ClipboardCheck,
  Compass,
  MapPin,
  Search,
  ShieldAlert,
  Sparkles,
} from "lucide-react";
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
  description: "Sistem Pemantauan Kualitas dan Rekomendasi Tindak Lanjut Pariwisata Danau Toba.",
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
      {/* Hero Section */}
      <section className="flex flex-col justify-between gap-4 border-b pb-5 lg:flex-row lg:items-end" style={{ borderColor: "var(--hairline)" }}>
        <div>
          <div className="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-[11.5px] font-medium text-accent" style={{ borderColor: "var(--accent)", background: "rgba(235,108,54,0.06)" }}>
            <Sparkles size={12} />
            <span>Pusat Kendali Mutu Pariwisata Danau Toba</span>
          </div>
          <h1 className="mt-2 text-[24px] font-semibold tracking-tight sm:text-[28px]">
            Masalah destinasi mana yang harus diperbaiki lebih dulu?
          </h1>
          <p className="mt-1.5 max-w-3xl text-[13.5px] leading-relaxed text-ink-2">
            Membantu pengelola wisata, POKDARWIS, dan dinas pariwisata menyaring ribuan suara wisatawan menjadi daftar prioritas perbaikan nyata yang terukur di 14 aspek fasilitas.
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <Link
            href="/destinasi"
            className="inline-flex items-center gap-1.5 rounded-md border px-3.5 py-2 text-[12.5px] font-medium text-ink transition-colors hover:bg-surface-2"
            style={{ borderColor: "var(--hairline)" }}
          >
            <Compass size={14} />
            <span>Cari Destinasi ({num(stats.canonicalPlaces)})</span>
          </Link>
          <Link
            href="/intervensi"
            className="inline-flex items-center gap-1.5 rounded-md bg-ink px-4 py-2 text-[12.5px] font-medium text-plane transition-opacity hover:opacity-90"
          >
            <ClipboardCheck size={14} />
            <span>Antrean Tindak Lanjut</span>
            <ArrowRight size={13} />
          </Link>
        </div>
      </section>

      {/* 3-Step Simple Workflow Guide */}
      <section className="grid gap-3 sm:grid-cols-3">
        <Card className="p-3.5">
          <div className="flex items-center gap-2.5">
            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-accent text-[11px] font-bold text-white">
              1
            </span>
            <h3 className="text-[13px] font-semibold">Pantau Sebaran Masalah</h3>
          </div>
          <p className="mt-2 text-[12px] leading-relaxed text-ink-2">
            Gunakan peta wilayah di bawah untuk memantau titik-titik keluhan wisatawan di 8 kabupaten Danau Toba.
          </p>
        </Card>

        <Card className="p-3.5">
          <div className="flex items-center gap-2.5">
            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-ink text-[11px] font-bold text-plane">
              2
            </span>
            <h3 className="text-[13px] font-semibold">Tinjau Rekomendasi Aksi</h3>
          </div>
          <p className="mt-2 text-[12px] leading-relaxed text-ink-2">
            Lihat rincian masalah per lokasi (sanitasi, jalan, tiket, staf) beserta langkah perbaikan yang disarankan.
          </p>
        </Card>

        <Card className="p-3.5">
          <div className="flex items-center gap-2.5">
            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-ink-2 text-[11px] font-bold text-plane">
              3
            </span>
            <h3 className="text-[13px] font-semibold">Verifikasi Lapangan</h3>
          </div>
          <p className="mt-2 text-[12px] leading-relaxed text-ink-2">
            Petugas melakukan pengecekan fisik di lokasi dan menandai status penanganan secara bertanggung jawab.
          </p>
        </Card>
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

      {/* Top Urgent Triage Rail */}
      <section className="space-y-2.5">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-[14px] font-semibold tracking-tight text-ink">
              Destinasi Membutuhkan Penanganan Segera
            </h2>
            <p className="text-[11.5px] text-muted">
              Berdasarkan frekuensi keluhan berulang wisatawan terbaru
            </p>
          </div>
          <Link href="/intervensi" className="text-[12px] font-medium text-accent hover:underline">
            Lihat semua {num(stats.ranked)} antrean →
          </Link>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {topUrgent.map((place) => {
            const mainIssue = place.issues.find(
              (i) => i.priority !== "Insufficient Data",
            );
            return (
              <Card key={place.id} className="flex flex-col justify-between p-3.5 transition-all hover:border-ink/40">
                <div>
                  <div className="flex items-center justify-between gap-1">
                    <span className="rounded bg-ink/10 px-1.5 py-0.5 text-[11px] font-bold text-ink">
                      #{place.rank}
                    </span>
                    <LevelBadge level={levelOfPlace(place)} size="sm" />
                  </div>
                  <h3 className="mt-2 text-[13.5px] font-semibold leading-snug">
                    <Link href={`/destinasi/${place.id}`} className="hover:text-accent hover:underline">
                      {place.name}
                    </Link>
                  </h3>
                  <p className="mt-0.5 text-[11.5px] text-muted">{place.kabupaten}</p>
                  {mainIssue ? (
                    <div className="mt-2.5 flex items-center gap-1.5 rounded border px-2 py-1 text-[11px]" style={{ borderColor: "var(--hairline)", background: "var(--surface-2)" }}>
                      <AspectIcon aspect={mainIssue.aspect} />
                      <span className="truncate font-medium">{ASPECT_LABEL[mainIssue.aspect]}</span>
                      <span className="ml-auto font-bold text-accent">
                        {score(place.priorityScore)}
                      </span>
                    </div>
                  ) : null}
                </div>
                <Link
                  href={`/destinasi/${place.id}`}
                  className="mt-3 flex items-center justify-between border-t pt-2 text-[11.5px] font-medium text-accent hover:underline"
                  style={{ borderColor: "var(--hairline)" }}
                >
                  <span>Buka Lembar Aksi</span>
                  <ArrowRight size={12} />
                </Link>
              </Card>
            );
          })}
        </div>
      </section>

      {/* Main Interactive Map */}
      <FrictionExplorer places={mapPlaces} kabupatenList={kabupatenList} />
    </div>
  );
}
