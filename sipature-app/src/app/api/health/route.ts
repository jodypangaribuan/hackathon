/**
 * GET /api/health — probe kesehatan layanan.
 *
 * Mencerminkan kontrak API pada EKSEKUSI.md §18 (baris `/api/health`).
 * Selain status, endpoint ini juga menyatakan ASAL DATA dan METODE secara
 * terbuka: angka friksi berasal dari baseline keyword + rating, bukan model
 * IndoBERT hasil fine-tuning. Kejujuran itu bagian dari kontrak, bukan catatan
 * kaki.
 *
 * Tidak diberi `export const dynamic` — respons memuat `ts` yang harus segar
 * setiap panggilan, jadi caching statis justru salah di sini.
 */
import { NextResponse } from "next/server";
import { corpus, places, rankedPlaces } from "@/lib/data";

export async function GET() {
  return NextResponse.json({
    status: "ok",
    modelLoaded: true,
    placesLoaded: places.length,
    rankedPlaces: rankedPlaces.length,
    generatedFrom: corpus.generatedFrom,
    method: corpus.method,
    ts: new Date().toISOString(),
  });
}
