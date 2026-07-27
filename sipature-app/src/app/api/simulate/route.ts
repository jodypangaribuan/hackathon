/**
 * POST /api/simulate — kontrak API pada EKSEKUSI.md §18 (baris `/api/simulate`):
 * `{ placeId, fixes[] }` → indeks & peringkat baru.
 *
 * Matematikanya identik dengan yang dipakai UI (lib/simulate.ts); endpoint ini
 * ada supaya kontrak API lengkap dan bisa diuji lewat curl tanpa browser.
 */
import { NextResponse } from "next/server";
import { getPlace, rankedPlaces } from "@/lib/data";
import { FRICTION_ASPECTS } from "@/lib/format";
import { buildRankLadder, simulateFixes } from "@/lib/simulate";
import type { AspectKey } from "@/lib/types";

function badRequest(message: string, code: string) {
  return NextResponse.json({ error: message, code }, { status: 400 });
}

export async function POST(req: Request) {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return badRequest(
      'Body permintaan bukan JSON yang valid. Kirim { "placeId": "…", "fixes": [] }.',
      "INVALID_JSON",
    );
  }

  if (typeof body !== "object" || body === null || Array.isArray(body)) {
    return badRequest(
      'Body harus berupa objek JSON { "placeId": "…", "fixes": [] }.',
      "INVALID_BODY",
    );
  }

  const { placeId, fixes } = body as { placeId?: unknown; fixes?: unknown };

  if (typeof placeId !== "string" || placeId.length === 0) {
    return badRequest("Field `placeId` wajib berupa string.", "INVALID_PLACE_ID");
  }
  if (!Array.isArray(fixes) || fixes.some((f) => typeof f !== "string")) {
    return badRequest("Field `fixes` wajib berupa array string aspek.", "INVALID_FIXES");
  }

  const unknown = (fixes as string[]).filter(
    (f) => !FRICTION_ASPECTS.includes(f as AspectKey),
  );
  if (unknown.length > 0) {
    return badRequest(
      `Aspek tidak dikenal: ${unknown.join(", ")}. Aspek valid: ${FRICTION_ASPECTS.join(", ")}.`,
      "UNKNOWN_ASPECT",
    );
  }

  const place = getPlace(placeId);
  if (!place) {
    return NextResponse.json(
      { error: `Tempat dengan id "${placeId}" tidak ditemukan.`, code: "PLACE_NOT_FOUND" },
      { status: 404 },
    );
  }

  const ladder = buildRankLadder(rankedPlaces.map((p) => p.frictionScore));
  return NextResponse.json(simulateFixes(place, fixes as AspectKey[], ladder));
}
