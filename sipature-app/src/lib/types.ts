export type PlaceKind = "wisata" | "kuliner" | "akomodasi" | "layanan";
export type Confidence = "high" | "medium" | "low" | "insufficient";
export type Priority =
  "Critical" | "High" | "Medium" | "Monitor" | "Insufficient Data";
export type AspectKey =
  | "cleanliness"
  | "waste"
  | "sanitation"
  | "crowding"
  | "access"
  | "parking"
  | "public_facilities"
  | "scenery"
  | "comfort"
  | "safety"
  | "price_transparency"
  | "staff_service"
  | "maintenance"
  | "opening_hours";

export interface PriorityComponent {
  value: number | null;
  original_weight: number;
  effective_weight: number;
  contribution: number;
}

export interface Issue {
  aspect: AspectKey;
  mentionCount: number;
  negativeCount: number;
  textReviewCount: number;
  allReviewCount: number;
  smoothedComplaintRate: number;
  meanConfidence: number;
  dataConfidence: Confidence;
  priority: Priority;
  priorityScore: number | null;
  priorityComponents: Record<string, PriorityComponent>;
  explanation: string;
  recommendedVerification: string;
  candidateIntervention: string;
  severityStatus: "unavailable_no_supported_model";
  evidenceStatus: "withheld_pending_privacy_review";
}

export interface Place {
  id: string;
  legacyId: string | null;
  name: string;
  kind: PlaceKind;
  lat: number | null;
  lon: number | null;
  canonicalStatus: "metadata_anchor" | "unresolved_placeholder";
  type: string;
  entryFee: string | null;
  hours: string | null;
  address: string | null;
  gmapsRating: number | null;
  status: string | null;
  facilities: string | null;
  kabupaten: string;
  kecamatan: string | null;
  priority: Priority;
  priorityScore: number | null;
  healthScore: number | null;
  concernScore: number | null;
  dataConfidence: Confidence;
  textReviewCount: number;
  allReviewCount: number;
  issues: Issue[];
  topAspects: AspectKey[];
  rank: number | null;
}

export interface Intervention {
  id: string;
  placeId: string;
  placeName: string;
  kabupaten: string;
  aspect: AspectKey;
  aspectLabel: string;
  category: string;
  title: string;
  verification: string;
  explanation: string;
  mentionCount: number;
  negativeCount: number;
  smoothedComplaintRate: number;
  dataConfidence: Confidence;
  priority: Priority;
  priorityScore: number;
  evidenceStatus: "withheld_pending_privacy_review";
  rank: number;
}

export interface Corpus {
  schemaVersion: string;
  modelVersion: string;
  generatedAt: string;
  sourceManifest: string;
  exportSha256: string;
  taxonomyVersion: string;
  totalCleanReviews: number;
  textualReviewsAnalyzed: number;
  reviewsWithPredictions: number;
  aspectPredictions: number;
  canonicalDestinations: number;
  geocodedDestinations: number;
  unresolvedDestinations: number;
  destinationsWithSignals: number;
  actionableDestinations: number;
  actionableIssues: number;
  aspectModel: string;
  polarityModel: string;
  polarityProbabilityAvailable: false;
  severityStatus: "unavailable_no_supported_model";
  expertJudgmentsCompleted: number;
  evidenceStatus: "withheld_pending_privacy_review";
  limitations: string[];
  aspects: { key: AspectKey; label: string; group: string }[];
  method: string;
}

export type SignalLevel = "none" | "monitor" | "medium" | "high" | "critical";
export interface LevelSpec {
  key: SignalLevel;
  label: string;
  icon: string;
  colorVar: string;
}

export interface AnalyzeHit {
  aspect: AspectKey;
  label: string;
  sentiment: "positif" | "negatif" | "netral";
  matchScore: number;
  snippets: string[];
}
export interface AnalyzeResult {
  method: "lexical_demo_v1";
  modelVersion: null;
  text: string;
  hits: AnalyzeHit[];
  latencyMs: number;
  note: string;
}

export interface SimulateResult {
  placeId: string;
  placeName: string;
  before: {
    healthScore: number | null;
    priority: Priority;
    priorityScore: number | null;
  };
  after: {
    healthScore: number | null;
    priority: Priority;
    priorityScore: number | null;
  };
  removed: { aspect: AspectKey; label: string }[];
  caveat: string;
}
