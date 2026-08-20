import type {
  AspectKey,
  Confidence,
  LevelSpec,
  Place,
  Priority,
} from "./types";

export const LEVELS: LevelSpec[] = [
  {
    key: "none",
    label: "Data Belum Cukup",
    icon: "○",
    colorVar: "var(--text-muted)",
  },
  {
    key: "monitor",
    label: "Kondisi Terjaga",
    icon: "●",
    colorVar: "var(--status-good)",
  },
  {
    key: "medium",
    label: "Perlu Perhatian",
    icon: "▲",
    colorVar: "var(--status-warning)",
  },
  {
    key: "high",
    label: "Perlu Tindakan",
    icon: "◆",
    colorVar: "var(--status-serious)",
  },
  {
    key: "critical",
    label: "Mendesak (Kritis)",
    icon: "■",
    colorVar: "var(--status-critical)",
  },
];
const LEVEL_BY_PRIORITY: Record<Priority, LevelSpec> = {
  "Insufficient Data": LEVELS[0],
  Monitor: LEVELS[1],
  Medium: LEVELS[2],
  High: LEVELS[3],
  Critical: LEVELS[4],
};
export function levelOf(priority: Priority) {
  return LEVEL_BY_PRIORITY[priority];
}
export function levelOfPlace(place: Place) {
  return levelOf(place.priority);
}

export const CONFIDENCE_LABEL: Record<Confidence, string> = {
  high: "Bukti Ulasan Kuat",
  medium: "Bukti Ulasan Cukup",
  low: "Bukti Ulasan Terbatas",
  insufficient: "Ulasan Belum Cukup",
};
export const ASPECT_LABEL: Record<AspectKey, string> = {
  cleanliness: "Kebersihan",
  waste: "Sampah & Limbah",
  sanitation: "Toilet & Sanitasi",
  crowding: "Kepadatan & Antrean",
  access: "Akses & Kondisi Rute",
  parking: "Parkir",
  public_facilities: "Fasilitas Publik & Aksesibilitas",
  scenery: "Pemandangan",
  comfort: "Kenyamanan",
  safety: "Keselamatan & Keamanan",
  price_transparency: "Harga & Transparansi Pungutan",
  staff_service: "Pelayanan Petugas",
  maintenance: "Perawatan & Kerusakan",
  opening_hours: "Jam Operasional",
};
export const SIGNAL_ASPECTS = Object.keys(ASPECT_LABEL) as AspectKey[];
export const CONFIDENCE_TONE = (confidence: Confidence) =>
  confidence === "high" || confidence === "medium" ? "strong" : "weak";

export const MAP_BBOX = {
  minLat: 1.95,
  maxLat: 3.2,
  minLon: 98.1,
  maxLon: 99.4,
};
export function project(lat: number, lon: number) {
  return {
    x: (lon - MAP_BBOX.minLon) / (MAP_BBOX.maxLon - MAP_BBOX.minLon),
    y: (MAP_BBOX.maxLat - lat) / (MAP_BBOX.maxLat - MAP_BBOX.minLat),
  };
}
export const MAP_ASPECT =
  (MAP_BBOX.maxLat - MAP_BBOX.minLat) /
  ((MAP_BBOX.maxLon - MAP_BBOX.minLon) * Math.cos((2.55 * Math.PI) / 180));
export const TOBA_OUTLINE: [number, number][] = [
  [98.52, 2.9],
  [98.5, 2.8],
  [98.55, 2.7],
  [98.62, 2.6],
  [98.7, 2.5],
  [98.78, 2.42],
  [98.88, 2.36],
  [98.98, 2.33],
  [99.06, 2.34],
  [99.12, 2.4],
  [99.14, 2.5],
  [99.1, 2.6],
  [99.05, 2.68],
  [98.98, 2.75],
  [98.9, 2.82],
  [98.8, 2.88],
  [98.68, 2.92],
  [98.58, 2.93],
];
export const SAMOSIR_OUTLINE: [number, number][] = [
  [98.72, 2.72],
  [98.8, 2.78],
  [98.9, 2.74],
  [98.95, 2.64],
  [98.92, 2.54],
  [98.85, 2.48],
  [98.76, 2.52],
  [98.7, 2.62],
];
export function toPath(
  points: [number, number][],
  width: number,
  height: number,
) {
  return (
    points
      .map(([lon, lat], index) => {
        const { x, y } = project(lat, lon);
        return `${index === 0 ? "M" : "L"}${(x * width).toFixed(1)},${(y * height).toFixed(1)}`;
      })
      .join(" ") + " Z"
  );
}

const idNum = new Intl.NumberFormat("id-ID");
export function num(value: number | null | undefined) {
  return value == null ? "–" : idNum.format(value);
}
export function pct(value: number, digits = 0) {
  return `${(value * 100).toFixed(digits).replace(".", ",")}%`;
}
export function score(value: number | null, scale = 100) {
  return value == null ? "–" : (value * scale).toFixed(1).replace(".", ",");
}
export function dateTime(value: string) {
  return new Intl.DateTimeFormat("id-ID", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "Asia/Jakarta",
  }).format(new Date(value));
}
