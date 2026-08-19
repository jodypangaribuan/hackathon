# SIPATURE

## Sistem Pemantauan Ulasan dan Prioritas Tindak Lanjut Pariwisata Toba

### Laporan Final Round — Del AI Hackathon 2026

**Nama Tim:** `[NAMA TIM]`
**Ketua:** `[NAMA KETUA]`
**Anggota:** `[NAMA ANGGOTA 1]`, `[NAMA ANGGOTA 2]`
**Tanggal:** 21–22 Agustus 2026
**Versi:** `[VERSI]`

> Jangan mencantumkan identitas institusi pendidikan. Atribut institusi tidak boleh ditampilkan. PDF akhir maksimal 25 MB.

---

## Petunjuk Template

- Ganti seluruh `[PLACEHOLDER]` dengan data aktual; hapus blok `> Arahan:` pada versi final.
- Struktur mengikuti **6 poin wajib presentasi** dan **rubrik 7 kriteria** (Technical Meeting 19 Agustus 2026).
- Pisahkan target, asumsi, dan hasil aktual secara eksplisit.
- Setiap angka terlacak ke notebook/script/config/artifact (hash).
- Setiap gambar/tabel memiliki nomor, judul, sumber, dan interpretasi.
- Evidence verbatim, anonim, dan memiliki provenance internal; gunakan istilah *reported issue* / *early-warning signal*.
- Wajib memuat **Deklarasi Penggunaan AI** (BAB IX).

---

## Ringkasan Eksekutif

> Arahan: 250–400 kata. Masalah → solusi → data → model → benchmark gold-v1 → produk → dampak → limitation.

`[MASALAH: RATING RATA-RATA TIDAK CUKUP]`

`[SOLUSI: REVIEW → ASPEK → SIGNAL → EVIDENCE → PRIORITAS → VERIFIKASI]`

`[DATA + HUMAN-GOLD BENCHMARK + MODEL PRODUKSI]`

`[PRODUK + DEPLOYMENT DGX B200 + LIMITATION]`

| Indikator Utama | Hasil Aktual | Keterangan |
| --- | ---: | --- |
| Review bersih | 22.169 | dari 22.302 raw |
| Review berteks | 12.234 | input NLP |
| Gold annotation | 1.320 | 3 annotator, agreement Jaccard 0,9664 |
| Aspect Macro F1 (gold-v1) | 0,5777 | TF-IDF (produksi) |
| IndoBERT aspect (gold-v1) | 0,4254 | ditolak |
| Destinasi actionable | 103 | 210 isu |
| Latency `/predict-review` | p50 2,1 ms | CPU-only |

---

# BAB I — LATAR BELAKANG DAN PERMASALAHAN

> Poin wajib 1. Rubrik 1 (Inovasi) & 5 (Dampak).

## 1.1 Konteks Pariwisata Danau Toba
`[EKOSISTEM, PENGELOLAAN, KUALITAS PENGALAMAN]`

## 1.2 Kondisi Data
`[REVIEW + METADATA MENTAH, TIDAK TERINTEGRASI]`

## 1.3 Kesenjangan Keputusan (Decision Gap)
`[RATING TINGGI MENYEMBUNYIKAN ISU; VOLUME BESAR TAK TERBACA MANUAL]`

## 1.4 Rumusan Masalah
`[BAGAIMANA MENGUBAH ULASAN → ISU SPESIFIK + BUKTI + PRIORITAS VERIFIKASI]`

## 1.5 Relevansi dengan Challenge
| Nilai | Kontribusi |
| --- | --- |
| Informatif | `[ ]` |
| Efisien | `[ ]` |
| Berkelanjutan | `[ ]` |
| Bernilai | `[ ]` |

---

# BAB II — ANALISIS PERMASALAHAN

> Poin wajib 2. Rubrik 1 & 2.

## 2.1 Pemangku Kepentingan
`[PENGELOLA, BPODT/PEMDA, WISATAWAN, PELAKU LOKAL]`

## 2.2 Profil Data
| Dataset | Baris | Fungsi | Masalah |
| --- | ---: | --- | --- |
| `wisata-v2.csv` | 12.691 | Review wisata | `[ ]` |
| `resto-hotel-v2.csv` | 9.611 | Review hotel/resto | `[ ]` |
| `[FILE]` | `[N]` | `[ ]` | `[ ]` |

## 2.3 Temuan EDA
- Skala: 22.302 raw → 22.169 clean (12.234 textual, 9.935 rating-only).
- Rating imbalance: 15.595 dari 22.243 rating = bintang 5.
- Volume vs complaint: sample kecil tidak stabil → Bayesian smoothing + min support.

## 2.4 Risiko dan Mitigasi
| Risiko | Mitigasi |
| --- | --- |
| Popularity bias | smoothing, min support |
| False alert | bahasa netral + verifikasi manusia |
| Sparse label | stratified sampling, Macro F1, class weights |

---

# BAB III — PENDEKATAN AI DAN MODELLING

> Poin wajib 3. Rubrik 2 (Implementasi & Kematangan AI).

## 3.1 Rantai Solusi
```text
Raw review → cleaning/entity resolution → annotation (silver + gold)
→ model (TF-IDF aspect + lexical polarity) → signal
→ evidence → priority → human verification → candidate intervention
```

## 3.2 Taxonomy
`[14 ASPEK: lingkungan, infrastruktur, pengalaman, operasional]`

## 3.3 Annotation
- Silver (AI-assisted weak supervision) untuk training.
- **Gold (human, 3 annotator)** untuk benchmark: 1.320 record, agreement Jaccard 0,9664 / polarity 0,9804 / severity κ 1,0.

## 3.4 Model yang Dibandingkan
| Model | Metode | Peran |
| --- | --- | --- |
| Keyword | rule leksikal | ceiling referensi |
| TF-IDF | word+char → OVR Logistic Regression | produksi |
| IndoBERT | fine-tune `indobenchmark/indobert-base-p1` | kandidat (ditolak) |

## 3.5 Split Leakage-Safe
`[922/196/202 per destinasi, 0 leakage, test terkunci]`

## 3.6 Polarity & Severity
- Polarity: `lexical-polarity-v1` (deterministik, tanpa probabilitas).
- Severity: `unavailable_no_supported_model` (support high 19 < 20).

---

# BAB IV — PROSES PENGEMBANGAN SOLUSI

> Poin wajib 4. Rubrik 2 & 4.

## 4.1 Tahapan
| Tahap | Output | Status |
| --- | --- | --- |
| Data (inventory, EDA, cleaning, ER) | `canonical_reviews.parquet` | Done |
| Annotation (silver + gold) | `gold.jsonl` (SHA `7b5b6057`) | Done |
| Model (keyword/TF-IDF/IndoBERT) | `tfidf-aspect-silver-v1` | Done |
| Engine (inference, aggregation, priority) | `a9-tfidf-lexical-v1.0.4` | Done |
| Product (API + web + workflow) | 3-service Docker | Done |

## 4.2 Reproducibility
`[SEED 42, CONFIG HASH, LOCKED DEPENDENCIES, MANIFEST PER STAGE]`

## 4.3 Teknologi
| Layer | Teknologi |
| --- | --- |
| Data | Python, Pandas, Parquet |
| Model | scikit-learn, PyTorch (IndoBERT) |
| API | FastAPI |
| Web | Next.js, Leaflet |
| Deployment | Docker, DGX B200 |

---

# BAB V — IMPLEMENTASI PRODUK DAN DEPLOYMENT

> Poin wajib 5. Rubrik 2 & 3 (Kualitas Produk).

## 5.1 Arsitektur
```text
web (Next.js) → inference (FastAPI TF-IDF) → db (PostgreSQL)
```

## 5.2 Fitur
`[OVERVIEW, MAP, DETAIL, QUEUE, SIMULATOR, ANALYZER, VERIFICATION WORKFLOW]`

## 5.3 Deployment DGX B200
- Docker Compose 3-service; model & data di-bundle (tanpa download saat startup).
- Offline: map tile → SVG luring; analyzer → fallback leksikal.
- Health check, cold start, restart verified.

## 5.4 Performa
| Metrik | Nilai |
| --- | --- |
| `/predict-review` latency | p50 2,1 ms · p95 3,1 ms |
| `/api/analyze` latency | p50 6,5 ms · p95 9,8 ms |
| Memory | web 95 MiB · inference 133 MiB · db 23 MiB |

---

# BAB VI — EVALUASI DAN HASIL

> Rubrik 2. Benchmark gold-v1 (human).

## 6.1 Benchmark Gold-v1
| Model | Silver (locked) | Gold-v1 |
| --- | ---: | ---: |
| Keyword | 0,9768 (sirkular) | 0,7056 |
| TF-IDF (produksi) | 0,7201 | 0,5777 |
| IndoBERT (aspek) | 0,5247 | 0,4254 |
| IndoBERT (polarity) | 0,7459 | 0,5077 (≈ chance) |

## 6.2 Keputusan Model
`[TF-IDF TETAP; INDOBERT DITOLAK; GOLD = BENCHMARK, BUKAN TRAINING DATA]`

## 6.3 Entity Resolution
`[precision 0,9714 · recall 0,4304 · false-merge 0,0286]`

## 6.4 Error Analysis
`[NEGATION, IMPLICIT, MIXED LANGUAGE, RARE ASPECT; FALSE-POSITIVE CASE]`

---

# BAB VII — DAMPAK DAN POTENSI PENGEMBANGAN

> Poin wajib 6. Rubrik 5 (Dampak) & 4 (Skalabilitas).

## 7.1 Manfaat per Stakeholder
| Pihak | Manfaat | Indikator |
| --- | --- | --- |
| Pengelola | `[ ]` | time-to-verification |
| BPODT/Pemda | `[ ]` | `[ ]` |
| Wisatawan | `[ ]` | `[ ]` |

## 7.2 Rencana Pilot
`[5–10 DESTINASI, BLIND REVIEW, FIELD VERIFICATION, KPI]`

## 7.3 Keberlanjutan
`[FEEDBACK LOOP, RETRAINING, GOVERNANCE, COST]`

## 7.4 Skalabilitas
`[BATCH-FIRST, POSTGRES, PARALELISASI]`

---

# BAB VIII — RESPONSIBLE AI DAN ETIKA

> Rubrik 7.

- Reviewer identity tidak muncul di UI/API/log.
- Evidence verbatim + provenance; teks ditahan publik.
- Bahasa: *reported issue* / *early-warning signal*, bukan vonis.
- Low-support → `Insufficient Data`, tidak diranking.
- Human verification wajib; rejected-alert workflow tersedia.

---

# BAB IX — DEKLARASI PENGGUNAAN AI

> Rubrik 7. Wajib.

## 9.1 AI dalam Solusi
| Komponen | Model/Metode | Status |
| --- | --- | --- |
| Aspect detection | TF-IDF + OVR LR | trained (silver) |
| Polarity | lexical fallback | deterministik |
| Severity | — | unavailable |

## 9.2 AI dalam Proses Pengembangan
| Tool | Penggunaan | Verifikasi Manusia |
| --- | --- | --- |
| `[LLM/IDE]` | `[ ]` | `[ ]` |

## 9.3 Batas Penggunaan AI
- AI tidak menjadi ground-truth tanpa verifikasi manusia.
- AI tidak membuat evidence baru.
- Simulator bukan causal prediction.

## 9.4 Deklarasi Kejujuran Hasil
> Seluruh metric berasal dari evaluasi aktual; target/asumsi/hasil dibedakan; evidence tidak difabrikasi.

---

# RUBRIC TRACEABILITY

| Kriteria (Bobot) | Bukti |
| --- | --- |
| 1. Inovasi (15%) | BAB I, II, III |
| 2. Implementasi AI (20%) | BAB III, IV, VI |
| 3. Kualitas Produk (15%) | BAB V |
| 4. Skalabilitas (15%) | BAB IV, VII |
| 5. Dampak Pariwisata (20%) | BAB I, VII |
| 6. Presentasi (10%) | Ringkasan, BAB VII, slide |
| 7. Etika & Deklarasi AI (5%) | BAB VIII, IX |

---

# LAMPIRAN

- Lampiran A — Data Dictionary (`docs/data-dictionary.md`).
- Lampiran B — Model Card (`docs/model-card.md`).
- Lampiran C — Reproducibility (`docs/reproducibility-runbook.md`).
- Lampiran D — Full Metrics (`ml/artifacts/metrics/*`).
- Lampiran E — Deployment Runbook (`docs/dgx-deployment-runbook.md`).
- Lampiran F — Evidence & Demo Audit (`docs/c7-evidence-demo-audit.md`).

---

## Finalisasi Dokumen

- [ ] Enam poin wajib presentasi tercakup dan berurutan.
- [ ] Rubrik 7 kriteria terpetakan ke bab bukti.
- [ ] Seluruh placeholder/arahan dihapus.
- [ ] Tanpa identitas institusi pendidikan.
- [ ] Tanpa PII reviewer.
- [ ] Deklarasi Penggunaan AI lengkap.
- [ ] PDF akhir ≤ 25 MB.
- [ ] Nama file: `[NamaTim] - LaporanFinal.pdf`.
