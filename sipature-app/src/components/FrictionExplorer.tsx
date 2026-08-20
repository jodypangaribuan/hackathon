"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { ChevronDown, MapPin } from "lucide-react";
import type { AspectKey, PlaceKind } from "@/lib/types";
import {
  ASPECT_LABEL,
  SIGNAL_ASPECTS,
  levelOf,
  num,
  score,
} from "@/lib/format";
import { Card, Empty, LevelBadge, Note, SectionTitle } from "@/components/ui";
import TobaMap, { type MapPoint } from "@/components/TobaMap";
import { AspectIcon } from "@/components/AppIcon";

export type MapPlace = MapPoint;

const KIND: Record<PlaceKind, string> = {
  wisata: "Wisata",
  kuliner: "Kuliner",
  akomodasi: "Akomodasi",
  layanan: "Layanan",
};

export default function FrictionExplorer({
  places,
  kabupatenList,
}: {
  places: MapPlace[];
  kabupatenList: string[];
}) {
  const router = useRouter();
  const [kabupaten, setKabupaten] = useState("");
  const [kind, setKind] = useState<PlaceKind | "">("");
  const [aspect, setAspect] = useState<AspectKey | "">("");
  const [query, setQuery] = useState("");
  const [showInsufficient, setShowInsufficient] = useState(true);

  const filtered = useMemo(
    () =>
      places.filter((place) => {
        const q = query.trim().toLowerCase();
        return (
          (!kabupaten || place.kabupaten === kabupaten) &&
          (!kind || place.kind === kind) &&
          (!aspect || place.topAspects.includes(aspect)) &&
          (showInsufficient || place.priority !== "Insufficient Data") &&
          (!q || place.name.toLowerCase().includes(q))
        );
      }),
    [places, kabupaten, kind, aspect, query, showInsufficient],
  );

  const ranked = useMemo(
    () =>
      filtered
        .filter((place) => place.rank !== null)
        .sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0)),
    [filtered],
  );

  const handleSelect = (id: string) => {
    router.push(`/destinasi/${id}`);
  };

  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_360px]">
      <div className="min-w-0">
        <Card className="mb-3 p-3">
          <div className="flex flex-wrap items-center gap-2">
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Cari nama tempat…"
              className="min-w-[160px] flex-1 rounded-md border bg-transparent px-2.5 py-1.5 text-[13px] outline-none placeholder:text-muted focus:border-ink"
              style={{ borderColor: "var(--hairline)" }}
            />
            <div className="relative">
              <select
                value={kabupaten}
                onChange={(e) => setKabupaten(e.target.value)}
                className="appearance-none rounded-md border bg-surface py-1.5 pl-2 pr-8 text-[13px] outline-none"
                style={{ borderColor: "var(--hairline)" }}
              >
                <option value="">Semua kabupaten</option>
                {kabupatenList.map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
              <ChevronDown
                aria-hidden="true"
                className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-muted"
                size={14}
                strokeWidth={1.8}
              />
            </div>
            <div className="relative">
              <select
                value={kind}
                onChange={(e) => setKind(e.target.value as PlaceKind | "")}
                className="appearance-none rounded-md border bg-surface py-1.5 pl-2 pr-8 text-[13px] outline-none"
                style={{ borderColor: "var(--hairline)" }}
              >
                <option value="">Semua jenis</option>
                {(Object.keys(KIND) as PlaceKind[]).map((item) => (
                  <option key={item} value={item}>
                    {KIND[item]}
                  </option>
                ))}
              </select>
              <ChevronDown
                aria-hidden="true"
                className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-muted"
                size={14}
                strokeWidth={1.8}
              />
            </div>
            <div className="relative">
              <select
                value={aspect}
                onChange={(e) => setAspect(e.target.value as AspectKey | "")}
                className="appearance-none rounded-md border bg-surface py-1.5 pl-2 pr-8 text-[13px] outline-none"
                style={{ borderColor: "var(--hairline)" }}
              >
                <option value="">Semua aspek</option>
                {SIGNAL_ASPECTS.map((item) => (
                  <option key={item} value={item}>
                    {ASPECT_LABEL[item]}
                  </option>
                ))}
              </select>
              <ChevronDown
                aria-hidden="true"
                className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-muted"
                size={14}
                strokeWidth={1.8}
              />
            </div>
            <label className="flex items-center gap-1.5 text-[12px] text-ink-2 cursor-pointer">
              <input
                type="checkbox"
                checked={showInsufficient}
                onChange={(e) => setShowInsufficient(e.target.checked)}
                className="rounded"
              />
              Data belum cukup
            </label>
            <span className="ml-auto text-[12px] text-muted">
              {num(filtered.length)} dari {num(places.length)}
            </span>
          </div>
        </Card>

        {/* Interactive Map */}
        <Card className="overflow-hidden">
          <TobaMap
            points={filtered}
            onSelect={handleSelect}
            heightClass="h-[460px] sm:h-[560px]"
          />
        </Card>
      </div>

      {/* Sidebar Priority List */}
      <div>
        <Card className="p-4">
          <SectionTitle hint={`${num(ranked.length)} tempat`}>
            Prioritas Verifikasi
          </SectionTitle>
          <p className="mb-3 text-[12px] text-muted">
            Urut menurut priority score SIPATURE. Klik nama tempat untuk membuka lembar aksi.
          </p>
          {ranked.length ? (
            <ol className="thin-scroll max-h-[560px] space-y-1 overflow-y-auto">
              {ranked.map((place) => (
                <li key={place.id}>
                  <Link
                    href={`/destinasi/${place.id}`}
                    className="flex items-center gap-3 rounded-md border px-2.5 py-2 transition-colors hover:bg-surface-2 hover:border-ink/40"
                    style={{ borderColor: "var(--hairline)" }}
                  >
                    <span className="w-8 text-right text-[12px] text-muted font-mono">
                      #{place.rank}
                    </span>
                    <span style={{ color: levelOf(place.priority).colorVar }}>
                      {levelOf(place.priority).icon}
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-[13px] font-medium text-ink">
                        {place.name}
                      </span>
                      <span className="block truncate text-[11px] text-muted">
                        {place.kabupaten}
                        {place.topAspects[0]
                          ? ` · ${ASPECT_LABEL[place.topAspects[0]]}`
                          : ""}
                      </span>
                    </span>
                    <span className="tabular text-[13px] font-bold text-accent">
                      {score(place.priorityScore)}
                    </span>
                  </Link>
                </li>
              ))}
            </ol>
          ) : (
            <Empty>Tidak ada destinasi yang lolos filter.</Empty>
          )}
        </Card>
        <div className="mt-3">
          <Note>
            Sinyal prioritas dihitung dari frekuensi keluhan, tingkat keyakinan model, dan volume eksposur ulasan wisatawan.
          </Note>
        </div>
      </div>
    </div>
  );
}
