/**
 * GET /api/places — daftar ringkas tempat, dengan filter.
 *
 * Mencerminkan kontrak API pada EKSEKUSI.md §18 (baris `/api/places`).
 * Query yang didukung:
 *   ?kabupaten=  daftar, boleh diulang atau dipisah koma (mis. `Toba,Samosir`)
 *   ?kind=       wisata | kuliner | akomodasi (boleh banyak)
 *   ?aspect=     satu kunci aspek; hanya tempat dengan kontribusi friksi > 0
 *   ?confidence= high | medium | low | none (boleh banyak)
 *   ?q=          pencarian nama/alamat
 *   ?limit=      1..1000
 *
 * Tidak diberi `export const dynamic = "force-static"`: respons bergantung
 * pada query param, sehingga harus dihitung per permintaan.
 */
import { NextResponse } from "next/server";
import {
  corpus,
  filterPlaces,
  kabupatenList,
  kindList,
  places,
} from "@/lib/data";
import { ASPECT_LABEL } from "@/lib/format";
import type { AspectKey, Confidence, Place, PlaceKind } from "@/lib/types";

const CONFIDENCE_VALUES: Confidence[] = ["high", "medium", "low", "none"];
const ASPECT_VALUES = Object.keys(ASPECT_LABEL) as AspectKey[];

function badRequest(message: string, code: string) {
  return NextResponse.json({ error: message, code }, { status: 400 });
}

/** Ambil parameter daftar: boleh diulang (`?kind=a&kind=b`) atau koma. */
function listParam(sp: URLSearchParams, key: string): string[] {
  return sp
    .getAll(key)
    .flatMap((v) => v.split(","))
    .map((v) => v.trim())
    .filter((v) => v.length > 0);
}

/** Cocokkan nilai ke daftar kanonik tanpa peduli besar-kecil huruf. */
function canonical<T extends string>(value: string, allowed: readonly T[]): T | null {
  const lower = value.toLowerCase();
  return allowed.find((a) => a.toLowerCase() === lower) ?? null;
}

/** Bentuk ringkas untuk peta dan tabel — bukan objek Place penuh. */
function summarize(p: Place) {
  return {
    id: p.id,
    name: p.name,
    kabupaten: p.kabupaten,
    kind: p.kind,
    lat: p.lat,
    lon: p.lon,
    frictionScore: p.frictionScore,
    rank: p.rank,
    confidence: p.confidence,
    nReviewsText: p.nReviewsText,
    topAspects: p.topAspects,
  };
}

/** Berperingkat lebih dulu (rank menaik), sisanya menurut skor menurun. */
function byRankThenScore(a: Place, b: Place): number {
  if (a.rank !== null && b.rank !== null) return a.rank - b.rank;
  if (a.rank !== null) return -1;
  if (b.rank !== null) return 1;
  return b.frictionScore - a.frictionScore || a.name.localeCompare(b.name, "id");
}

export async function GET(req: Request) {
  const sp = new URL(req.url).searchParams;

  const kabupaten: string[] = [];
  for (const raw of listParam(sp, "kabupaten")) {
    const hit = canonical(raw, kabupatenList);
    if (!hit) {
      return badRequest(
        `Kabupaten "${raw}" tidak dikenal. Pilihan: ${kabupatenList.join(", ")}.`,
        "UNKNOWN_KABUPATEN",
      );
    }
    kabupaten.push(hit);
  }

  const kind: PlaceKind[] = [];
  for (const raw of listParam(sp, "kind")) {
    const hit = canonical(raw, kindList);
    if (!hit) {
      return badRequest(
        `Jenis "${raw}" tidak dikenal. Pilihan: ${kindList.join(", ")}.`,
        "UNKNOWN_KIND",
      );
    }
    kind.push(hit);
  }

  const confidence: Confidence[] = [];
  for (const raw of listParam(sp, "confidence")) {
    const hit = canonical(raw, CONFIDENCE_VALUES);
    if (!hit) {
      return badRequest(
        `Tingkat kepercayaan "${raw}" tidak dikenal. Pilihan: ${CONFIDENCE_VALUES.join(", ")}.`,
        "UNKNOWN_CONFIDENCE",
      );
    }
    confidence.push(hit);
  }

  const rawAspect = sp.get("aspect")?.trim();
  let aspect: AspectKey | null = null;
  if (rawAspect) {
    aspect = canonical(rawAspect, ASPECT_VALUES);
    if (!aspect) {
      return badRequest(
        `Aspek "${rawAspect}" tidak dikenal. Pilihan: ${ASPECT_VALUES.join(", ")}.`,
        "UNKNOWN_ASPECT",
      );
    }
  }

  const rawLimit = sp.get("limit");
  let limit: number | null = null;
  if (rawLimit !== null && rawLimit.trim() !== "") {
    const n = Number(rawLimit);
    if (!Number.isInteger(n) || n < 1 || n > 1000) {
      return badRequest(
        "Parameter limit harus bilangan bulat 1–1000.",
        "INVALID_LIMIT",
      );
    }
    limit = n;
  }

  const matched = filterPlaces(places, {
    kabupaten,
    kind,
    confidence,
    aspect,
    query: sp.get("q") ?? undefined,
  }).sort(byRankThenScore);

  const items = (limit === null ? matched : matched.slice(0, limit)).map(summarize);

  return NextResponse.json({
    count: items.length,
    total: matched.length,
    // Disebut sekali di sini supaya konsumen API tahu asal angkanya.
    method: corpus.method,
    items,
  });
}
