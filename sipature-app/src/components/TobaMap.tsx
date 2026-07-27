"use client";

/**
 * Pembungkus peta. Memilih antara peta sungguhan (Leaflet + tile gratis) dan
 * peta cadangan luring (SVG), lalu memasang pemilih basemap dan legenda.
 *
 * Leaflet dimuat lewat next/dynamic ssr:false karena modulnya menyentuh
 * `window` saat dievaluasi.
 */

import dynamic from "next/dynamic";
import { useState } from "react";
import type { AspectKey, Confidence, PlaceKind } from "@/lib/types";
import { LEVELS, num } from "@/lib/format";
import { TriangleAlert } from "lucide-react";
import TobaMapFallback from "./TobaMapFallback";

/** Versi ramping satu tempat — cukup untuk peta. */
export interface MapPoint {
  id: string;
  name: string;
  kind: PlaceKind;
  lat: number;
  lon: number;
  kabupaten: string;
  frictionScore: number;
  confidence: Confidence;
  topAspects: AspectKey[];
  nReviewsText: number;
  rank: number | null;
}

export type Basemap = "auto" | "terang" | "gelap" | "satelit";

const LeafletMap = dynamic(() => import("./LeafletMap"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full w-full items-center justify-center text-[12px] text-muted">
      Memuat peta…
    </div>
  ),
});

const BASEMAPS: { key: Basemap; label: string }[] = [
  { key: "auto", label: "Peta" },
  { key: "satelit", label: "Satelit" },
];

export default function TobaMap({
  points,
  selectedId,
  onSelect,
  heightClass = "h-[520px]",
}: {
  points: MapPoint[];
  selectedId?: string | null;
  onSelect?: (id: string) => void;
  heightClass?: string;
}) {
  const [basemap, setBasemap] = useState<Basemap>("auto");
  const [offline, setOffline] = useState(false);

  return (
    <div>
      {/* kendali basemap */}
      <div
        className="flex flex-wrap items-center gap-2 border-b px-3 py-2"
        style={{ borderColor: "var(--hairline)" }}
      >
        <div
          className="inline-flex overflow-hidden rounded-md border"
          style={{ borderColor: "var(--hairline)" }}
          role="group"
          aria-label="Pilih jenis peta dasar"
        >
          {BASEMAPS.map((b) => {
            const active = basemap === b.key;
            return (
              <button
                key={b.key}
                onClick={() => setBasemap(b.key)}
                disabled={offline}
                aria-pressed={active}
                className="px-2.5 py-1 text-[12px] transition-colors disabled:cursor-not-allowed disabled:opacity-40"
                style={{
                  background: active ? "var(--surface-2)" : "transparent",
                  color: active ? "var(--text-primary)" : "var(--text-secondary)",
                  fontWeight: active ? 600 : 400,
                }}
              >
                {b.label}
              </button>
            );
          })}
        </div>

        {offline ? (
          <span
            className="inline-flex items-center gap-1.5 rounded-md border px-2 py-1 text-[11px]"
            style={{ borderColor: "var(--hairline)", color: "var(--text-secondary)" }}
          >
             <TriangleAlert size={13} style={{ color: "var(--status-warning)" }} />
            Mode luring — tile peta tidak dapat dimuat, beralih ke peta ringkas
          </span>
        ) : null}

        <button
          onClick={() => setOffline((v) => !v)}
          className="ml-auto rounded-md border px-2 py-1 text-[11px] text-muted transition-colors hover:text-ink-2"
          style={{ borderColor: "var(--hairline)" }}
          title="Peta ringkas tidak memerlukan koneksi internet sama sekali. Tombol ini untuk menguji kesiapan demo luring."
        >
          {offline ? "Coba peta daring" : "Uji mode luring"}
        </button>
      </div>

      {/* peta */}
      <div className={`${heightClass} w-full`}>
        {offline ? (
          <TobaMapFallback
            points={points}
            selectedId={selectedId}
            onSelect={onSelect}
            heightClass="h-full"
          />
        ) : (
          <LeafletMap
            points={points}
            selectedId={selectedId}
            onSelect={onSelect}
            basemap={basemap}
            onTileFailure={() => setOffline(true)}
          />
        )}
      </div>

      {/* legenda — ikon + label WAJIB menyertai warna */}
      <div
        className="flex flex-wrap items-center gap-x-4 gap-y-1 border-t px-3 py-2"
        style={{ borderColor: "var(--hairline)" }}
      >
        {LEVELS.map((l) => (
          <span key={l.key} className="inline-flex items-center gap-1.5 text-[11px] text-ink-2">
            <span aria-hidden style={{ color: l.colorVar }}>
              {l.icon}
            </span>
            {l.label}
            {l.key === "kritis" ? (
              <span className="tabular text-muted">≥ {l.min}</span>
            ) : l.key !== "none" ? (
              <span className="tabular text-muted">
                {l.min}–{l.max}
              </span>
            ) : null}
          </span>
        ))}
        <span className="ml-auto text-[11px] text-muted">
          Ukuran titik = jumlah ulasan · {num(points.length)} tempat
        </span>
      </div>
    </div>
  );
}
