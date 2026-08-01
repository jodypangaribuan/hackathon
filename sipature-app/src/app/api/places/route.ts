import { NextResponse } from "next/server";
import { corpus, filterPlaces, places } from "@/lib/data";
import { SIGNAL_ASPECTS } from "@/lib/format";
import type { AspectKey, Confidence, PlaceKind } from "@/lib/types";
export async function GET(req: Request) {
  const params = new URL(req.url).searchParams;
  const aspect = params.get("aspect");
  if (aspect && !SIGNAL_ASPECTS.includes(aspect as AspectKey))
    return NextResponse.json(
      { error: "Unknown aspect", code: "UNKNOWN_ASPECT" },
      { status: 400 },
    );
  const matched = filterPlaces(places, {
    kabupaten: params.get("kabupaten") ? [params.get("kabupaten")!] : undefined,
    kind: params.get("kind") ? [params.get("kind") as PlaceKind] : undefined,
    confidence: params.get("confidence")
      ? [params.get("confidence") as Confidence]
      : undefined,
    aspect: aspect as AspectKey | null,
    query: params.get("q") ?? undefined,
  }).sort(
    (a, b) =>
      (a.rank === null ? 1 : 0) - (b.rank === null ? 1 : 0) ||
      (a.rank ?? 0) - (b.rank ?? 0),
  );
  const limit = Math.min(
    1000,
    Math.max(
      1,
      Number(params.get("limit") ?? matched.length) || matched.length,
    ),
  );
  return NextResponse.json({
    count: Math.min(limit, matched.length),
    total: matched.length,
    modelVersion: corpus.modelVersion,
    generatedAt: corpus.generatedAt,
    items: matched.slice(0, limit).map((place) => ({
      id: place.id,
      name: place.name,
      kind: place.kind,
      latitude: place.lat,
      longitude: place.lon,
      kabupaten: place.kabupaten,
      priority: place.priority,
      priorityScore: place.priorityScore,
      dataConfidence: place.dataConfidence,
      rank: place.rank,
      topAspects: place.topAspects,
    })),
  });
}
