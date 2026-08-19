# Model Selection & Evaluasi Final

Catatan keputusan model + strategi evaluasi, agar tidak lupa arah di final.

---

## 1. Perbandingan vs SILVER — SUDAH FINAL & TERKUNCI

Hasil locked silver test (A6/A8), dievaluasi **sekali** dan tidak boleh dibuka ulang:

| Model | Macro F1 (locked silver test) | Status |
|---|---|---|
| Keyword | 0,9768 | ⚠️ sirkular (berbagi vocabulary dengan silver rules) |
| **TF-IDF** | **0,7201** / Micro 0,8040 | ✅ **dipilih untuk deteksi aspek** |
| IndoBERT (aspek) | 0,5247 | Ditolak (kalah + lebih mahal) |
| IndoBERT (polarity) | 0,7459 | Dilatih, **belum** dipakai produksi |

**Locked-test policy:** jangan buka ulang silver test untuk memilih/menyetel ulang
model. Keputusan aspek = TF-IDF sudah final.

## 2. Perbandingan vs GOLD — BENCHMARK MANUSIA (final)

Gold-v1 (3 annotator, agreement aspect Jaccard 0,9664) adalah benchmark **manusia
yang independen** dari silver. Ketiga model dievaluasi terhadap gold-v1 **tanpa
re-tune** (inference-only, split leakage-safe yang sama):

| Model | Silver (locked) | Gold-v1 | Status |
|---|---|---|---|
| Keyword | 0,9768 (sirkular) | 0,7056 | ceiling referensi |
| **TF-IDF** | 0,7201 | **0,5777** | ✅ produksi (model terlatih) |
| IndoBERT (aspek) | 0,5247 | 0,4254 | ditolak |
| IndoBERT (polarity) | 0,7459 | 0,5077 (≈ chance) | ditolak |

**Kenapa produksi tetap TF-IDF (silver) dan bukan "model gold"?**

Gold adalah **benchmark evaluasi**, bukan data training:

1. **Independensi gold** hilang bila dipakai melatih.
2. **Circular/leakage** — 1.320 review gold = persis split evaluasi; train-di-gold
   lalu test-di-gold adalah sirkular (persis keyword 0,9768 di silver).
3. **Generalisasi** — gold 1.320 vs korpus 12.234 berteks.
4. **Alur benar:** `silver → latih TF-IDF → prediksi korpus → agregasi (A9)`;
   `gold → audit model terlatih`.
5. **Upgrade yang benar (pasca-hackathon):** retrain di gold + held-out human set
   baru untuk uji ulang.

## 3. Keputusan produksi (final)

| Komponen | Model produksi | Keputusan |
|---|---|---|
| Deteksi aspek | TF-IDF (`tfidf-aspect-silver-v1`) | Tetap (gold-v1 0,5777; IndoBERT 0,4254 kalah) |
| Polarity | Lexical fallback (`lexical-polarity-v1`) | Tetap (IndoBERT polarity 0,5077 ≈ chance) |
| Severity | — | `unavailable_no_supported_model` (support `high` 19 < 20) |

Catatan jujur: di gold, keyword (0,7056) > TF-IDF (0,5777). Keyword adalah lexikon
rule yang sama dengan pembuat silver (rule engine, bukan model terlatih); TF-IDF
tetap model yang belajar dari data. Keduanya dilaporkan terpisah.

## 4. Alur setelah gold selesai — DONE

1. ✅ `annotation-agreement` + `freeze-gold` → `gold.jsonl` (SHA `7b5b6057`).
2. ✅ Evaluasi 3 model vs gold-v1 → F1 terhadap manusia.
3. ✅ Update `model-card.md`, laporan, `/metode`, dan `qa-answer-bank.md`.
4. ✅ Keputusan polarity: IndoBERT 0,5077 → lexical tetap.
5. ⏳ Deploy + demo + presentasi (C5–C10).

## 5. Yang TIDAK boleh

- Membuka ulang silver test untuk tuning/selection.
- Mengganti model produksi tanpa dasar (gold harus membenarkan).
- Mengklaim metrik gold sebelum benar-benar dihitung.
