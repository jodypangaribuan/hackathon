"use client";

/**
 * Layar 1 — Peta Friksi. Client component interaktif: peta sungguhan
 * (Leaflet + tile gratis, dengan cadangan SVG luring) + filter + peringkat.
 * Menerima data RAMPING lewat props — bukan places.json utuh — supaya bundle
 * tetap kecil.
 */

import Link from "next/link";
import { useMemo, useState } from "react";
import type { AspectKey, PlaceKind } from "@/lib/types";
import {
  ASPECT_ICON,
  ASPECT_LABEL,
  FRICTION_ASPECTS,
  levelOf,
  num,
  score,
} from "@/lib/format";
import { Card, Empty, LevelBadge, Note, SectionTitle } from "@/components/ui";
import TobaMap, { type MapPoint } from "@/components/TobaMap";

/**
 * Versi ramping satu tempat. Bentuknya sama dengan MapPoint di TobaMap —
 * dialiaskan agar halaman pemanggil tidak perlu tahu detail peta.
 */
export type MapPlace = MapPoint;

const KIND_SHORT: Record<PlaceKind, string> = {
  wisata: "Wisata",
  kuliner: "Kuliner",
  akomodasi: "Akomodasi",
};

export default function FrictionExplorer({
  places,
  kabupatenList,
}: {
  places: MapPlace[];
  kabupatenList: string[];
}) {
  const [kabupaten, setKabupaten] = useState<string>("");
  const [kind, setKind] = useState<PlaceKind | "">("");
  const [aspect, setAspect] = useState<AspectKey | "">("");
  const [query, setQuery] = useState("");
  const [showNoData, setShowNoData] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return places.filter((p) => {
      if (kabupaten && p.kabupaten !== kabupaten) return false;
      if (kind && p.kind !== kind) return false;
      if (aspect && !p.topAspects.includes(aspect)) return false;
      if (!showNoData && (p.confidence === "none" || p.confidence === "low")) return false;
      if (q && !p.name.toLowerCase().includes(q)) return false;
      return true;
    });
  }, [places, kabupaten, kind, aspect, query, showNoData]);

  const ranked = useMemo(
    () =>
      filtered
        .filter((p) => p.rank !== null)
        .sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0)),
    [filtered],
  );

  const selected = useMemo(
    () => places.find((p) => p.id === selectedId) ?? null,
    [places, selectedId],
  );

  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_360px]">
      {/* ------------------------------------------------------------- peta */}
      <div className="min-w-0">
        {/* filter */}
        <Card className="mb-3 p-3">
          <div className="flex flex-wrap items-center gap-2">
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Cari nama tempat…"
              aria-label="Cari nama tempat"
              className="min-w-[160px] flex-1 rounded-md border bg-transparent px-2.5 py-1.5 text-[13px] outline-none placeholder:text-muted"
              style={{ borderColor: "var(--hairline)" }}
            />
            <select
              value={kabupaten}
              onChange={(e) => setKabupaten(e.target.value)}
              aria-label="Filter kabupaten"
              className="rounded-md border bg-surface px-2 py-1.5 text-[13px]"
              style={{ borderColor: "var(--hairline)" }}
            >
              <option value="">Semua kabupaten</option>
              {kabupatenList.map((k) => (
                <option key={k} value={k}>
                  {k}
                </option>
              ))}
            </select>
            <select
              value={kind}
              onChange={(e) => setKind(e.target.value as PlaceKind | "")}
              aria-label="Filter jenis tempat"
              className="rounded-md border bg-surface px-2 py-1.5 text-[13px]"
              style={{ borderColor: "var(--hairline)" }}
            >
              <option value="">Semua jenis</option>
              {(Object.keys(KIND_SHORT) as PlaceKind[]).map((k) => (
                <option key={k} value={k}>
                  {KIND_SHORT[k]}
                </option>
              ))}
            </select>
            <select
              value={aspect}
              onChange={(e) => setAspect(e.target.value as AspectKey | "")}
              aria-label="Filter aspek keluhan utama"
              className="rounded-md border bg-surface px-2 py-1.5 text-[13px]"
              style={{ borderColor: "var(--hairline)" }}
            >
              <option value="">Semua aspek keluhan</option>
              {FRICTION_ASPECTS.map((a) => (
                <option key={a} value={a}>
                  {ASPECT_ICON[a]} {ASPECT_LABEL[a]}
                </option>
              ))}
            </select>
            <label className="flex cursor-pointer items-center gap-1.5 text-[12px] text-ink-2">
              <input
                type="checkbox"
                checked={showNoData}
                onChange={(e) => setShowNoData(e.target.checked)}
                style={{ accentColor: "var(--series-1)" }}
              />
              Tampilkan tempat tanpa cukup data
            </label>
            <span className="tabular ml-auto text-[12px] text-muted">
              {num(filtered.length)} dari {num(places.length)} tempat
            </span>
          </div>
        </Card>

        {/* peta sungguhan — Leaflet + tile gratis, cadangan SVG bila luring */}
        <Card className="overflow-hidden">
          <TobaMap
            points={filtered}
            selectedId={selectedId}
            onSelect={(id) => setSelectedId((cur) => (cur === id ? null : id))}
            heightClass="h-[420px] sm:h-[520px]"
          />
        </Card>

        {/* panel tempat terpilih */}
        {selected ? (
          <Card className="mt-3 p-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="text-[15px] font-semibold">{selected.name}</h3>
                  <LevelBadge level={levelOf(selected.frictionScore, selected.confidence)} size="sm" />
                </div>
                <p className="mt-1 text-[12px] text-muted">
                  {KIND_SHORT[selected.kind]} · {selected.kabupaten} ·{" "}
                  {num(selected.nReviewsText)} ulasan berteks
                  {selected.rank !== null ? ` · prioritas #${selected.rank}` : ""}
                </p>
                {selected.topAspects.length > 0 ? (
                  <p className="mt-2 text-[12px] text-ink-2">
                    Keluhan utama:{" "}
                    {selected.topAspects.slice(0, 3).map((a, i) => (
                      <span key={a}>
                        {i > 0 ? " · " : ""}
                        {ASPECT_ICON[a]} {ASPECT_LABEL[a]}
                      </span>
                    ))}
                  </p>
                ) : null}
              </div>
              <div className="flex shrink-0 items-center gap-3">
                <div className="text-right">
                  <div className="tabular text-[24px] font-semibold leading-none">
                    {score(selected.frictionScore)}
                  </div>
                  <div className="text-[11px] text-muted">indeks friksi</div>
                </div>
                <Link
                  href={`/destinasi/${selected.id}`}
                  className="rounded-md border px-3 py-1.5 text-[13px] font-medium text-ink transition-colors hover:bg-surface-2"
                  style={{ borderColor: "var(--hairline)" }}
                >
                  Buka rapor →
                </Link>
              </div>
            </div>
          </Card>
        ) : (
          <p className="mt-3 text-center text-[12px] text-muted">
            Klik titik pada peta untuk melihat ringkasan tempat.
          </p>
        )}
      </div>

      {/* -------------------------------------------------------- peringkat */}
      <div className="min-w-0">
        <Card className="p-4">
          <SectionTitle hint={`${num(ranked.length)} tempat`}>
            Prioritas Perbaikan
          </SectionTitle>
          <p className="mb-3 text-[12px] leading-relaxed text-muted">
            Urut menurut indeks friksi — besarnya kerugian yang terukur dari
            ulasan. Peringkat 1 = paling mendesak dibenahi.
          </p>
          {ranked.length === 0 ? (
            <Empty>Tidak ada tempat berperingkat yang lolos filter.</Empty>
          ) : (
            <ol className="thin-scroll max-h-[560px] space-y-1 overflow-y-auto pr-1">
              {ranked.map((p) => {
                const lvl = levelOf(p.frictionScore, p.confidence);
                return (
                  <li key={p.id}>
                    <Link
                      href={`/destinasi/${p.id}`}
                      className="flex items-center gap-3 rounded-md border px-2.5 py-2 transition-colors hover:bg-surface-2"
                      style={{ borderColor: "var(--hairline)" }}
                    >
                      <span className="tabular w-8 shrink-0 text-right text-[12px] text-muted">
                        #{p.rank}
                      </span>
                      <span aria-hidden className="shrink-0 text-[13px]" style={{ color: lvl.colorVar }}>
                        {lvl.icon}
                      </span>
                      <span className="min-w-0 flex-1">
                        <span className="block truncate text-[13px] font-medium text-ink">
                          {p.name}
                        </span>
                        <span className="block truncate text-[11px] text-muted">
                          {p.kabupaten}
                          {p.topAspects[0]
                            ? ` · ${ASPECT_LABEL[p.topAspects[0]]}`
                            : ""}
                        </span>
                      </span>
                      <span className="tabular shrink-0 text-[13px] font-semibold">
                        {score(p.frictionScore)}
                      </span>
                    </Link>
                  </li>
                );
              })}
            </ol>
          )}
        </Card>
        <div className="mt-3">
          <Note>
            Tempat dengan &lt; 20 ulasan berteks ditandai{" "}
            <span aria-hidden>○</span> dan dikeluarkan dari peringkat — sampel
            kecil tidak dihukum, tidak juga dipercaya berlebihan. Skor dihitung
            dengan baseline <em>keyword + rating</em>, bukan model IndoBERT
            terlatih.
          </Note>
        </div>
      </div>
    </div>
  );
}
