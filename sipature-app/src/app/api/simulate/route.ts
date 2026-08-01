import { NextResponse } from "next/server";
import { getPlace } from "@/lib/data";
import { SIGNAL_ASPECTS } from "@/lib/format";
import { simulateFixes } from "@/lib/simulate";
import type { AspectKey } from "@/lib/types";
export async function POST(req: Request) {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json(
      { error: "Invalid JSON", code: "INVALID_JSON" },
      { status: 400 },
    );
  }
  if (!body || typeof body !== "object" || Array.isArray(body))
    return NextResponse.json(
      { error: "Invalid body", code: "INVALID_BODY" },
      { status: 400 },
    );
  const { placeId, fixes } = body as { placeId?: unknown; fixes?: unknown };
  if (
    typeof placeId !== "string" ||
    !Array.isArray(fixes) ||
    fixes.some(
      (item) =>
        typeof item !== "string" || !SIGNAL_ASPECTS.includes(item as AspectKey),
    )
  )
    return NextResponse.json(
      { error: "Invalid placeId or fixes", code: "INVALID_REQUEST" },
      { status: 400 },
    );
  const place = getPlace(placeId);
  if (!place)
    return NextResponse.json(
      { error: "Place not found", code: "PLACE_NOT_FOUND" },
      { status: 404 },
    );
  return NextResponse.json(simulateFixes(place, fixes as AspectKey[]));
}
