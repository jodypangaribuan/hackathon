import { desc } from "drizzle-orm";

import { db, schema } from "@/db";
import { ASPECT_LABEL } from "./format";
import type {
  AspectKey,
  Confidence,
  Corpus,
  Intervention,
  Issue,
  Place,
  PlaceKind,
  Priority,
  PriorityComponent,
} from "./types";

// ============================================================================
// Konstanta (pure, tidak bergantung DB)
// ============================================================================
export const kindList: PlaceKind[] = [
  "wisata",
  "kuliner",
  "akomodasi",
  "layanan",
];
export const KIND_LABEL: Record<PlaceKind, string> = {
  wisata: "Destinasi Wisata",
  kuliner: "Kuliner",
  akomodasi: "Akomodasi",
  layanan: "Layanan/Belum Terklasifikasi",
};
export const KIND_SHORT: Record<PlaceKind, string> = {
  wisata: "Wisata",
  kuliner: "Kuliner",
  akomodasi: "Akomodasi",
  layanan: "Layanan",
};

export interface PlaceFilter {
  kabupaten?: string[];
  kind?: PlaceKind[];
  aspect?: AspectKey | null;
  confidence?: Confidence[];
  query?: string;
}
export function filterPlaces(all: Place[], filter: PlaceFilter) {
  const query = (filter.query ?? "").trim().toLowerCase();
  return all.filter((place) => {
    if (filter.kabupaten?.length && !filter.kabupaten.includes(place.kabupaten))
      return false;
    if (filter.kind?.length && !filter.kind.includes(place.kind)) return false;
    if (
      filter.confidence?.length &&
      !filter.confidence.includes(place.dataConfidence)
    )
      return false;
    if (
      filter.aspect &&
      !place.issues.some(
        (issue) =>
          issue.aspect === filter.aspect &&
          issue.priority !== "Insufficient Data",
      )
    )
      return false;
    return (
      !query ||
      place.name.toLowerCase().includes(query) ||
      (place.address ?? "").toLowerCase().includes(query)
    );
  });
}

// ============================================================================
// Mapping DB → tipe aplikasi
// ============================================================================
const PRIORITY_RANK: Record<Priority, number> = {
  Critical: 0,
  High: 1,
  Medium: 2,
  Monitor: 3,
  "Insufficient Data": 4,
};

type DestRow = typeof schema.destinations.$inferSelect;
type SignalRow = typeof schema.destinationSignals.$inferSelect;
type AlertRow = typeof schema.alerts.$inferSelect;

function toIssue(
  signal: SignalRow,
  alert?: AlertRow,
  rejectionReason?: string | null,
  evidenceSnippets?: { text: string; probability: number; date?: string | null }[],
): Issue {
  return {
    aspect: signal.aspect as AspectKey,
    mentionCount: signal.mentionCount,
    negativeCount: signal.negativeCount,
    textReviewCount: signal.textReviewCount,
    allReviewCount: signal.allReviewCount,
    smoothedComplaintRate: signal.smoothedComplaintRate ?? 0,
    meanConfidence: signal.meanConfidence ?? 0,
    dataConfidence: signal.dataConfidence,
    priority: signal.priority,
    priorityScore: signal.priorityScore,
    priorityComponents:
      (signal.priorityComponents as Record<string, PriorityComponent>) ?? {},
    explanation: signal.explanation ?? "",
    recommendedVerification: signal.recommendedVerification ?? "",
    candidateIntervention: signal.candidateIntervention ?? "",
    severityStatus: signal.severityStatus,
    evidenceStatus: "published",
    verificationStatus: alert?.status ?? "pending",
    rejectionReason: rejectionReason ?? null,
    evidenceSnippets: evidenceSnippets ?? [],
  };
}

function compareIssues(a: Issue, b: Issue) {
  return (
    PRIORITY_RANK[a.priority] - PRIORITY_RANK[b.priority] ||
    (b.priorityScore ?? -1) - (a.priorityScore ?? -1) ||
    a.aspect.localeCompare(b.aspect)
  );
}

function toPlace(dest: DestRow, issues: Issue[]): Place {
  return {
    id: dest.id,
    legacyId: dest.legacyId,
    name: dest.name,
    kind: dest.kind,
    lat: dest.latitude,
    lon: dest.longitude,
    canonicalStatus: dest.canonicalStatus,
    type: dest.placeType ?? dest.kind,
    entryFee: dest.entryFee,
    hours: dest.operationalHours,
    address: dest.address,
    gmapsRating: dest.gmapsRating,
    status: dest.operationalStatus,
    facilities: dest.facilities,
    kabupaten: dest.kabupaten ?? "Belum terpetakan",
    kecamatan: dest.kecamatan,
    priority: dest.priority,
    priorityScore: dest.priorityScore,
    healthScore: dest.healthScore,
    concernScore: dest.concernScore,
    dataConfidence: dest.dataConfidence,
    textReviewCount: dest.textReviewCount,
    allReviewCount: dest.allReviewCount,
    issues,
    topAspects: issues
      .filter((issue) => issue.priority !== "Insufficient Data")
      .slice(0, 3)
      .map((issue) => issue.aspect),
    rank: dest.rank,
  };
}

// ============================================================================
// Query DB (live)
// ============================================================================
async function loadAll() {
  const [dests, signals, aspects, alertsList, verificationsList, allEvidence] = await Promise.all([
    db.select().from(schema.destinations),
    db.select().from(schema.destinationSignals),
    db.select().from(schema.aspects),
    db.select().from(schema.alerts),
    db.select().from(schema.alertVerifications).orderBy(desc(schema.alertVerifications.id)),
    db.select().from(schema.evidence),
  ]);

  const alertMap = new Map<string, AlertRow>();
  for (const alert of alertsList) {
    alertMap.set(`${alert.destinationId}--${alert.aspect}`, alert);
  }

  const lastRejectionMap = new Map<string, string>();
  for (const v of verificationsList) {
    if (v.rejectionReason && !lastRejectionMap.has(v.alertId)) {
      lastRejectionMap.set(v.alertId, v.rejectionReason);
    }
  }

  const evidenceMap = new Map<string, { text: string; probability: number; date?: string | null }[]>();
  for (const ev of allEvidence) {
    const key = `${ev.destinationId}--${ev.aspect}`;
    const list = evidenceMap.get(key) ?? [];
    list.push({
      text: ev.text,
      probability: ev.aspectProbability,
      date: ev.publishedDateEstimate,
    });
    evidenceMap.set(key, list);
  }

  const byDest = new Map<string, Issue[]>();
  for (const signal of signals) {
    const list = byDest.get(signal.destinationId) ?? [];
    const alert = alertMap.get(`${signal.destinationId}--${signal.aspect}`);
    const reason = alert ? lastRejectionMap.get(alert.id) : null;
    const snippets = evidenceMap.get(`${signal.destinationId}--${signal.aspect}`);
    list.push(toIssue(signal, alert, reason, snippets));
    byDest.set(signal.destinationId, list);
  }

  const places: Place[] = dests.map((dest) =>
    toPlace(
      dest,
      (byDest.get(dest.id) ?? []).sort(compareIssues),
    ),
  );

  const groupByAspect = new Map(aspects.map((a) => [a.key, a.aspectGroup]));
  return { places, signals, groupByAspect };
}

export async function getPlaces(): Promise<Place[]> {
  const { places } = await loadAll();
  return places;
}

export async function getRankedPlaces(): Promise<Place[]> {
  const places = await getPlaces();
  return places
    .filter((place) => place.rank !== null)
    .sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0));
}

export async function getMappablePlaces(): Promise<
  (Place & { lat: number; lon: number })[]
> {
  const places = await getPlaces();
  return places.filter(
    (place): place is Place & { lat: number; lon: number } =>
      place.lat !== null && place.lon !== null,
  );
}

export async function getPlace(id: string): Promise<Place | undefined> {
  const places = await getPlaces();
  return places.find((place) => place.id === id || place.legacyId === id);
}

export async function getCorpus(): Promise<Corpus> {
  const [row] = await db
    .select()
    .from(schema.dataExports)
    .orderBy(desc(schema.dataExports.id))
    .limit(1);
  if (!row) throw new Error("data_exports kosong — jalankan `npm run db:seed`");
  return row.corpusJson as unknown as Corpus;
}

export async function getInterventions(): Promise<Intervention[]> {
  const { places, signals, groupByAspect } = await loadAll();
  const placeById = new Map(places.map((p) => [p.id, p]));
  const items: Intervention[] = signals
    .filter((signal) => signal.priority !== "Insufficient Data")
    .map((signal): Intervention => {
      const place = placeById.get(signal.destinationId);
      return {
        id: `${signal.destinationId}--${signal.aspect}`,
        placeId: signal.destinationId,
        placeName: place?.name ?? signal.destinationId,
        kabupaten: place?.kabupaten ?? "Belum terpetakan",
        aspect: signal.aspect as AspectKey,
        aspectLabel: "",
        category: groupByAspect.get(signal.aspect) ?? "",
        title: signal.candidateIntervention ?? "",
        verification: signal.recommendedVerification ?? "",
        explanation: signal.explanation ?? "",
        mentionCount: signal.mentionCount,
        negativeCount: signal.negativeCount,
        smoothedComplaintRate: signal.smoothedComplaintRate ?? 0,
        dataConfidence: signal.dataConfidence,
        priority: signal.priority,
        priorityScore: signal.priorityScore ?? 0,
        evidenceStatus: "withheld_pending_privacy_review",
        rank: 0,
      };
    })
    .sort(
      (a, b) =>
        (b.priorityScore ?? -1) - (a.priorityScore ?? -1) ||
        a.id.localeCompare(b.id),
    );
  items.forEach((item, index) => {
    item.rank = index + 1;
    item.aspectLabel = aspectLabel(item.aspect);
  });
  return items;
}

export async function getInterventionsForPlace(
  placeId: string,
): Promise<Intervention[]> {
  const interventions = await getInterventions();
  return interventions.filter((item) => item.placeId === placeId);
}

export async function getKabupatenList(): Promise<string[]> {
  const places = await getMappablePlaces();
  return Array.from(new Set(places.map((place) => place.kabupaten))).sort();
}

export async function getHeadlineStats() {
  const corpus = await getCorpus();
  return {
    reviews: corpus.totalCleanReviews,
    reviewsWithText: corpus.textualReviewsAnalyzed,
    placesGeocoded: corpus.geocodedDestinations,
    canonicalPlaces: corpus.canonicalDestinations,
    ranked: corpus.actionableDestinations,
    actionableIssues: corpus.actionableIssues,
    noData: corpus.unresolvedDestinations,
  };
}

function aspectLabel(aspect: AspectKey): string {
  return ASPECT_LABEL[aspect] ?? aspect;
}
