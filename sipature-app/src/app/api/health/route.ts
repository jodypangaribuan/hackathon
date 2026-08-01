import { NextResponse } from "next/server";
import { corpus, places, rankedPlaces } from "@/lib/data";
export async function GET() {
  return NextResponse.json({
    status: "ok",
    mode: "precomputed_batch",
    modelVersion: corpus.modelVersion,
    generatedAt: corpus.generatedAt,
    placesLoaded: places.length,
    actionableDestinations: rankedPlaces.length,
    evidenceStatus: corpus.evidenceStatus,
    expertJudgmentsCompleted: corpus.expertJudgmentsCompleted,
    ts: new Date().toISOString(),
  });
}
