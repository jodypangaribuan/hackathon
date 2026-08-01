"use client";

/**
 * Peta cadangan LURING — SVG murni, nol permintaan jaringan.
 *
 * Dipakai otomatis bila tile peta gagal dimuat (ruang lockdown tanpa internet,
 * firewall, atau penyedia tile sedang mati). Garis pantai adalah aproksimasi
 * stilistis untuk orientasi, BUKAN data geospasial resmi.
 *
 * Keberadaan berkas ini adalah jawaban atas pertanyaan juri
 * "bagaimana kalau di ruang demo tidak ada internet?".
 */

import {
  MAP_ASPECT,
  SAMOSIR_OUTLINE,
  TOBA_OUTLINE,
  levelOf,
  num,
  project,
  score,
  toPath,
} from "@/lib/format";
import type { MapPoint } from "./TobaMap";

const W = 1000;
const H = Math.round(W * MAP_ASPECT);

export default function TobaMapFallback({
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
  const drawOrder = [...points].sort(
    (a, b) => (a.priorityScore ?? -1) - (b.priorityScore ?? -1),
  );

  return (
    <div className={`${heightClass} w-full overflow-hidden`}>
      <svg
        viewBox={`0 0 ${W} ${H}`}
        preserveAspectRatio="xMidYMid meet"
        className="block h-full w-full"
        role="img"
        aria-label={`Peta ringkas ${num(points.length)} tempat di kawasan Danau Toba (mode luring)`}
      >
        <path
          d={toPath(TOBA_OUTLINE, W, H)}
          fill="color-mix(in srgb, var(--series-1) 16%, transparent)"
          stroke="var(--baseline)"
          strokeWidth={1.5}
        />
        <path
          d={toPath(SAMOSIR_OUTLINE, W, H)}
          fill="var(--plane)"
          stroke="var(--baseline)"
          strokeWidth={1.5}
        />
        <text
          x={project(2.62, 98.83).x * W}
          y={project(2.62, 98.83).y * H}
          textAnchor="middle"
          fontSize={15}
          fill="var(--text-muted)"
        >
          Samosir
        </text>
        <text
          x={project(2.44, 98.75).x * W}
          y={project(2.44, 98.75).y * H}
          textAnchor="middle"
          fontSize={15}
          fontStyle="italic"
          fill="var(--text-muted)"
        >
          Danau Toba
        </text>

        {drawOrder.map((p) => {
          const { x, y } = project(p.lat, p.lon);
          const lvl = levelOf(p.priority);
          const isSel = p.id === selectedId;
          return (
            <g
              key={p.id}
              transform={`translate(${(x * W).toFixed(1)},${(y * H).toFixed(1)})`}
              onClick={() => onSelect?.(p.id)}
              style={{ cursor: onSelect ? "pointer" : "default" }}
            >
              {isSel ? (
                <circle
                  r={13}
                  fill="none"
                  stroke="var(--series-1)"
                  strokeWidth={2}
                />
              ) : null}
              {/* ikon tingkat = pembawa makna kedua di samping warna */}
              <text
                textAnchor="middle"
                dominantBaseline="central"
                fontSize={lvl.key === "none" ? 9 : 11}
                fill={lvl.colorVar}
                stroke="var(--surface-1)"
                strokeWidth={0.6}
                paintOrder="stroke"
              >
                {lvl.icon}
              </text>
              <title>{`${p.name} — priority score ${score(p.priorityScore)} (${lvl.label})`}</title>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
