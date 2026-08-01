import type { AnalyzeHit, AnalyzeResult, AspectKey } from "./types";
import { ASPECT_LABEL } from "./format";

const PATTERNS: Record<AspectKey, RegExp> = {
  cleanliness: /bersih|kotor|jorok|kumuh|bau/gi,
  waste: /sampah|limbah|plastik|berserakan|tempat sampah/gi,
  sanitation: /toilet|wc\b|kamar mandi|mck|sanitasi|air mati/gi,
  crowding: /ramai|padat|sesak|antre|antri|berdesakan/gi,
  access: /akses|jalan|berlubang|terjal|berbatu|petunjuk arah/gi,
  parking: /parkir|parkiran|lahan parkir/gi,
  public_facilities:
    /fasilitas|gazebo|tempat duduk|penerangan|mushola|masjid|gereja|difabel|kursi roda/gi,
  scenery: /pemandangan|panorama|view|indah|cantik|sunrise|sunset|asri/gi,
  comfort: /nyaman|panas|sejuk|bising|tenang|pengap/gi,
  safety: /aman|bahaya|rawan|licin|preman|maling|copet/gi,
  price_transparency:
    /harga|tarif|tiket|pungli|pungutan|mahal|biaya|retribusi|karcis/gi,
  staff_service: /pelayanan|petugas|staf|staff|ramah|kasar|lambat|responsif/gi,
  maintenance: /terawat|perawatan|rusak|usang|terbengkalai/gi,
  opening_hours:
    /jam buka|jam operasional|tutup|belum buka|masih tutup|24 jam/gi,
};
const NEGATIVE =
  /\b(tidak|gak|kurang|buruk|jelek|kotor|mahal|rusak|kecewa|parah|bahaya|tutup|lama)\b/gi;
const POSITIVE =
  /\b(bagus|bersih|indah|ramah|murah|nyaman|puas|keren|terawat|aman|baik)\b/gi;

export function analyzeText(text: string): AnalyzeResult {
  const start = typeof performance !== "undefined" ? performance.now() : 0;
  const clean = text.replace(/\s+/g, " ").trim();
  const hits: AnalyzeHit[] = [];
  for (const [aspect, pattern] of Object.entries(PATTERNS) as [
    AspectKey,
    RegExp,
  ][]) {
    const matches = [...clean.matchAll(new RegExp(pattern.source, "gi"))].slice(
      0,
      4,
    );
    if (!matches.length) continue;
    const negative = (clean.match(NEGATIVE) ?? []).length;
    const positive = (clean.match(POSITIVE) ?? []).length;
    const sentiment =
      negative > positive
        ? "negatif"
        : positive > negative
          ? "positif"
          : "netral";
    hits.push({
      aspect,
      label: ASPECT_LABEL[aspect],
      sentiment,
      matchScore: Math.min(1, 0.4 + matches.length * 0.15),
      snippets: matches.slice(0, 2).map((match) => {
        const at = match.index ?? 0;
        return clean.slice(
          Math.max(0, at - 45),
          Math.min(clean.length, at + match[0].length + 55),
        );
      }),
    });
  }
  return {
    mode: "baseline",
    method: "lexical_demo_v1",
    modelVersion: null,
    scoreType: "lexical_match",
    text: clean,
    hits,
    latencyMs: Math.max(
      1,
      Math.round(
        ((typeof performance !== "undefined" ? performance.now() : 0) - start) *
          100,
      ) / 100,
    ),
    note: "Sandbox leksikal deterministik, bukan model intelligence utama. Input tidak disimpan dan hasil tidak mengubah prioritas destinasi.",
  };
}
