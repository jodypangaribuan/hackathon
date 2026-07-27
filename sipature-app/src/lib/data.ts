/**
 * Loader data — HANYA dipakai di server component / route handler.
 * Client component menerima data lewat props supaya bundle tetap ramping.
 *
 * Semua data sudah PRECOMPUTED sejak tahap preliminary (lihat EKSEKUSI.md §19).
 * Aplikasi tidak menghitung ulang model saat halaman dibuka.
 */
import placesJson from "@/data/places.json";
import opportunitiesJson from "@/data/opportunities.json";
import corpusJson from "@/data/corpus.json";
import lexiconJson from "@/data/lexicon.json";

import type {
  Place,
  Opportunity,
  Corpus,
  Lexicon,
  AspectKey,
  PlaceKind,
  Confidence,
} from "./types";

export const places = placesJson as unknown as Place[];
export const opportunities = opportunitiesJson as unknown as Opportunity[];
export const corpus = corpusJson as unknown as Corpus;
export const lexicon = lexiconJson as unknown as Lexicon;

/** Tempat yang punya cukup data untuk masuk peringkat publik. */
export const rankedPlaces: Place[] = places
  .filter((p) => p.rank !== null)
  .sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0));

export function getPlace(id: string): Place | undefined {
  return places.find((p) => p.id === id);
}

export function getOpportunity(id: string): Opportunity | undefined {
  return opportunities.find((o) => o.id === id);
}

export function opportunitiesForPlace(placeId: string): Opportunity[] {
  return opportunities.filter((o) => o.placeId === placeId);
}

export const kabupatenList: string[] = Array.from(
  new Set(places.map((p) => p.kabupaten)),
).sort();

export const kindList: PlaceKind[] = ["wisata", "kuliner", "akomodasi"];

export const KIND_LABEL: Record<PlaceKind, string> = {
  wisata: "Destinasi Wisata",
  kuliner: "Kuliner",
  akomodasi: "Akomodasi",
};

export const KIND_SHORT: Record<PlaceKind, string> = {
  wisata: "Wisata",
  kuliner: "Kuliner",
  akomodasi: "Akomodasi",
};

export interface PlaceFilter {
  kabupaten?: string[];
  kind?: PlaceKind[];
  aspect?: AspectKey | null;
  confidence?: Confidence[];
  query?: string;
}

export function filterPlaces(all: Place[], f: PlaceFilter): Place[] {
  const q = (f.query ?? "").trim().toLowerCase();
  return all.filter((p) => {
    if (f.kabupaten?.length && !f.kabupaten.includes(p.kabupaten)) return false;
    if (f.kind?.length && !f.kind.includes(p.kind)) return false;
    if (f.confidence?.length && !f.confidence.includes(p.confidence)) return false;
    if (f.aspect) {
      const a = p.aspects.find((x) => x.aspect === f.aspect);
      if (!a || a.frictionContrib <= 0) return false;
    }
    if (q && !p.name.toLowerCase().includes(q) && !(p.address ?? "").toLowerCase().includes(q)) {
      return false;
    }
    return true;
  });
}

/** Ringkasan angka untuk stat tile di halaman utama. */
export function headlineStats() {
  const toba = corpus.kabupaten.find((k) => k.name === "Toba");
  return {
    duration: toba?.duration ?? null,
    visits: toba?.visits ?? null,
    intl: toba?.intl ?? null,
    reviews: corpus.totalReviews,
    reviewsWithText: corpus.reviewsWithText,
    placesGeocoded: corpus.placesGeocoded,
    ranked: corpus.rankedCount,
    noData: places.filter((p) => p.confidence === "none").length,
  };
}
