"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  Compass,
  EyeOff,
  Filter,
  MapPin,
  Search,
  SlidersHorizontal,
  X,
} from "lucide-react";
import type { Place, PlaceKind } from "@/lib/types";
import {
  ASPECT_LABEL,
  levelOfPlace,
  num,
  score,
} from "@/lib/format";
import { AspectIcon } from "@/components/AppIcon";
import {
  Badge,
  Card,
  ConfidenceBadge,
  Empty,
  LevelBadge,
} from "@/components/ui";

const KIND_SHORT: Record<PlaceKind, string> = {
  wisata: "Wisata",
  kuliner: "Kuliner",
  akomodasi: "Akomodasi",
  layanan: "Layanan",
};

interface Props {
  places: Place[];
  kabupatenList: string[];
}

export default function DestinationDirectoryClient({
  places,
  kabupatenList,
}: Props) {
  const [query, setQuery] = useState("");
  const [kind, setKind] = useState<string>("all");
  const [kabupaten, setKabupaten] = useState<string>("all");
  const [level, setLevel] = useState<string>("all");
  const [sortBy, setSortBy] = useState<"rank" | "score" | "reviews" | "name">("rank");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return places
      .filter((p) => {
        if (q) {
          const matchName = p.name.toLowerCase().includes(q);
          const matchKab = p.kabupaten.toLowerCase().includes(q);
          const matchKec = (p.kecamatan ?? "").toLowerCase().includes(q);
          const matchAddr = (p.address ?? "").toLowerCase().includes(q);
          if (!matchName && !matchKab && !matchKec && !matchAddr) return false;
        }
        if (kind !== "all" && p.kind !== kind) return false;
        if (kabupaten !== "all" && p.kabupaten !== kabupaten) return false;
        if (level !== "all") {
          if (level === "actionable" && p.priority === "Insufficient Data") return false;
          if (level === "unresolved" && p.canonicalStatus !== "unresolved_placeholder") return false;
          if (level !== "actionable" && level !== "unresolved" && p.priority !== level) return false;
        }
        return true;
      })
      .sort((a, b) => {
        if (sortBy === "rank") {
          const rA = a.rank ?? 9999;
          const rB = b.rank ?? 9999;
          if (rA !== rB) return rA - rB;
          return (b.priorityScore ?? -1) - (a.priorityScore ?? -1);
        }
        if (sortBy === "score") {
          return (b.priorityScore ?? -1) - (a.priorityScore ?? -1);
        }
        if (sortBy === "reviews") {
          return b.textReviewCount - a.textReviewCount;
        }
        if (sortBy === "name") {
          return a.name.localeCompare(b.name);
        }
        return 0;
      });
  }, [places, query, kind, kabupaten, level, sortBy]);

  const actionableCount = places.filter((p) => (p.rank ?? 0) > 0).length;

  return (
    <div className="space-y-4">
      {/* Search & Filter Bar */}
      <Card className="p-3 sm:p-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          {/* Search Box */}
          <div className="relative flex-1">
            <Search
              size={15}
              className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted"
            />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Cari nama destinasi, kabupaten, kecamatan, atau alamat..."
              className="w-full rounded-md border bg-transparent py-2 pl-9 pr-8 text-[13px] outline-none transition-colors placeholder:text-muted focus:border-ink"
              style={{ borderColor: "var(--hairline)" }}
            />
            {query ? (
              <button
                type="button"
                onClick={() => setQuery("")}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted hover:text-ink"
                aria-label="Hapus pencarian"
              >
                <X size={14} />
              </button>
            ) : null}
          </div>

          {/* Filter Dropdowns */}
          <div className="flex flex-wrap items-center gap-2">
            {/* Kind Filter */}
            <select
              value={kind}
              onChange={(e) => setKind(e.target.value)}
              className="rounded-md border bg-transparent px-2.5 py-1.5 text-[12px] text-ink outline-none"
              style={{ borderColor: "var(--hairline)", background: "var(--surface-2)" }}
            >
              <option value="all">Semua Kategori</option>
              <option value="wisata">Destinasi Wisata</option>
              <option value="akomodasi">Hotel / Penginapan</option>
              <option value="kuliner">Restoran / Kuliner</option>
              <option value="layanan">Layanan Lainnya</option>
            </select>

            {/* Kabupaten Filter */}
            <select
              value={kabupaten}
              onChange={(e) => setKabupaten(e.target.value)}
              className="rounded-md border bg-transparent px-2.5 py-1.5 text-[12px] text-ink outline-none"
              style={{ borderColor: "var(--hairline)", background: "var(--surface-2)" }}
            >
              <option value="all">Semua Kabupaten</option>
              {kabupatenList.map((k) => (
                <option key={k} value={k}>
                  {k}
                </option>
              ))}
            </select>

            {/* Level Filter */}
            <select
              value={level}
              onChange={(e) => setLevel(e.target.value)}
              className="rounded-md border bg-transparent px-2.5 py-1.5 text-[12px] text-ink outline-none"
              style={{ borderColor: "var(--hairline)", background: "var(--surface-2)" }}
            >
              <option value="all">Semua Status</option>
              <option value="actionable">Actionable ({actionableCount})</option>
              <option value="Critical">Prioritas Critical</option>
              <option value="High">Prioritas High</option>
              <option value="Medium">Prioritas Medium</option>
              <option value="Monitor">Prioritas Monitor</option>
              <option value="unresolved">Placeholder Unresolved</option>
            </select>

            {/* Sort Dropdown */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as never)}
              className="rounded-md border bg-transparent px-2.5 py-1.5 text-[12px] text-ink outline-none"
              style={{ borderColor: "var(--hairline)", background: "var(--surface-2)" }}
            >
              <option value="rank">Urut: Prioritas Utama</option>
              <option value="score">Urut: Skor Tertinggi</option>
              <option value="reviews">Urut: Ulasan Terbanyak</option>
              <option value="name">Urut: Nama (A-Z)</option>
            </select>
          </div>
        </div>

        {/* Counter Bar */}
        <div className="mt-3 flex items-center justify-between border-t pt-2.5 text-[11px] text-muted" style={{ borderColor: "var(--hairline)" }}>
          <span>
            Menampilkan <strong className="text-ink">{num(filtered.length)}</strong> dari {num(places.length)} destinasi kanonikal
          </span>
          {query || kind !== "all" || kabupaten !== "all" || level !== "all" ? (
            <button
              type="button"
              onClick={() => {
                setQuery("");
                setKind("all");
                setKabupaten("all");
                setLevel("all");
              }}
              className="text-accent hover:underline"
            >
              Reset seluruh filter
            </button>
          ) : null}
        </div>
      </Card>

      {/* Directory Grid */}
      {filtered.length === 0 ? (
        <Empty>
          Tidak ada destinasi yang cocok dengan kriteria pencarian atau filter yang dipilih.
        </Empty>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {filtered.map((place) => {
            const pLevel = levelOfPlace(place);
            const isActionable = (place.rank ?? 0) > 0;
            return (
              <Card
                key={place.id}
                className="flex flex-col justify-between p-4 transition-all hover:border-ink/40"
              >
                <div>
                  {/* Top Row: Rank & Badges */}
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-1.5">
                      {isActionable ? (
                        <span className="rounded bg-ink/10 px-1.5 py-0.5 text-[11px] font-bold text-ink">
                          #{place.rank}
                        </span>
                      ) : (
                        <span className="rounded bg-muted/10 px-1.5 py-0.5 text-[10px] text-muted">
                          Audit
                        </span>
                      )}
                      <LevelBadge level={pLevel} size="sm" />
                    </div>
                    <span className="text-[11px] text-muted">
                      {KIND_SHORT[place.kind]}
                    </span>
                  </div>

                  {/* Title */}
                  <h3 className="mt-2.5 text-[15px] font-semibold tracking-tight">
                    <Link
                      href={`/destinasi/${place.id}`}
                      className="hover:text-accent hover:underline"
                    >
                      {place.name}
                    </Link>
                  </h3>

                  {/* Location info */}
                  <p className="mt-1 flex items-center gap-1 text-[12px] text-ink-2">
                    <MapPin size={12} className="shrink-0 text-muted" />
                    <span className="truncate">
                      {place.kabupaten}
                      {place.kecamatan ? ` · ${place.kecamatan}` : ""}
                    </span>
                  </p>

                  {/* Top Aspects */}
                  {place.topAspects.length > 0 ? (
                    <div className="mt-3 flex flex-wrap gap-1">
                      {place.topAspects.slice(0, 3).map((asp) => (
                        <span
                          key={asp}
                          className="inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-[10.5px] text-ink-2"
                          style={{
                            borderColor: "var(--hairline)",
                            background: "var(--surface-2)",
                          }}
                        >
                          <AspectIcon aspect={asp} />
                          {ASPECT_LABEL[asp]}
                        </span>
                      ))}
                      {place.topAspects.length > 3 ? (
                        <span className="rounded px-1.5 py-0.5 text-[10px] text-muted">
                          +{place.topAspects.length - 3}
                        </span>
                      ) : null}
                    </div>
                  ) : null}
                </div>

                {/* Bottom Meta & Action */}
                <div className="mt-4 border-t pt-3" style={{ borderColor: "var(--hairline)" }}>
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-muted">
                      {num(place.textReviewCount)} teks / {num(place.allReviewCount)} ulasan
                    </span>
                    {isActionable ? (
                      <span className="font-semibold text-ink">
                        Skor {score(place.priorityScore)}
                      </span>
                    ) : (
                      <ConfidenceBadge confidence={place.dataConfidence} />
                    )}
                  </div>

                  <Link
                    href={`/destinasi/${place.id}`}
                    className="mt-2.5 flex items-center justify-between rounded-md border px-2.5 py-1.5 text-[11.5px] font-medium text-ink transition-colors hover:bg-surface-2"
                    style={{ borderColor: "var(--hairline)" }}
                  >
                    <span>Lihat Detail &amp; Sinyal</span>
                    <ArrowRight size={12} />
                  </Link>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
