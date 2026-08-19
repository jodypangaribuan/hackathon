# C1 — Final Round Scope Lock v2.0

**Status:** Dikunci (final)
**Tanggal:** 2026-08-19
**Menggantikan:** `SIPATURE-Project-Charter.md` §Scope Lock v1.0 (preliminary)
**Acuan final:** Technical Meeting 18 Aug 2026 → `docs/dgx-deployment-runbook.md` §A

> Dokumen ini mengunci rantai, model produksi, demo case, mandatory feature, dan
> kebijakan freeze untuk Final Round (21–22 Agustus 2026). Angka demo memakai
> output A9 final (`a9-tfidf-lexical-v1.0.4`), bukan baseline keyword+rating awal.

---

## 1. Rantai Terkunci (review → model → signal → evidence → priority → verification)

```text
Raw review
-> cleaned & linked data (entity resolution, canonical destination)
-> model prediction (TF-IDF aspect + lexical polarity; severity unavailable)
-> destination signal (aggregation + Bayesian smoothing + missing-aware)
-> verbatim evidence (evidence gate, privacy-safe)
-> explainable priority (renormalisasi bobot bila komponen missing)
-> human field verification (rejected-alert workflow)
-> candidate intervention
```

- **Deteksi aspek:** `tfidf-aspect-silver-v1` (TF-IDF word+char → One-vs-Rest
  Logistic Regression), threshold per-aspek.
- **Polarity:** `lexical-polarity-v1` (aspect-conditioned lexical fallback, tanpa
  probabilitas). IndoBERT polarity **ditolak** (gold-v1 0,5077 ≈ chance).
- **Severity:** `unavailable_no_supported_model` (support kelas `high` 19 < gate 20).
- **IndoBERT:** ditolak untuk produksi (aspect gold-v1 0,4254 < TF-IDF 0,5777 <
  keyword 0,7056).

Benchmark evaluasi akhir terhadap **human-gold gold-v1** (SHA `7b5b6057…`,
agreement aspect Jaccard 0,9664 / polarity 0,9804 / severity κ 1,0):

| Model | Silver | Gold-v1 |
|---|---|---|
| Keyword | 0,9768 (sirkular) | 0,7056 |
| TF-IDF (produksi) | 0,7201 | 0,5777 |
| IndoBERT (aspek) | 0,5247 | 0,4254 |

## 2. Demo Case Terkunci (nilai A9 final)

### Utama — Kawah Putih Dolok Tinggi Raja

| Field | Nilai A9 final |
|---|---|
| ID | `dest_wisata_2bd1bff4744c6a` (`kawah-putih-dolok-tinggi-raja`) |
| Google Maps rating | 4,0 |
| Review berteks | 47 |
| Priority | High · score 0,721 · rank 4 |
| Confidence | low |
| Isu utama (mention) | price_transparency (17) · access (11) · safety (3) |

**Cerita demo:** rating tinggi (4,0) menyembunyikan sinyal pungutan harga dan
akses jalan; priority engine mengangkatnya ke High dengan evidence verbatim.

### Backup — Bagus Bay Guest House

| Field | Nilai A9 final |
|---|---|
| ID | `dest_hotel_07475b028ff995` (`bagus-bay-guest-house`) |
| Google Maps rating | 5,0 |
| Review berteks | 71 |
| Priority | Medium · score 0,382 · rank 76 |
| Confidence | low |
| Isu utama (mention) | sanitation (21) · maintenance (11) · price_transparency (10) |

### Failure Case — Puncak Paralayang Sibodiala

| Field | Nilai A9 final |
|---|---|
| ID | `dest_wisata_edb0d6c8c3e9a6` (`puncak-paralayang-sibodiala`) |
| Google Maps rating | 4,7 |
| Review berteks | 9 |
| Priority | Insufficient Data · rank — |
| Confidence | insufficient |

**Cerita demo:** review menyebut akses/jalan berbahaya, tetapi support tekstual
di bawah minimum-mention gate → sistem **tidak** memeringkat dan menandai
`insufficient data`, menunjukkan missing-aware + human oversight, bukan klaim.

## 3. Mandatory Features Terkunci

- Overview (coverage, issues, priorities).
- Map (actionable/monitor/insufficient, filter, 322 canonical coordinates).
- Detail (evidence, metadata enrichment, canonical identity, confidence, health,
  missing components).
- Queue (reason, ranking, support, recommended verification).
- Simulator (asumsi eksplisit + warning non-kausal permanen).
- Analyzer (sandbox leksikal, dilabeli jelas bukan model A9).

## 4. Model & Data Lock (hash)

| Artifact | SHA-256 |
|---|---|
| Model aspect `tfidf-aspect-silver-v1` | `a10bddb1…` |
| App export `app-export.json` | `8037d072…` |
| Human-gold `gold.jsonl` (gold-v1) | `7b5b6057…` |
| Taxonomy `taxonomy.yaml` | `9840978b…` |

## 5. Internal Freeze

- **Internal freeze:** 2026-08-20 23:59 WIB (TBD — konfirmasi tim).
- **Lockdown panitia:** 2026-08-22 12:00 WIB.
- Setelah freeze, hanya perbaikan blocker yang diperbolehkan; setiap perubahan
  wajib dicatat di `docs/known-data-issues.md` / tracker harian.
