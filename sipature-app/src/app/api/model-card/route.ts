import { NextResponse } from "next/server";

import { getCorpus } from "@/lib/data";

export async function GET() {
  const corpus = await getCorpus();
  return NextResponse.json({
    modelVersion: corpus.modelVersion,
    aspectModel: corpus.aspectModel,
    polarityModel: corpus.polarityModel,
    polarityProbabilityAvailable: corpus.polarityProbabilityAvailable,
    severityStatus: corpus.severityStatus,
    taxonomyVersion: corpus.taxonomyVersion,
    evidenceStatus: corpus.evidenceStatus,
    expertJudgmentsCompleted: corpus.expertJudgmentsCompleted,
    generatedAt: corpus.generatedAt,
    method: corpus.method,
    limitations: corpus.limitations,
    aspects: corpus.aspects,
  });
}
