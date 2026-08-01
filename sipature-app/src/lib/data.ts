import placesJson from "@/data/generated/a9-places.json";
import interventionsJson from "@/data/generated/a9-interventions.json";
import corpusJson from "@/data/generated/a9-corpus.json";
import type {
  AspectKey,
  Confidence,
  Corpus,
  Intervention,
  Place,
  PlaceKind,
} from "./types";

export const places = placesJson as Place[];
export const interventions = interventionsJson as Intervention[];
export const corpus = corpusJson as Corpus;
export const rankedPlaces = places
  .filter((place) => place.rank !== null)
  .sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0));
export const mappablePlaces = places.filter(
  (place): place is Place & { lat: number; lon: number } =>
    place.lat !== null && place.lon !== null,
);

export function getPlace(id: string) {
  return places.find((place) => place.id === id || place.legacyId === id);
}
export function interventionsForPlace(placeId: string) {
  return interventions.filter((item) => item.placeId === placeId);
}

export const kabupatenList = Array.from(
  new Set(mappablePlaces.map((place) => place.kabupaten)),
).sort();
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

export function headlineStats() {
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
