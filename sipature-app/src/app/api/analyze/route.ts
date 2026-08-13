/**
 * POST /api/analyze — satu-satunya inferensi live di aplikasi ini.
 *
 * Mencerminkan kontrak API pada EKSEKUSI.md §18 (baris `/api/analyze`):
 * `{text}` → aspek + sentimen + skor + evidence + latency.
 *
 * Bila service inference (FastAPI, lihat `INFERENCE_URL`) tersedia, request
 * diteruskan ke model produksi TF-IDF. Jika tidak tersedia / gagal, fallback
 * ke baseline leksikon + isyarat sentimen (`@/lib/absa-sim`). Mode aktual
 * dikirim lewat field `mode` di setiap respons.
 *
 * Semua yang lain di aplikasi ini precomputed (EKSEKUSI.md §19).
 */
import { NextResponse } from "next/server";
import { analyzeText } from "@/lib/absa-sim";
import { analyzeWithModel } from "@/lib/inference";

const MAX_CHARS = 5000;
const INFERENCE_URL = process.env.INFERENCE_URL;
const INFERENCE_TIMEOUT_MS = 5000;

function badRequest(message: string, code: string) {
  return NextResponse.json({ error: message, code }, { status: 400 });
}

export async function POST(req: Request) {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return badRequest(
      'Body permintaan bukan JSON yang valid. Kirim { "text": "…" }.',
      "INVALID_JSON",
    );
  }

  if (typeof body !== "object" || body === null || Array.isArray(body)) {
    return badRequest(
      'Body harus berupa objek JSON { "text": "…" }.',
      "INVALID_BODY",
    );
  }

  const { text } = body as { text?: unknown };

  if (typeof text !== "string") {
    return badRequest(
      "Field `text` wajib ada dan harus berupa string.",
      "TEXT_REQUIRED",
    );
  }

  if (text.trim().length < 1) {
    return badRequest("Field `text` tidak boleh kosong.", "TEXT_EMPTY");
  }

  if (text.length > MAX_CHARS) {
    return badRequest(
      `Field \`text\` maksimal ${MAX_CHARS} karakter, diterima ${text.length}.`,
      "TEXT_TOO_LONG",
    );
  }

  if (INFERENCE_URL) {
    try {
      const controller = new AbortController();
      const timer = setTimeout(
        () => controller.abort(),
        INFERENCE_TIMEOUT_MS,
      );
      const result = await analyzeWithModel(text, INFERENCE_URL, controller.signal);
      clearTimeout(timer);
      return NextResponse.json(result, {
        headers: { "Cache-Control": "no-store" },
      });
    } catch {
      // Jatuh ke sandbox leksikal di bawah; mode tercermin pada field `mode`.
    }
  }

  return NextResponse.json(analyzeText(text), {
    headers: { "Cache-Control": "no-store" },
  });
}
