import { createHash } from "node:crypto";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const appRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const workspace = resolve(appRoot, "..");
const sourcePath = resolve(
  process.argv[2] ??
    join(workspace, "ml/artifacts/a9/20260801-a9-tfidf-lexical-v1-r5/export/app-export.json"),
);
const expectedHash = "f349a499afe04cdb9fafde8101e136470a41ca53815bd0c829dd62f07ca812b0";
const outputDir = join(appRoot, "src/data/generated");

const raw = await readFile(sourcePath);
const actualHash = createHash("sha256").update(raw).digest("hex");
if (actualHash !== expectedHash) throw new Error(`A9 export hash mismatch: ${actualHash}`);

const source = JSON.parse(raw.toString("utf8"));
const legacy = JSON.parse(
  await readFile(join(appRoot, "src/data/metadata-enrichment.json"), "utf8"),
);
const summary = JSON.parse(
  await readFile(
    join(workspace, "docs/evidence/a9/20260801-a9-tfidf-lexical-v1-r5/summary.json"),
    "utf8",
  ),
);

const aspects = {
  cleanliness: ["Kebersihan", "environmental"],
  waste: ["Sampah & Limbah", "environmental"],
  sanitation: ["Toilet & Sanitasi", "environmental"],
  crowding: ["Kepadatan & Antrean", "environmental"],
  access: ["Akses & Kondisi Rute", "infrastructure"],
  parking: ["Parkir", "infrastructure"],
  public_facilities: ["Fasilitas Publik & Aksesibilitas", "infrastructure"],
  scenery: ["Pemandangan", "visitor_experience"],
  comfort: ["Kenyamanan", "visitor_experience"],
  safety: ["Keselamatan & Keamanan", "visitor_experience"],
  price_transparency: ["Harga & Transparansi Pungutan", "visitor_experience"],
  staff_service: ["Pelayanan Petugas", "operations"],
  maintenance: ["Perawatan & Kerusakan", "operations"],
  opening_hours: ["Jam Operasional", "operations"],
};
const expectedAspects = new Set(Object.keys(aspects));

function normalizeName(value) {
  return value.normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase()
    .replace(/[^a-z0-9]+/g, " ").trim();
}

function distanceKm(a, b) {
  if (a.latitude == null || a.longitude == null) return Infinity;
  const rad = Math.PI / 180;
  const dLat = (a.latitude - b.lat) * rad;
  const dLon = (a.longitude - b.lon) * rad;
  const x = Math.sin(dLat / 2) ** 2 +
    Math.cos(a.latitude * rad) * Math.cos(b.lat * rad) * Math.sin(dLon / 2) ** 2;
  return 6371 * 2 * Math.atan2(Math.sqrt(x), Math.sqrt(1 - x));
}

const legacyByName = new Map();
for (const item of legacy) {
  const key = normalizeName(item.name);
  legacyByName.set(key, [...(legacyByName.get(key) ?? []), item]);
}

function enrich(destination) {
  const candidates = legacyByName.get(normalizeName(destination.name)) ?? [];
  if (!candidates.length) return null;
  const ordered = [...candidates].sort((a, b) => distanceKm(destination, a) - distanceKm(destination, b));
  const match = ordered[0];
  if (ordered.length > 1 && distanceKm(destination, ordered[0]) === distanceKm(destination, ordered[1])) {
    return null;
  }
  return match;
}

function kind(value) {
  return value === "resto" ? "kuliner" : value === "hotel" ? "akomodasi" :
    value === "wisata" ? "wisata" : "layanan";
}

function priorityRank(value) {
  return { Critical: 0, High: 1, Medium: 2, Monitor: 3, "Insufficient Data": 4 }[value];
}

if (source.schema_version !== "1.0.0" || source.model_version !== "a9-tfidf-lexical-v1.0.4") {
  throw new Error("Unsupported A9 schema or model version");
}
if (source.destinations.length !== 388) throw new Error("Expected 388 destinations");

const ids = new Set();
let issueCount = 0;
let actionableIssueCount = 0;
const places = source.destinations.map((destination) => {
  if (ids.has(destination.destination_id)) throw new Error("Duplicate canonical destination ID");
  ids.add(destination.destination_id);
  const metadata = enrich(destination);
  const issues = destination.issues.map((issue) => {
    if (!expectedAspects.has(issue.aspect)) throw new Error(`Unknown aspect ${issue.aspect}`);
    if (issue.negative_count > issue.mention_count || issue.text_review_count > issue.all_review_count) {
      throw new Error(`Invalid issue counts for ${destination.destination_id}/${issue.aspect}`);
    }
    if (issue.severe_count !== null || issue.severity_status !== "unavailable_no_supported_model") {
      throw new Error("Unsupported severity value present");
    }
    issueCount += 1;
    if (issue.priority !== "Insufficient Data") actionableIssueCount += 1;
    return {
      aspect: issue.aspect,
      mentionCount: issue.mention_count,
      negativeCount: issue.negative_count,
      textReviewCount: issue.text_review_count,
      allReviewCount: issue.all_review_count,
      smoothedComplaintRate: issue.smoothed_complaint_rate,
      meanConfidence: issue.mean_confidence,
      dataConfidence: issue.data_confidence,
      priority: issue.priority,
      priorityScore: issue.priority_score,
      priorityComponents: issue.priority_components,
      explanation: issue.explanation,
      recommendedVerification: issue.recommended_verification,
      candidateIntervention: issue.candidate_intervention,
      severityStatus: issue.severity_status,
      evidenceStatus: "withheld_pending_privacy_review",
    };
  }).sort((a, b) => priorityRank(a.priority) - priorityRank(b.priority) ||
    (b.priorityScore ?? -1) - (a.priorityScore ?? -1) || a.aspect.localeCompare(b.aspect));

  const textReviewCount = Math.max(0, ...issues.map((issue) => issue.textReviewCount));
  const allReviewCount = Math.max(0, ...issues.map((issue) => issue.allReviewCount));
  return {
    id: destination.destination_id,
    legacyId: metadata?.id ?? null,
    name: destination.name,
    kind: kind(destination.kind),
    lat: destination.latitude,
    lon: destination.longitude,
    canonicalStatus: destination.latitude == null ? "unresolved_placeholder" : "metadata_anchor",
    type: metadata?.type ?? destination.kind,
    entryFee: metadata?.entryFee ?? null,
    hours: metadata?.hours ?? null,
    address: metadata?.address ?? null,
    gmapsRating: metadata?.gmapsRating ?? null,
    status: metadata?.status ?? null,
    facilities: metadata?.facilities ?? null,
    kabupaten: metadata?.kabupaten ?? "Belum terpetakan",
    kecamatan: metadata?.kecamatan ?? null,
    priority: destination.priority,
    priorityScore: destination.priority_score,
    healthScore: destination.health_score,
    concernScore: destination.health_score == null ? null : 100 - destination.health_score,
    dataConfidence: destination.data_confidence,
    textReviewCount,
    allReviewCount,
    issues,
    topAspects: issues.filter((issue) => issue.priority !== "Insufficient Data").slice(0, 3).map((issue) => issue.aspect),
    rank: null,
  };
});

const actionable = places.filter((place) => place.priority !== "Insufficient Data")
  .sort((a, b) => (b.priorityScore ?? -1) - (a.priorityScore ?? -1) || a.id.localeCompare(b.id));
actionable.forEach((place, index) => { place.rank = index + 1; });

const interventions = actionable.flatMap((place) => place.issues
  .filter((issue) => issue.priority !== "Insufficient Data")
  .map((issue) => ({
    id: `${place.id}--${issue.aspect}`,
    placeId: place.id,
    placeName: place.name,
    kabupaten: place.kabupaten,
    aspect: issue.aspect,
    aspectLabel: aspects[issue.aspect][0],
    category: aspects[issue.aspect][1],
    title: issue.candidateIntervention,
    verification: issue.recommendedVerification,
    explanation: issue.explanation,
    mentionCount: issue.mentionCount,
    negativeCount: issue.negativeCount,
    smoothedComplaintRate: issue.smoothedComplaintRate,
    dataConfidence: issue.dataConfidence,
    priority: issue.priority,
    priorityScore: issue.priorityScore,
    evidenceStatus: issue.evidenceStatus,
    rank: 0,
  })))
  .sort((a, b) => (b.priorityScore ?? -1) - (a.priorityScore ?? -1) || a.id.localeCompare(b.id));
interventions.forEach((item, index) => { item.rank = index + 1; });

const mappable = places.filter((place) => place.lat != null && place.lon != null);
if (mappable.length !== 322 || actionable.length !== 103 || actionableIssueCount !== 210 || issueCount !== 1121) {
  throw new Error(`A9 count gate failed: ${mappable.length}/${actionable.length}/${actionableIssueCount}/${issueCount}`);
}
if (places.some((place) => place.canonicalStatus === "unresolved_placeholder" && place.priority !== "Insufficient Data")) {
  throw new Error("Unresolved destination received operational priority");
}

const corpus = {
  schemaVersion: source.schema_version,
  modelVersion: source.model_version,
  generatedAt: source.generated_at,
  sourceManifest: source.source_manifest,
  exportSha256: actualHash,
  taxonomyVersion: "1.0.0-rc1",
  totalCleanReviews: 22169,
  textualReviewsAnalyzed: summary.inference.text_reviews,
  reviewsWithPredictions: summary.inference.reviews_with_predictions,
  aspectPredictions: summary.inference.aspect_predictions,
  canonicalDestinations: places.length,
  geocodedDestinations: mappable.length,
  unresolvedDestinations: places.length - mappable.length,
  destinationsWithSignals: summary.aggregation.destinations_with_signals,
  actionableDestinations: actionable.length,
  actionableIssues: actionableIssueCount,
  aspectModel: summary.models.aspect,
  polarityModel: summary.models.polarity,
  polarityProbabilityAvailable: false,
  severityStatus: summary.models.severity_status,
  expertJudgmentsCompleted: summary.expert_review.judgments_completed,
  evidenceStatus: "withheld_pending_privacy_review",
  limitations: source.limitations,
  aspects: Object.entries(aspects).map(([key, [label, group]]) => ({ key, label, group })),
  method: "TF-IDF multilabel aspect + lexical polarity fallback + Bayesian smoothing + missing-aware priority",
};

const forbiddenKeys = /^(text|review_text|review_id|reviewer|profile|source_file|source_row|evidence|url|email|phone)$/i;
function assertPublic(value, path = "root") {
  if (Array.isArray(value)) return value.forEach((item, index) => assertPublic(item, `${path}[${index}]`));
  if (value && typeof value === "object") {
    for (const [key, child] of Object.entries(value)) {
      if (forbiddenKeys.test(key)) throw new Error(`Forbidden public key: ${path}.${key}`);
      assertPublic(child, `${path}.${key}`);
    }
  }
}
assertPublic(places);
assertPublic(interventions);

await mkdir(outputDir, { recursive: true });
await Promise.all([
  writeFile(join(outputDir, "a9-places.json"), `${JSON.stringify(places, null, 2)}\n`),
  writeFile(join(outputDir, "a9-interventions.json"), `${JSON.stringify(interventions, null, 2)}\n`),
  writeFile(join(outputDir, "a9-corpus.json"), `${JSON.stringify(corpus, null, 2)}\n`),
]);
console.log(`Generated A9 app data: ${places.length} destinations, ${interventions.length} interventions`);
