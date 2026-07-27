/**
 * Helper tampilan bersama: tingkat friksi, proyeksi peta, formatter.
 * Dipakai oleh server maupun client component.
 */
import type {
  AspectKey,
  Confidence,
  FrictionLevel,
  LevelSpec,
  Place,
  Trend,
} from "./types";

/* ------------------------------------------------------- tingkat friksi */

/**
 * Friksi adalah *state* (good → critical), bukan identitas, sehingga memakai
 * STATUS PALETTE — bukan gradasi pelangi merah-kuning-hijau.
 * Aturan wajib: warna status TIDAK PERNAH sendirian. Selalu sertakan
 * `label` dan `icon` di setiap tempat warna ini dipakai.
 *
 * Ambang batas diturunkan dari distribusi nyata 127 tempat berperingkat:
 * p50=0,5 · p75=2,0 · p90=4,1 · p95=6,0 · p100=35,0
 */
export const LEVELS: LevelSpec[] = [
  { key: "none",   label: "Data tidak cukup", icon: "○", colorVar: "var(--text-muted)",       min: -1,  max: 0 },
  { key: "rendah", label: "Rendah",           icon: "●", colorVar: "var(--status-good)",      min: 0,   max: 1 },
  { key: "sedang", label: "Sedang",           icon: "▲", colorVar: "var(--status-warning)",   min: 1,   max: 3 },
  { key: "serius", label: "Serius",           icon: "◆", colorVar: "var(--status-serious)",   min: 3,   max: 8 },
  { key: "kritis", label: "Kritis",           icon: "■", colorVar: "var(--status-critical)",  min: 8,   max: Infinity },
];

export const LEVEL_BY_KEY: Record<FrictionLevel, LevelSpec> = LEVELS.reduce(
  (acc, l) => ({ ...acc, [l.key]: l }),
  {} as Record<FrictionLevel, LevelSpec>,
);

/** Tempat tanpa cukup review selalu 'none', berapa pun skornya. */
export function levelOf(score: number, confidence: Confidence): LevelSpec {
  if (confidence === "none" || confidence === "low") return LEVEL_BY_KEY.none;
  const hit = LEVELS.find((l) => l.key !== "none" && score >= l.min && score < l.max);
  return hit ?? LEVEL_BY_KEY.rendah;
}

export function levelOfPlace(p: Place): LevelSpec {
  return levelOf(p.frictionScore, p.confidence);
}

export const CONFIDENCE_LABEL: Record<Confidence, string> = {
  high: "Kepercayaan tinggi",
  medium: "Kepercayaan sedang",
  low: "Kepercayaan rendah",
  none: "Tanpa review",
};

/* --------------------------------------------------------- proyeksi peta */

/** Kotak batas yang memuat seluruh 320 titik dataset. */
export const MAP_BBOX = { minLat: 1.95, maxLat: 3.2, minLon: 98.1, maxLon: 99.4 };

/** Equirectangular sederhana → koordinat 0..1. Cukup untuk area sekecil ini. */
export function project(lat: number, lon: number): { x: number; y: number } {
  const { minLat, maxLat, minLon, maxLon } = MAP_BBOX;
  return {
    x: (lon - minLon) / (maxLon - minLon),
    y: (maxLat - lat) / (maxLat - minLat),
  };
}

/** Rasio tinggi:lebar yang benar untuk bbox ini (koreksi cos lintang). */
export const MAP_ASPECT =
  (MAP_BBOX.maxLat - MAP_BBOX.minLat) /
  ((MAP_BBOX.maxLon - MAP_BBOX.minLon) * Math.cos((2.55 * Math.PI) / 180));

/**
 * Garis pantai Danau Toba — APROKSIMASI stilistis untuk orientasi visual,
 * bukan data geospasial resmi. Format [lon, lat].
 */
export const TOBA_OUTLINE: [number, number][] = [
  [98.52, 2.9], [98.5, 2.8], [98.55, 2.7], [98.62, 2.6], [98.7, 2.5],
  [98.78, 2.42], [98.88, 2.36], [98.98, 2.33], [99.06, 2.34], [99.12, 2.4],
  [99.14, 2.5], [99.1, 2.6], [99.05, 2.68], [98.98, 2.75], [98.9, 2.82],
  [98.8, 2.88], [98.68, 2.92], [98.58, 2.93],
];

/** Pulau Samosir — aproksimasi. */
export const SAMOSIR_OUTLINE: [number, number][] = [
  [98.72, 2.72], [98.8, 2.78], [98.9, 2.74], [98.95, 2.64],
  [98.92, 2.54], [98.85, 2.48], [98.76, 2.52], [98.7, 2.62],
];

export function toPath(points: [number, number][], w: number, h: number): string {
  return (
    points
      .map(([lon, lat], i) => {
        const { x, y } = project(lat, lon);
        return `${i === 0 ? "M" : "L"}${(x * w).toFixed(1)},${(y * h).toFixed(1)}`;
      })
      .join(" ") + " Z"
  );
}

/* ------------------------------------------------------------ formatter */

const idNum = new Intl.NumberFormat("id-ID");

export function num(n: number | null | undefined): string {
  return n === null || n === undefined ? "–" : idNum.format(n);
}

export function pct(v: number, digits = 0): string {
  return `${(v * 100).toFixed(digits)}%`;
}

export function km(v: number | null | undefined): string {
  if (v === null || v === undefined) return "–";
  return v < 1 ? `${Math.round(v * 1000)} m` : `${v.toFixed(1)} km`;
}

export function score(v: number): string {
  return v.toFixed(1);
}

/** Severity ditampilkan sebagai dampak bintang: -1.205 → "−1,21★" */
export function severityLabel(sev: number): string {
  const s = sev.toFixed(2).replace(".", ",");
  return `${sev < 0 ? "−" : "+"}${s.replace("-", "")}★`;
}

export function monthsAgoLabel(m: number | null): string {
  if (m === null) return "waktu tidak diketahui";
  if (m <= 0) return "< 1 bulan lalu";
  if (m < 12) return `${m} bulan lalu`;
  const y = Math.round(m / 12);
  return y <= 1 ? "1 tahun lalu" : `${y} tahun lalu`;
}

export const TREND_META: Record<Trend, { icon: string; label: string; tone: string }> = {
  naik:   { icon: "▲", label: "Keluhan meningkat", tone: "var(--status-critical)" },
  turun:  { icon: "▼", label: "Keluhan menurun",   tone: "var(--success-text)" },
  stabil: { icon: "—", label: "Stabil",            tone: "var(--text-muted)" },
};

export const ASPECT_LABEL: Record<AspectKey, string> = {
  kebersihan: "Kebersihan",
  harga_pungli: "Harga & Pungutan",
  toilet_sanitasi: "Toilet & Sanitasi",
  parkir: "Parkir",
  akses_jalan: "Akses Jalan",
  ramah_keluarga: "Ramah Keluarga & Lansia",
  halal_muslim: "Halal & Muslim-Friendly",
  rumah_ibadah: "Rumah Ibadah",
  jam_operasional: "Jam Operasional",
  keamanan_sikap: "Keamanan & Sikap Warga",
  pemandangan: "Pemandangan",
};

export const FRICTION_ASPECTS: AspectKey[] = (
  Object.keys(ASPECT_LABEL) as AspectKey[]
).filter((k) => k !== "pemandangan");
