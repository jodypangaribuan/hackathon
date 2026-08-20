"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  ClipboardCheck,
  Filter,
  MapPin,
  Search,
  SlidersHorizontal,
  X,
} from "lucide-react";
import type { AspectKey, Place } from "@/lib/types";
import {
  ASPECT_LABEL,
  levelOfPlace,
  num,
  score,
} from "@/lib/format";
import { AspectIcon } from "@/components/AppIcon";
import { Card, Empty, LevelBadge, SectionTitle } from "@/components/ui";

interface Props {
  rankedPlaces: Place[];
}

export default function InterventionQueueClient({ rankedPlaces }: Props) {
  const [query, setQuery] = useState("");
  const [kabupaten, setKabupaten] = useState("all");
  const [urgencyFilter, setUrgencyFilter] = useState<string>("all");
  const [aspectFilter, setAspectFilter] = useState<string>("all");

  const kabupatenList = useMemo(
    () => Array.from(new Set(rankedPlaces.map((p) => p.kabupaten))).sort(),
    [rankedPlaces],
  );

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return rankedPlaces.filter((place) => {
      if (q) {
        const matchName = place.name.toLowerCase().includes(q);
        const matchKab = place.kabupaten.toLowerCase().includes(q);
        if (!matchName && !matchKab) return false;
      }
      if (kabupaten !== "all" && place.kabupaten !== kabupaten) return false;
      if (urgencyFilter !== "all") {
        if (urgencyFilter === "high" && place.priority !== "High" && place.priority !== "Critical") return false;
        if (urgencyFilter === "medium" && place.priority !== "Medium") return false;
        if (urgencyFilter === "monitor" && place.priority !== "Monitor") return false;
      }
      if (aspectFilter !== "all") {
        const hasAspect = place.issues.some(
          (i) => i.aspect === aspectFilter && i.priority !== "Insufficient Data",
        );
        if (!hasAspect) return false;
      }
      return true;
    });
  }, [rankedPlaces, query, kabupaten, urgencyFilter, aspectFilter]);

  const urgentCount = rankedPlaces.filter(
    (p) => p.priority === "High" || p.priority === "Critical",
  ).length;

  return (
    <div className="space-y-4">
      {/* Search & Quick Filter Controls */}
      <Card className="p-3 sm:p-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          {/* Search box */}
          <div className="relative flex-1">
            <Search
              size={15}
              className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted"
            />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Cari nama destinasi atau kabupaten..."
              className="w-full rounded-md border bg-transparent py-2 pl-9 pr-8 text-[13px] outline-none transition-colors placeholder:text-muted focus:border-ink"
              style={{ borderColor: "var(--hairline)" }}
            />
            {query ? (
              <button
                type="button"
                onClick={() => setQuery("")}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted hover:text-ink"
              >
                <X size={14} />
              </button>
            ) : null}
          </div>

          {/* Quick Filters */}
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => setUrgencyFilter(urgencyFilter === "high" ? "all" : "high")}
              className="rounded-md border px-2.5 py-1.5 text-[12px] font-medium transition-colors"
              style={{
                borderColor: urgencyFilter === "high" ? "var(--status-critical)" : "var(--hairline)",
                background: urgencyFilter === "high" ? "rgba(220,38,38,0.08)" : "var(--surface-2)",
                color: urgencyFilter === "high" ? "var(--status-critical)" : "var(--text-secondary)",
              }}
            >
              🔴 Perlu Tindakan Segera ({urgentCount})
            </button>

            <select
              value={kabupaten}
              onChange={(e) => setKabupaten(e.target.value)}
              className="rounded-md border px-2.5 py-1.5 text-[12px] text-ink outline-none"
              style={{ borderColor: "var(--hairline)", background: "var(--surface-2)" }}
            >
              <option value="all">Semua Kabupaten</option>
              {kabupatenList.map((k) => (
                <option key={k} value={k}>
                  {k}
                </option>
              ))}
            </select>

            <select
              value={aspectFilter}
              onChange={(e) => setAspectFilter(e.target.value)}
              className="rounded-md border px-2.5 py-1.5 text-[12px] text-ink outline-none"
              style={{ borderColor: "var(--hairline)", background: "var(--surface-2)" }}
            >
              <option value="all">Semua Topik Masalah</option>
              <option value="sanitation">Toilet & Sanitasi</option>
              <option value="cleanliness">Kebersihan & Sampah</option>
              <option value="access">Akses & Kondisi Rute</option>
              <option value="price_transparency">Harga & Pungli</option>
              <option value="staff_service">Pelayanan Petugas</option>
              <option value="parking">Parkir</option>
              <option value="maintenance">Perawatan Fasilitas</option>
            </select>
          </div>
        </div>

        <div className="mt-3 flex items-center justify-between border-t pt-2 text-[11px] text-muted" style={{ borderColor: "var(--hairline)" }}>
          <span>
            Menampilkan <strong className="text-ink">{num(filtered.length)}</strong> dari {num(rankedPlaces.length)} destinasi prioritas
          </span>
          {query || kabupaten !== "all" || urgencyFilter !== "all" || aspectFilter !== "all" ? (
            <button
              onClick={() => {
                setQuery("");
                setKabupaten("all");
                setUrgencyFilter("all");
                setAspectFilter("all");
              }}
              className="text-accent hover:underline"
            >
              Reset filter
            </button>
          ) : null}
        </div>
      </Card>

      {/* Triage Work Orders Table */}
      <Card className="overflow-hidden">
        <div className="p-4 sm:p-5 border-b" style={{ borderColor: "var(--hairline)" }}>
          <SectionTitle hint="Urut berdasarkan skor urgensi keluhan wisatawan">
            Daftar Tugas Verifikasi &amp; Penanganan Lapangan
          </SectionTitle>
          <p className="text-[12.5px] text-ink-2">
            Gunakan daftar tugas ini untuk meninjau titik keluhan fisik dan mencatat hasil inspeksi langsung di lapangan.
          </p>
        </div>

        {filtered.length === 0 ? (
          <div className="p-6">
            <Empty>Tidak ada destinasi yang cocok dengan filter yang dipilih.</Empty>
          </div>
        ) : (
          <div className="thin-scroll overflow-x-auto">
            <table className="w-full min-w-[900px] text-left text-[12.5px]">
              <thead
                className="border-b text-[11px] uppercase tracking-wider text-muted"
                style={{
                  borderColor: "var(--hairline)",
                  background: "var(--surface-2)",
                }}
              >
                <tr>
                  <th className="px-4 py-2.5">Tingkat Urgensi</th>
                  <th className="px-3 py-2.5">Destinasi &amp; Lokasi</th>
                  <th className="px-3 py-2.5">Masalah Utama</th>
                  <th className="px-3 py-2.5">Bukti Keluhan</th>
                  <th className="px-3 py-2.5">Panduan Cek Lapangan</th>
                  <th className="px-4 py-2.5 text-right">Aksi</th>
                </tr>
              </thead>
              <tbody className="divide-y" style={{ borderColor: "var(--hairline)" }}>
                {filtered.map((place) => {
                  const issue = place.issues.find(
                    (item) => item.priority !== "Insufficient Data",
                  );
                  return (
                    <tr
                      key={place.id}
                      className="transition-colors hover:bg-surface-2/60"
                    >
                      {/* Urgency Rank */}
                      <td className="px-4 py-3.5">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-ink">#{place.rank}</span>
                          <LevelBadge level={levelOfPlace(place)} size="sm" />
                        </div>
                      </td>

                      {/* Place Name & Location */}
                      <td className="px-3 py-3.5">
                        <Link
                          href={`/destinasi/${place.id}`}
                          className="font-semibold text-ink hover:text-accent hover:underline"
                        >
                          {place.name}
                        </Link>
                        <span className="block text-[11.5px] text-muted">
                          {place.kabupaten} · Skor Urgensi {score(place.priorityScore)}
                        </span>
                      </td>

                      {/* Main Aspect Issue */}
                      <td className="px-3 py-3.5">
                        {issue ? (
                          <span className="inline-flex items-center gap-1.5 font-medium text-ink">
                            <AspectIcon aspect={issue.aspect} size={15} />
                            {ASPECT_LABEL[issue.aspect]}
                          </span>
                        ) : (
                          "–"
                        )}
                      </td>

                      {/* Evidence / Support */}
                      <td className="px-3 py-3.5">
                        {issue ? (
                          <div>
                            <span className="font-medium text-ink">
                              {num(issue.negativeCount)} keluhan
                            </span>
                            <span className="text-muted text-[11px] block">
                              dari {num(issue.mentionCount)} sebutan ulasan
                            </span>
                          </div>
                        ) : (
                          "–"
                        )}
                      </td>

                      {/* Action / Recommended Verification */}
                      <td className="max-w-[320px] px-3 py-3.5 text-ink-2">
                        {issue ? (
                          <div className="line-clamp-2 text-[12px] leading-relaxed">
                            {issue.recommendedVerification}
                          </div>
                        ) : (
                          "–"
                        )}
                      </td>

                      {/* Action Link */}
                      <td className="px-4 py-3.5 text-right">
                        <Link
                          href={`/destinasi/${place.id}`}
                          className="inline-flex items-center gap-1 rounded-md border px-2.5 py-1.5 text-[11.5px] font-medium text-ink transition-colors hover:bg-surface-2"
                          style={{ borderColor: "var(--hairline)" }}
                        >
                          <span>Lembar Aksi</span>
                          <ArrowRight size={12} />
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
