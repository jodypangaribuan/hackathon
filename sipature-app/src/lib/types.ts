/**
 * Tipe data SIPATURE — mencerminkan persis skema JSON di src/data/.
 * JSON dihasilkan oleh scripts/gen_seed.py dari dataset asli panitia.
 */

export type PlaceKind = "wisata" | "kuliner" | "akomodasi";
export type Confidence = "high" | "medium" | "low" | "none";
export type Trend = "naik" | "turun" | "stabil";

/** Kunci aspek yang dikenali model. `pemandangan` bukan aspek friksi. */
export type AspectKey =
  | "kebersihan"
  | "harga_pungli"
  | "toilet_sanitasi"
  | "parkir"
  | "akses_jalan"
  | "ramah_keluarga"
  | "halal_muslim"
  | "rumah_ibadah"
  | "jam_operasional"
  | "keamanan_sikap"
  | "pemandangan";

export interface Evidence {
  /** Kutipan verbatim review asli, dipotong di sekitar kata kunci aspek. */
  text: string;
  rating: number | null;
  monthsAgo: number | null;
}

export interface AspectRow {
  aspect: AspectKey;
  /** Jumlah review yang menyebut aspek ini. */
  nMention: number;
  /** Jumlah di antaranya yang bernada negatif (rating <= 3). */
  nNegative: number;
  negRateRaw: number;
  /** Wilson lower bound 95% — menghukum sampel kecil. Ini yang dipakai. */
  negRateWilson: number;
  /** mean(rating | aspek disebut) - mean(rating global). Negatif = menyeret rating. */
  severity: number;
  mentionRate: number;
  /** mentionRate x negRateWilson x |severity| */
  frictionContrib: number;
  trend: Trend;
  evidence: Evidence[];
  priorityRank: number;
}

export interface NearestPlace {
  km: number;
  name: string;
}

export interface TransportRoute {
  name: string;
  hours: string;
  price: string;
  via: string;
}

export interface InfraGap {
  nearestFood: NearestPlace | null;
  nearestHalalFood: NearestPlace | null;
  nearestLodging: NearestPlace | null;
  /** null = tidak terdata di sheet 'waktu operasional destinasi'. */
  hasToilet: boolean | null;
  publicTransport: TransportRoute[];
}

export interface Place {
  id: string;
  name: string;
  kind: PlaceKind;
  lat: number;
  lon: number;
  type: string;
  entryFee: string | null;
  hours: string | null;
  address: string | null;
  gmapsRating: number | null;
  status: string | null;
  facilities?: string | null;
  kabupaten: string;
  kecamatan: string | null;
  infraGap: InfraGap;
  /** Indeks mentah (0–0,35). Untuk tampilan pakai frictionScore. */
  frictionIndex: number;
  /** frictionIndex x 100 — skala 0–100 yang enak dibaca. */
  frictionScore: number;
  nReviewsText: number;
  confidence: Confidence;
  aspects: AspectRow[];
  topAspects: AspectKey[];
  /** null bila confidence low/none (tidak masuk peringkat publik). */
  rank: number | null;
}

export interface Opportunity {
  id: string;
  title: string;
  icon: string;
  category: string;
  aspect: AspectKey;
  aspectLabel: string;
  placeId: string;
  placeName: string;
  kabupaten: string;
  lat: number;
  lon: number;
  evidenceCount: number;
  mentionCount: number;
  negRate: number;
  why: string;
  gapKm: number | null;
  competitorNote: string;
  marketProxy: string;
  kabupatenVisits: number | null;
  budgetBand: string | null;
  investEstimate: string;
  score: number;
  evidence: string[];
  rank: number;
}

export interface KabupatenStat {
  name: string;
  visits: number;
  intl: number;
  /** Hanya baris Toba yang terisi di dataset panitia. */
  duration: number | null;
  budget: string;
}

export interface AspectMeta {
  key: AspectKey;
  label: string;
  icon: string;
}

export interface Corpus {
  totalReviews: number;
  reviewsWithText: number;
  placesGeocoded: number;
  globalMeanRating: number;
  ratingDistribution: Record<string, number>;
  severity: Record<string, number>;
  aspects: AspectMeta[];
  kabupaten: KabupatenStat[];
  generatedFrom: string;
  method: string;
  maxFrictionScore: number;
  rankedCount: number;
}

export interface LexiconEntry {
  label: string;
  icon: string;
  pattern: string;
  severity: number;
  isFriction: boolean;
}

export interface Lexicon {
  aspects: Record<string, LexiconEntry>;
  samples: string[];
}

/* ---------------------------------------------------------- tingkat friksi */

export type FrictionLevel = "none" | "rendah" | "sedang" | "serius" | "kritis";

export interface LevelSpec {
  key: FrictionLevel;
  /** Label teks — WAJIB ikut ditampilkan; warna tidak pernah sendirian. */
  label: string;
  icon: string;
  colorVar: string;
  min: number;
  max: number;
}

/* ------------------------------------------------------------ kontrak API */

export interface AnalyzeHit {
  aspect: AspectKey;
  label: string;
  icon: string;
  sentiment: "positif" | "negatif" | "netral";
  score: number;
  severity: number;
  isFriction: boolean;
  evidence: string[];
}

export interface AnalyzeResult {
  text: string;
  hits: AnalyzeHit[];
  latencyMs: number;
  /** true bila tidak ada satu pun kata kunci aspek yang cocok. */
  keywordBaselineWouldMiss: boolean;
  note: string;
}

export interface SimulateRequest {
  placeId: string;
  fixes: AspectKey[];
}

export interface SimulateResult {
  placeId: string;
  placeName: string;
  before: { score: number; rank: number | null };
  after: { score: number; rank: number | null };
  removed: { aspect: AspectKey; label: string; delta: number }[];
  caveat: string;
}
