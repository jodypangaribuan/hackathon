import { NextResponse } from "next/server";
import { getCorpus, getPlaces, getRankedPlaces } from "@/lib/data";
export async function GET() {
  const [corpus, places, rankedPlaces] = await Promise.all([
    getCorpus(),
    getPlaces(),
    getRankedPlaces(),
  ]);
  return NextResponse.json({
    status: "ok",
    mode: "database",
    modelVersion: corpus.modelVersion,
    generatedAt: corpus.generatedAt,
    placesLoaded: places.length,
    actionableDestinations: rankedPlaces.length,
    evidenceStatus: corpus.evidenceStatus,
    expertJudgmentsCompleted: corpus.expertJudgmentsCompleted,
    ts: new Date().toISOString(),
  });
}
