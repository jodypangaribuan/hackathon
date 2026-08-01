import { NextResponse } from "next/server";
import { corpus, interventions } from "@/lib/data";
export async function GET(req: Request) {
  const params = new URL(req.url).searchParams;
  const category = params.get("category");
  const kabupaten = params.get("kabupaten");
  const items = interventions.filter(
    (item) =>
      (!category || item.category === category) &&
      (!kabupaten || item.kabupaten === kabupaten),
  );
  return NextResponse.json({
    count: items.length,
    modelVersion: corpus.modelVersion,
    semantics: "candidate_intervention_pending_field_verification",
    items,
  });
}
