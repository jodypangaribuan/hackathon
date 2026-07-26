/**
 * GET /api/opportunities — peluang UMKM, terurut potensi.
 *
 * Mencerminkan kontrak API pada EKSEKUSI.md §18 (baris `/api/opportunities`).
 * Query yang didukung:
 *   ?kabupaten=  daftar, boleh diulang atau dipisah koma
 *   ?category=   daftar kategori peluang (mis. `Lingkungan`, `Fasilitas`)
 *   ?limit=      1..1000
 *
 * Peluang diturunkan dari keluhan yang terbukti ada di ulasan asli; skornya
 * memakai baseline yang sama dengan indeks friksi, bukan model terlatih.
 */
import { NextResponse } from "next/server";
import { corpus, opportunities } from "@/lib/data";

const KABUPATEN_VALUES = Array.from(
  new Set(opportunities.map((o) => o.kabupaten)),
).sort();

const CATEGORY_VALUES = Array.from(
  new Set(opportunities.map((o) => o.category)),
).sort();

function badRequest(message: string, code: string) {
  return NextResponse.json({ error: message, code }, { status: 400 });
}

function listParam(sp: URLSearchParams, key: string): string[] {
  return sp
    .getAll(key)
    .flatMap((v) => v.split(","))
    .map((v) => v.trim())
    .filter((v) => v.length > 0);
}

function canonical(value: string, allowed: readonly string[]): string | null {
  const lower = value.toLowerCase();
  return allowed.find((a) => a.toLowerCase() === lower) ?? null;
}

export async function GET(req: Request) {
  const sp = new URL(req.url).searchParams;

  const kabupaten: string[] = [];
  for (const raw of listParam(sp, "kabupaten")) {
    const hit = canonical(raw, KABUPATEN_VALUES);
    if (!hit) {
      return badRequest(
        `Kabupaten "${raw}" tidak punya peluang terdata. Pilihan: ${KABUPATEN_VALUES.join(", ")}.`,
        "UNKNOWN_KABUPATEN",
      );
    }
    kabupaten.push(hit);
  }

  const category: string[] = [];
  for (const raw of listParam(sp, "category")) {
    const hit = canonical(raw, CATEGORY_VALUES);
    if (!hit) {
      return badRequest(
        `Kategori "${raw}" tidak dikenal. Pilihan: ${CATEGORY_VALUES.join(", ")}.`,
        "UNKNOWN_CATEGORY",
      );
    }
    category.push(hit);
  }

  const rawLimit = sp.get("limit");
  let limit: number | null = null;
  if (rawLimit !== null && rawLimit.trim() !== "") {
    const n = Number(rawLimit);
    if (!Number.isInteger(n) || n < 1 || n > 1000) {
      return badRequest("Parameter limit harus bilangan bulat 1–1000.", "INVALID_LIMIT");
    }
    limit = n;
  }

  const matched = opportunities
    .filter((o) => {
      if (kabupaten.length && !kabupaten.includes(o.kabupaten)) return false;
      if (category.length && !category.includes(o.category)) return false;
      return true;
    })
    .sort((a, b) => a.rank - b.rank);

  const items = limit === null ? matched : matched.slice(0, limit);

  return NextResponse.json({
    count: items.length,
    total: matched.length,
    method: corpus.method,
    items,
  });
}
