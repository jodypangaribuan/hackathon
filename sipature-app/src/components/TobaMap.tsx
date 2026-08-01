"use client";
import dynamic from "next/dynamic";
import { useState } from "react";
import type { AspectKey, Confidence, PlaceKind, Priority } from "@/lib/types";
import { LEVELS, num } from "@/lib/format";
import { TriangleAlert } from "lucide-react";
import TobaMapFallback from "./TobaMapFallback";

export interface MapPoint {
  id: string;
  name: string;
  kind: PlaceKind;
  lat: number;
  lon: number;
  kabupaten: string;
  priority: Priority;
  priorityScore: number | null;
  dataConfidence: Confidence;
  topAspects: AspectKey[];
  textReviewCount: number;
  allReviewCount: number;
  rank: number | null;
}
export type Basemap = "auto" | "terang" | "gelap" | "satelit";
const LeafletMap = dynamic(() => import("./LeafletMap"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full items-center justify-center text-[12px] text-muted">
      Memuat peta…
    </div>
  ),
});

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
      <div
        className="flex flex-wrap items-center gap-2 border-b px-3 py-2"
        style={{ borderColor: "var(--hairline)" }}
      >
        <div
          className="inline-flex overflow-hidden rounded-md border"
          style={{ borderColor: "var(--hairline)" }}
        >
          {(
            [
              ["auto", "Peta"],
              ["satelit", "Satelit"],
            ] as const
          ).map(([key, label]) => (
            <button
              key={key}
              onClick={() => setBasemap(key)}
              disabled={offline}
              className="px-2.5 py-1 text-[12px]"
              style={{
                background:
                  basemap === key ? "var(--surface-2)" : "transparent",
              }}
            >
              {label}
            </button>
          ))}
        </div>
        {offline ? (
          <span className="inline-flex items-center gap-1.5 text-[11px] text-muted">
            <TriangleAlert size={13} />
            Mode luring
          </span>
        ) : null}
        <button
          onClick={() => setOffline((value) => !value)}
          className="ml-auto rounded-md border px-2 py-1 text-[11px] text-muted"
          style={{ borderColor: "var(--hairline)" }}
        >
          {offline ? "Coba peta daring" : "Uji mode luring"}
        </button>
      </div>
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
      <div
        className="flex flex-wrap items-center gap-x-4 gap-y-1 border-t px-3 py-2"
        style={{ borderColor: "var(--hairline)" }}
      >
        {LEVELS.map((level) => (
          <span
            key={level.key}
            className="inline-flex items-center gap-1.5 text-[11px] text-ink-2"
          >
            <span style={{ color: level.colorVar }}>{level.icon}</span>
            {level.label}
          </span>
        ))}
        <span className="ml-auto text-[11px] text-muted">
          Ukuran titik = jumlah review bersih · {num(points.length)} tempat
          berkoordinat
        </span>
      </div>
    </div>
  );
}
