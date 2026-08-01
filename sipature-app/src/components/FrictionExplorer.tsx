"use client";
import Link from "next/link";
import { useMemo, useState } from "react";
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
  const [kabupaten, setKabupaten] = useState("");
  const [kind, setKind] = useState<PlaceKind | "">("");
  const [aspect, setAspect] = useState<AspectKey | "">("");
  const [query, setQuery] = useState("");
  const [showInsufficient, setShowInsufficient] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);
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
  const selected = places.find((place) => place.id === selectedId) ?? null;
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
              className="min-w-[160px] flex-1 rounded-md border bg-transparent px-2.5 py-1.5 text-[13px]"
              style={{ borderColor: "var(--hairline)" }}
            />
            <select
              value={kabupaten}
              onChange={(e) => setKabupaten(e.target.value)}
              className="rounded-md border bg-surface px-2 py-1.5 text-[13px]"
              style={{ borderColor: "var(--hairline)" }}
            >
              <option value="">Semua kabupaten</option>
              {kabupatenList.map((item) => (
                <option key={item}>{item}</option>
              ))}
            </select>
            <select
              value={kind}
              onChange={(e) => setKind(e.target.value as PlaceKind | "")}
              className="rounded-md border bg-surface px-2 py-1.5 text-[13px]"
              style={{ borderColor: "var(--hairline)" }}
            >
              <option value="">Semua jenis</option>
              {(Object.keys(KIND) as PlaceKind[]).map((item) => (
                <option key={item} value={item}>
                  {KIND[item]}
                </option>
              ))}
            </select>
            <select
              value={aspect}
              onChange={(e) => setAspect(e.target.value as AspectKey | "")}
              className="rounded-md border bg-surface px-2 py-1.5 text-[13px]"
              style={{ borderColor: "var(--hairline)" }}
            >
              <option value="">Semua aspek</option>
              {SIGNAL_ASPECTS.map((item) => (
                <option key={item} value={item}>
                  {ASPECT_LABEL[item]}
                </option>
              ))}
            </select>
            <label className="flex items-center gap-1.5 text-[12px] text-ink-2">
              <input
                type="checkbox"
                checked={showInsufficient}
                onChange={(e) => setShowInsufficient(e.target.checked)}
              />
              Data tidak cukup
            </label>
            <span className="ml-auto text-[12px] text-muted">
              {num(filtered.length)} dari {num(places.length)}
            </span>
          </div>
        </Card>
        <Card className="overflow-hidden">
          <TobaMap
            points={filtered}
            selectedId={selectedId}
            onSelect={(id) =>
              setSelectedId((current) => (current === id ? null : id))
            }
            heightClass="h-[420px] sm:h-[520px]"
          />
        </Card>
        {selected ? (
          <Card className="mt-3 p-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-[15px] font-semibold">{selected.name}</h3>
                  <LevelBadge level={levelOf(selected.priority)} size="sm" />
                </div>
                <p className="mt-1 text-[12px] text-muted">
                  {KIND[selected.kind]} · {selected.kabupaten} ·{" "}
                  {num(selected.allReviewCount)} review bersih
                  {selected.rank ? ` · prioritas #${selected.rank}` : ""}
                </p>
                <p className="mt-2 text-[12px] text-ink-2">
                  {selected.topAspects.map((item) => (
                    <span
                      key={item}
                      className="mr-3 inline-flex items-center gap-1"
                    >
                      <AspectIcon aspect={item} />
                      {ASPECT_LABEL[item]}
                    </span>
                  ))}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <div className="tabular text-[24px] font-semibold">
                    {score(selected.priorityScore)}
                  </div>
                  <div className="text-[11px] text-muted">priority score</div>
                </div>
                <Link
                  href={`/destinasi/${selected.id}`}
                  className="rounded-md border px-3 py-1.5 text-[13px]"
                  style={{ borderColor: "var(--hairline)" }}
                >
                  Buka rapor →
                </Link>
              </div>
            </div>
          </Card>
        ) : (
          <p className="mt-3 text-center text-[12px] text-muted">
            Klik titik untuk melihat ringkasan.
          </p>
        )}
      </div>
      <div>
        <Card className="p-4">
          <SectionTitle hint={`${num(ranked.length)} tempat`}>
            Prioritas Verifikasi
          </SectionTitle>
          <p className="mb-3 text-[12px] text-muted">
            Urut menurut priority score A9. Peringkat adalah sinyal triase,
            bukan bukti kondisi lapangan.
          </p>
          {ranked.length ? (
            <ol className="thin-scroll max-h-[560px] space-y-1 overflow-y-auto">
              {ranked.map((place) => (
                <li key={place.id}>
                  <Link
                    href={`/destinasi/${place.id}`}
                    className="flex items-center gap-3 rounded-md border px-2.5 py-2"
                    style={{ borderColor: "var(--hairline)" }}
                  >
                    <span className="w-8 text-right text-[12px] text-muted">
                      #{place.rank}
                    </span>
                    <span style={{ color: levelOf(place.priority).colorVar }}>
                      {levelOf(place.priority).icon}
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-[13px] font-medium">
                        {place.name}
                      </span>
                      <span className="block truncate text-[11px] text-muted">
                        {place.kabupaten}
                        {place.topAspects[0]
                          ? ` · ${ASPECT_LABEL[place.topAspects[0]]}`
                          : ""}
                      </span>
                    </span>
                    <span className="tabular text-[13px] font-semibold">
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
            Priority memakai complaint frequency, confidence, persistence, dan
            exposure. Severity, facility gap, serta feasibility unavailable dan
            dinormalisasi keluar.
          </Note>
        </div>
      </div>
    </div>
  );
}
