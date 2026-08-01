/**
 * GET /api/places/[id] — rapor lengkap satu tempat.
 *
 * Mencerminkan kontrak API pada EKSEKUSI.md §18 (baris `/api/places/{id}`):
 * detail + array aspek + evidence + tren + gap infrastruktur. Objek Place
 * dikembalikan apa adanya karena skema JSON seed sudah persis kontrak itu.
 *
 * Catatan Next.js 15: pada route dinamis, `params` adalah Promise.
 * Tidak diberi `export const dynamic` — route dinamis tanpa
 * generateStaticParams dihitung per permintaan.
 */
import { NextResponse } from "next/server";
import { getPlace, interventionsForPlace } from "@/lib/data";

export async function GET(
  _req: Request,
  ctx: { params: Promise<{ id: string }> },
) {
  const { id } = await ctx.params;
  const place = getPlace(id);

  if (!place) {
    return NextResponse.json(
      {
        error: `Tempat dengan id "${id}" tidak ditemukan.`,
        code: "PLACE_NOT_FOUND",
      },
      { status: 404 },
    );
  }

  return NextResponse.json({
    ...place,
    // Tautan silang ke Layar 3; kosong bila tempat ini tidak menghasilkan peluang.
    interventionIds: interventionsForPlace(place.id).map((item) => item.id),
  });
}
