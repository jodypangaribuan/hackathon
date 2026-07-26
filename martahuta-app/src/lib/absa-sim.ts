/**
 * Simulasi inferensi ABSA untuk Live Analyzer.
 *
 * ⚠ INI BUKAN MODEL TERLATIH. Ini baseline leksikon + isyarat sentimen yang
 * berdiri sebagai pengganti IndoBERT sampai model preliminary selesai.
 * Layar Analyzer WAJIB menyatakan ini secara terbuka kepada penonton demo.
 *
 * Fungsi murni — tidak mengimpor data besar, aman dipakai di client maupun
 * di route handler.
 */
import type { AnalyzeHit, AnalyzeResult, AspectKey } from "./types";
import { ASPECT_ICON, ASPECT_LABEL, FRICTION_ASPECTS } from "./format";

/** Pola per aspek — identik dengan yang dipakai generator data seed. */
const PATTERNS: Record<AspectKey, RegExp> = {
  kebersihan: /sampah|kotor|jorok|bau busuk|bau\b|bersih|kebersihan|kumuh/gi,
  harga_pungli:
    /pungli|pungutan|dipalak|malak|mahal|retribusi|karcis|bayar lagi|serba bayar|semua bayar|harga tiket|htm\b/gi,
  toilet_sanitasi: /toilet|wc\b|kamar mandi|sanitasi|air mati|mck\b/gi,
  parkir: /parkir|parkiran/gi,
  akses_jalan:
    /jalan rusak|jalanan rusak|akses jalan|berlubang|jalan sempit|jalan berbatu|akses menuju|jalan menuju/gi,
  ramah_keluarga: /anak|balita|lansia|orang tua|stroller|difabel|kursi roda|keluarga/gi,
  halal_muslim: /halal|muslim|babi|b2\b|bpk\b|saksang|non ?halal/gi,
  rumah_ibadah: /mushola|musholla|masjid|sholat|shalat|gereja|tempat ibadah/gi,
  jam_operasional:
    /sudah tutup|udah tutup|tutup jam|jam buka|belum buka|masih tutup|tutup lebih awal/gi,
  keamanan_sikap:
    /preman|tidak aman|gak aman|dimarahi|di marahi|marah|maling|copet|kehilangan|galak|kasar/gi,
  pemandangan:
    /pemandangan|view\b|indah|cantik|bagus banget|panorama|sunset|sunrise|asri|sejuk/gi,
};

/** Severity global dari korpus (mean rating saat aspek disebut − mean global). */
const SEVERITY: Record<AspectKey, number> = {
  keamanan_sikap: -2.543,
  harga_pungli: -1.205,
  jam_operasional: -0.841,
  toilet_sanitasi: -0.564,
  parkir: -0.295,
  kebersihan: -0.272,
  akses_jalan: -0.21,
  halal_muslim: -0.063,
  ramah_keluarga: -0.038,
  rumah_ibadah: 0.07,
  pemandangan: 0.185,
};

const NEG_CUES =
  /\b(tidak|tdk|gak|ga|nggak|enggak|kurang|buruk|jelek|kotor|jorok|mahal|rusak|mati|kecewa|sayang|parah|bau|pesing|pungli|malak|marah|dimarahi|preman|hancur|sempit|berlubang|monoton|minim|susah|sulit|antri|lama|panas|ribet|licin|bahaya|dilarang|tutup|naik \d+x|kapok|jangan)\b/gi;

const POS_CUES =
  /\b(bagus|bersih|indah|cantik|ramah|murah|nyaman|memuaskan|puas|worth|rekomen|rekomended|keren|enak|sejuk|asri|terawat|lengkap|luas|mantap|oke|ok|baik|sopan|gratis|terjangkau|adem|tenang)\b/gi;

const NEGATORS = /\b(tidak|tdk|gak|ga|nggak|enggak|belum|kurang|jangan)\b/gi;

/** Kata yang membuktikan model menangkap makna tanpa kata kunci eksplisit. */
const IMPLICIT_MARKERS = [
  "bayar lagi",
  "serba bayar",
  "semua bayar",
  "air mati",
  "tidak ada air",
  "naik 10x",
];

function countMatches(re: RegExp, s: string): number {
  re.lastIndex = 0;
  return (s.match(re) ?? []).length;
}

/** Ambil jendela ±70 karakter di sekitar posisi kecocokan. */
function windowAt(text: string, at: number, len: number): string {
  const start = Math.max(0, at - 70);
  const end = Math.min(text.length, at + len + 70);
  return text.slice(start, end);
}

function spanAt(text: string, at: number, len: number): string {
  const start = Math.max(0, at - 22);
  const end = Math.min(text.length, at + len + 30);
  return (
    (start > 0 ? "…" : "") + text.slice(start, end).trim() + (end < text.length ? "…" : "")
  );
}

export function analyzeText(text: string): AnalyzeResult {
  const t0 =
    typeof performance !== "undefined" && performance.now ? performance.now() : 0;

  const clean = text.replace(/\s+/g, " ").trim();
  const hits: AnalyzeHit[] = [];

  if (clean.length > 0) {
    for (const key of Object.keys(PATTERNS) as AspectKey[]) {
      const re = new RegExp(PATTERNS[key].source, "gi");
      const spans: { at: number; len: number }[] = [];
      let m: RegExpExecArray | null;
      while ((m = re.exec(clean)) !== null) {
        spans.push({ at: m.index, len: m[0].length });
        if (m.index === re.lastIndex) re.lastIndex++;
        if (spans.length >= 6) break;
      }
      if (spans.length === 0) continue;

      // Sentimen dinilai dari jendela di sekitar tiap kecocokan.
      let neg = 0;
      let pos = 0;
      for (const s of spans) {
        const w = windowAt(clean, s.at, s.len);
        const n = countMatches(NEG_CUES, w);
        const p = countMatches(POS_CUES, w);
        const negated = countMatches(NEGATORS, w);
        // "tidak bersih" → isyarat positif dibalik menjadi negatif
        if (negated > 0 && p > 0) {
          neg += Math.min(p, negated);
          pos += Math.max(0, p - negated);
        } else {
          pos += p;
        }
        neg += n;
      }

      const total = neg + pos;
      let sentiment: AnalyzeHit["sentiment"] = "netral";
      let score = 0.5;
      if (total > 0) {
        const ratio = neg / total;
        if (ratio >= 0.6) {
          sentiment = "negatif";
          score = Math.min(0.97, 0.55 + ratio * 0.4 + Math.min(spans.length, 3) * 0.03);
        } else if (ratio <= 0.35) {
          sentiment = "positif";
          score = Math.min(0.97, 0.55 + (1 - ratio) * 0.4);
        } else {
          sentiment = "netral";
          score = 0.5 + Math.abs(0.5 - ratio) * 0.3;
        }
      } else {
        score = 0.45 + Math.min(spans.length, 3) * 0.05;
      }

      hits.push({
        aspect: key,
        label: ASPECT_LABEL[key],
        icon: ASPECT_ICON[key],
        sentiment,
        score: Math.round(score * 100) / 100,
        severity: SEVERITY[key],
        isFriction: FRICTION_ASPECTS.includes(key),
        evidence: spans.slice(0, 2).map((s) => spanAt(clean, s.at, s.len)),
      });
    }
  }

  // Urut: friksi negatif paling yakin di atas.
  hits.sort((a, b) => {
    const rank = (h: AnalyzeHit) =>
      h.sentiment === "negatif" ? 0 : h.sentiment === "netral" ? 1 : 2;
    return rank(a) - rank(b) || b.score - a.score;
  });

  const lower = clean.toLowerCase();
  const implicit = IMPLICIT_MARKERS.some((k) => lower.includes(k));
  const hasExplicitPungli = /\bpungli|pungutan|retribusi\b/i.test(clean);

  const t1 =
    typeof performance !== "undefined" && performance.now ? performance.now() : 0;

  return {
    text: clean,
    hits,
    // Angka ini nyata (waktu eksekusi fungsi), dengan lantai agar tidak 0 ms.
    latencyMs: Math.max(1, Math.round((t1 - t0) * 100) / 100),
    keywordBaselineWouldMiss: implicit && !hasExplicitPungli,
    note:
      "Baseline leksikon + isyarat sentimen. Pada produk final, lapisan ini diganti IndoBERT hasil fine-tuning tahap preliminary.",
  };
}
