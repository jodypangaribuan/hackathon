# SIPATURE Model Card

**Model name/version:** `tfidf-aspect-silver-v1` (aspek) + `lexical-polarity-v1` (polarity)
**Pipeline version:** `a9-tfidf-lexical-v1.0.4`
**Status:** Released untuk deteksi aspek (TF-IDF); polarity memakai fallback leksikal
**Date:** 2026-08-14 (evaluasi silver terkunci; human-gold pending)

## Model Details

- **Deteksi aspek (produksi):** TF-IDF (word unigram/bigram + char 3–5 gram,
  `sublinear_tf`) → One-vs-Rest Logistic Regression (`class_weight="balanced"`,
  `C=1.0`, `max_iter=2000`, `solver="liblinear"`). Threshold per-aspek di-tune
  pada validation. Deterministik, CPU-only, latency ≈0,1 ms/review.
- **Polarity (produksi):** `lexical-polarity-v1` — fallback leksikal
  aspect-conditioned (konteks + isyarat negatif/positif + kontras), **tanpa
  probabilitas**.
- **Kandidat (belum produksi):** IndoBERT `indobenchmark/indobert-base-p1`
  (revisi `c2cd0b51…`, MIT, 124,5M param) — aspect & polarity. Polarity 0,7459
  (silver) berpotensi menggantikan fallback bila human-gold membenarkan.
- **Severity:** tidak tersedia (`unavailable_no_supported_model`) — support
  kelas `high` 19 < gate 20.
- **License/model pihak ketiga:** IndoBERT MIT; TF-IDF/sklearn BSD-3.

## Intended Use

Decision-support untuk mendeteksi *reported* tourism issues dan memprioritaskan
verifikasi lapangan manusia di kawasan Danau Toba. Output = sinyal triase,
bukan fakta lapangan.

## Out-of-Scope Use

- Public verdicts about destination safety, cleanliness, or pollution.
- Automated enforcement or funding decisions without human review.
- Scientific environmental measurement.
- Causal impact prediction.
- Menggantikan penilaian ahli/pengelola destinasi.

## Training and Evaluation Data

- **Sumber:** 14 CSV dataset panitia (ulasan + metadata), 22.302 raw → 22.169
  clean reviews (12.234 berteks) setelah dedup + quarantine.
- **Entitas:** 388 canonical destination (322 metadata anchor + 66 unresolved
  placeholder) via entity resolution (blocking + fuzzy name/address + Haversine;
  reviewed-pair precision 0,9714, false-merge 0,0286).
- **Label:** AI-assisted weak-supervision **silver** (`silver-1.0.0`), 1.320
  record (120 pilot + 1.200 main), konsensus 2/3 rule-pass, mean pass-agreement
  0,8827. **Bukan human-gold.**
- **Split:** leakage-safe per destination (duplicate/repeated-text digabung via
  union-find), 922 train / 196 validation / 202 locked test, 0 leakage, test
  terkunci & dievaluasi **sekali**.
- **Human-gold:** pending — anotasi 3 anggota tim via `tools/annotator/`.

## Metrics

Semua metrik = **agreement terhadap silver reference**, bukan human-gold
(human-gold evaluation pending).

| Komponen | Metrik (locked silver test) |
|---|---|
| TF-IDF aspek (produksi) | Macro F1 0,7201 · Micro F1 0,8040 · Exact Match 0,7079 · Hamming 0,0343 |
| IndoBERT aspek (kandidat, ditolak) | Macro F1 0,5247 · Micro 0,5241 |
| Keyword baseline (sirkular) | Macro F1 0,9768 (⚠️ berbagi vocabulary dgn silver rules) |
| IndoBERT polarity (kandidat) | Macro F1 0,7459 (support 248) |
| Kalibrasi (IndoBERT) | temperature 0,6 · ECE 0,2021 · Brier 0,1258 |
| Entity resolution | reviewed-pair precision 0,9714 · recall 0,4304 · false-merge 0,0286 |
| A9 inferensi | 9.785 prediksi · 1.682 sinyal · 103 destinasi actionable · 210 isu |
| Sensitivity bobot | top-20 Jaccard 0,8182–1,0000 |

Artifact metrik: `ml/artifacts/metrics/{keyword,tfidf}-silver-v1-test-metrics.json`,
`docs/evidence/…` (safe aggregate). Human-gold: `[PENDING]`.

## Limitations and Biases

- **Silver ≠ gold:** seluruh evaluasi saat ini terhadap weak-supervision; belum
  ada akurasi human-gold.
- **Keyword sirkular:** 0,9768 bukan akurasi nyata (diungkap sebagai ceiling).
- **Severity / facility-gap / feasibility:** tidak tersedia, renormalisasi bobot.
- **Polarity leksikal:** tidak mengeluarkan probabilitas; bisa salah pada
  negasi/sarkasme implisit.
- **Rare aspect tidak stabil:** `opening_hours` support 2 di test.
- **Bias popularitas/platform/bahasa:** destinasi populer punya lebih banyak
  ulasan; marker bahasa adalah heuristik; exposure memakai log-normalisasi.
- **Entity resolution recall rendah (0,4304):** unresolved destination tidak
  diberi prioritas (konservatif, tapi bisa melewatkan isu).
- **Evidence belum dinilai manusia** — tetap "reported issue", bukan fakta.
- **Simulator non-kausal** — bukan prediksi dampak.

## Ethical Considerations and Safeguards

- **Privasi:** reviewer name, review ID, source file/row tidak masuk bundle
  aplikasi; evidence text ditahan (`withheld_pending_privacy_review`).
- **Bahasa hati-hati:** istilah "reported issue" / "early-warning signal",
  bukan vonis "kotor/bahaya/tidak layak".
- **Human verification wajib:** setiap alert = kandidat verifikasi, bukan
  keputusan otomatis; ada workflow rejected alert.
- **Minimum support & identity gate:** insufficient-data dan unresolved
  identity tidak diranking.
- **Provenance:** setiap batch terikat hash (model/config/data) di
  `model_versions` + `data_exports`; regenerasi via `scripts/refresh.sh`.

## Rencana Update (setelah human-gold)

1. Isi metrik human-gold (silver-vs-gold agreement + F1 model vs gold).
2. Keputusan polarity (lexical vs IndoBERT) berdasarkan hasil gold.
3. Promosi status model card dari "released (silver)" ke "released (gold-validated)".
