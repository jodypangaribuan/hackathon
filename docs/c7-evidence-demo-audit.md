# C7 — Evidence & Demo Audit

**Tanggal:** 2026-08-19
**Scope:** audit evidence + demo case untuk Final Round (C7).

## 1. Evidence → Source Rows (traceability)

- `evidence.parquet` (restricted A9) menyimpan `source_file` + `source_row` +
  `review_id` (opaque hash) untuk setiap kutipan.
- Verifikasi spot-check: teks evidence adalah substring **verbatim** dari kolom
  `review-text` sumber (setelah NFKC + whitespace normalization — mis. newline
  dinormalisasi jadi spasi).
- **Catatan offset:** `source_row` adalah nomor baris file (1-indexed + header),
  sehingga = indeks pandas 0-based + 2. Konsisten di semua kasus yang dicek.
- Export publik (`app-export.json`) lebih anonim: evidence hanya `text` +
  `aspect_probability` + `published_date_estimate` (tanpa `review_id`/`source_*`).

## 2. Reviewer Identity

- `evidence.parquet` tidak memuat `reviewer-id`/`name` — hanya `review_id` hash.
- Export publik tidak memuat identitas reviewer maupun provenance review-level.
- Kolom `reviewer-id`/`name` di CSV sumber TIDAK masuk artifact A9 sama sekali.

## 3. Manual-Check Predictions (main/backup cases)

| Case | Temuan |
|---|---|
| Kawah Putih Dolok Tinggi Raja | Prediksi akses + pungli (price_transparency) didukung kutipan nyata "jalan rusak", "pungli". Benar. |
| Bagus Bay Guest House | sanitation (toilet/kamar mandi kotor) + maintenance (kasur rusak) didukung kutipan. Benar. |
| Puncak Paralayang Sibodiala | `Insufficient Data` (support < gate) — sistem tidak memeringkat. Sesuai missing-aware. |

Catatan limitation yang ditemukan (sudah didokumentasikan):
- Lexical polarity bisa salah pada klausa kontras ("tempat bagus, tapi jalan jelek" → akses `neutral`).
- Review pendek bahasa Inggris kadang tidak terdeteksi (FN).
- Negasi seperti "pungli tidak ada" bisa ter-flag negative.

## 4. Priority Formula & Intervention Mapping

- `scoring.yaml` bobot tersedia: complaint_frequency 0,20 + model_confidence 0,15
  + persistence 0,15 + visitor_exposure 0,10 = 0,60 → renormalisasi jadi 0,3333 /
  0,2500 / 0,2500 / 0,1667 (cocok dengan formula di `/metode`).
- `a9.yaml` memetakan 14 aspek → `recommended_verification` + `candidate_intervention`
  (tampil di detail + queue).

## 5. False-Positive Demo Case (human oversight)

**Alert:** Danau Sidihoni — `scenery`, priority High, rank 40 (neg=4/22).

Keempat review "negatif" ternyata **positif/pujian**:
- "danau di atas danau, danau yang unik …"
- "Danaunya terlihat biasa, tetapi sebenarnya berpotensi untuk dikembangkan …"
- "Lokasi bagus, kalau dikelola profesional pasti berdampak …"
- "tempat wisata yg masih alami …"

Lexical polarity salah baca frasa "terlihat biasa" / "tidak terlalu luas" sebagai
negatif. Alert ini di-**reject** via `/api/alerts/verify` (reason: false positive).

Demo naratif: sistem mengangkat sinyal → manusia menolaknya dengan alasan → status
alert `rejected` tersimpan (oversight terbukti, bukan otomatis percaya model).
