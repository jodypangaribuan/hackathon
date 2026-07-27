# SIPATURE

## Sistem Peringatan Dini dan Prioritas Intervensi Kualitas Pariwisata Danau Toba

### Laporan Analisis — Preliminary Round Del AI Hackathon 2026

**Nama Tim:** `[NAMA TIM]`  
**Ketua:** `[NAMA KETUA]`  
**Anggota:** `[NAMA ANGGOTA]`  
**Tanggal:** `[TANGGAL]`  
**Versi:** `[VERSI]`

> Jangan mencantumkan identitas institusi pendidikan. PDF akhir maksimal 25 MB.

## Petunjuk Template

- Ganti seluruh `[PLACEHOLDER]` dengan data aktual.
- Hapus seluruh blok `> Arahan:` pada versi final.
- Pisahkan target, asumsi, dan hasil aktual.
- Setiap angka harus terlacak ke notebook/script/config/artifact.
- Setiap gambar/tabel memiliki nomor, judul, sumber, interpretasi.
- Evidence harus verbatim, anonim, dan memiliki provenance internal.
- Gunakan istilah `sinyal peringatan dini`, bukan vonis terhadap destinasi.

## Ringkasan Eksekutif

> Arahan: 250–400 kata. Ringkas masalah, target user, data, pendekatan AI, hasil aktual utama, produk, manfaat, dan limitation.

`[MASALAH DAN ALASAN RATING RATA-RATA TIDAK CUKUP]`

`[SOLUSI: REVIEW -> ISSUE -> EVIDENCE -> PRIORITY -> VERIFICATION]`

`[DATASET, MODEL YANG DIBANDINGKAN, HASIL LOCKED TEST]`

`[MANFAAT DAN LIMITATION UTAMA]`

| Indikator Utama | Hasil Aktual | Keterangan |
| --- | ---: | --- |
| Total review | `[N]` | `[CAKUPAN]` |
| Review berteks | `[N]` | `[PERSENTASE]` |
| Destinasi canonical | `[N]` | `[VERSI DATA]` |
| Gold annotation | `[N]` | `[VERSI]` |
| Aspect Macro F1 | `[0.000]` | `[MODEL, TEST]` |
| Alert Precision | `[0.000]` | `[THRESHOLD]` |
| Evidence correctness | `[0.000]` | `[HUMAN EVALUATION]` |

## Daftar Isi

`[GENERATE OTOMATIS]`

## Daftar Gambar dan Tabel

`[GENERATE OTOMATIS]`

## Daftar Istilah

| Istilah | Definisi |
| --- | --- |
| ABSA | Aspect-Based Sentiment Analysis |
| Macro F1 | Rata-rata F1 semua label dengan bobot sama |
| Entity Resolution | Penghubungan record lintas sumber ke entitas canonical |
| Early-Warning Signal | Sinyal berbasis ulasan yang memerlukan verifikasi manusia |
| `[ISTILAH]` | `[DEFINISI]` |

---

# BAB I — LATAR BELAKANG

## 1.1 Konteks Pariwisata Danau Toba

> Arahan: Jelaskan ekosistem destinasi, akomodasi, kuliner, transportasi, fasilitas, budaya, masyarakat, dan pemerintah. Fokus pada kualitas pengelolaan.

`[ISI KONTEKS]`

## 1.2 Latar Belakang Data

> Arahan: Jelaskan review, metadata, koordinat, fasilitas, jam, harga, dan transportasi yang mentah, tidak lengkap, tidak terstruktur, dan belum terintegrasi.

`[ISI KONDISI DATA]`

## 1.3 Kesenjangan Keputusan Operasional

> Arahan: Bedakan memiliki data dengan memiliki actionable intelligence. Berikan contoh rating tinggi yang menyembunyikan isu sanitasi, sampah, akses, atau harga.

`[ISI DECISION GAP]`

## 1.4 Urgensi Permasalahan

> Arahan: Jelaskan dampak pada pengalaman, keberlanjutan, efisiensi inspeksi, reputasi, dan alokasi sumber daya. Hindari klaim ekonomi tanpa bukti.

`[ISI URGENSI]`

## 1.5 Relevansi dengan Challenge

| Nilai Challenge | Kontribusi SIPATURE |
| --- | --- |
| Informatif | `[KONTRIBUSI]` |
| Inklusif | `[KONTRIBUSI/BATASAN]` |
| Efisien | `[PRIORITAS INSPEKSI]` |
| Berkelanjutan | `[SANITASI/LINGKUNGAN]` |
| Bernilai | `[MANFAAT OPERASIONAL]` |

## 1.6 Tujuan

### 1.6.1 Tujuan Umum

`[SATU TUJUAN UMUM]`

### 1.6.2 Tujuan Khusus

1. `[TUJUAN DATA ENGINEERING]`
2. `[TUJUAN MODEL]`
3. `[TUJUAN AGREGASI/RANKING]`
4. `[TUJUAN PRODUK]`
5. `[TUJUAN EVALUASI/RESPONSIBLE AI]`

## 1.7 Manfaat

| Pihak | Manfaat | Indikator |
| --- | --- | --- |
| Pengelola destinasi | `[MANFAAT]` | `[METRIC]` |
| BPODT/pemerintah | `[MANFAAT]` | `[METRIC]` |
| Wisatawan | `[MANFAAT]` | `[METRIC]` |
| Masyarakat lokal | `[MANFAAT]` | `[METRIC]` |

## 1.8 Ruang Lingkup dan Batasan

**Termasuk:** klasifikasi review, aspect polarity/severity, entity resolution, health/priority score, peta, evidence, queue, simulator.

**Tidak termasuk:** chatbot/RAG, booking, marketplace, real-time crowd tracking, scientific monitoring, causal impact prediction.

## 1.9 Struktur Laporan

`[RINGKAS ISI BAB I–VIII]`

---

# BAB II — ANALISIS PERMASALAHAN

## 2.1 Pemangku Kepentingan

| Stakeholder | Peran | Kebutuhan | Hambatan |
| --- | --- | --- | --- |
| Pengelola destinasi | `[PERAN]` | `[KEBUTUHAN]` | `[HAMBATAN]` |
| BPODT/pemerintah | `[PERAN]` | `[KEBUTUHAN]` | `[HAMBATAN]` |
| Wisatawan | `[PERAN]` | `[KEBUTUHAN]` | `[HAMBATAN]` |
| Pelaku lokal | `[PERAN]` | `[KEBUTUHAN]` | `[HAMBATAN]` |

## 2.2 Persona dan Jobs-to-be-Done

### 2.2.1 Pengelola Destinasi

`[PERSONA, TUGAS, KEPUTUSAN, PAIN POINT, SUCCESS CONDITION]`

### 2.2.2 Perencana Pemerintah/BPODT

`[PERSONA, TUGAS, KEPUTUSAN, PAIN POINT, SUCCESS CONDITION]`

## 2.3 Problem Tree

> Arahan: Tampilkan akar masalah -> masalah inti -> konsekuensi.

**Gambar 2.1. Problem Tree SIPATURE**  
`[SISIPKAN DIAGRAM DAN INTERPRETASI]`

## 2.4 Current User Journey

```text
Review tersebar -> inspeksi manual -> sulit membandingkan isu
-> keputusan ad hoc -> respons terlambat
```

`[VALIDASI DENGAN WAWANCARA ATAU NYATAKAN SEBAGAI ASUMSI]`

## 2.5 Inventaris dan Profil Data

| Dataset | Baris | Kolom | Fungsi | Masalah Utama |
| --- | ---: | ---: | --- | --- |
| `wisata-v2.csv` | `[N]` | `[N]` | `[FUNGSI]` | `[ISSUE]` |
| `resto-hotel-v2.csv` | `[N]` | `[N]` | `[FUNGSI]` | `[ISSUE]` |
| `[FILE]` | `[N]` | `[N]` | `[FUNGSI]` | `[ISSUE]` |

**Gambar 2.2. Missing Values Heatmap**  
`[VISUAL + INTERPRETASI]`

**Gambar 2.3. Data Cleaning Funnel**  
`[VISUAL + ALASAN RECORD DIKELUARKAN]`

## 2.6 EDA Review

### 2.6.1 Distribusi Rating

`[GAMBAR + TEMUAN + IMPLIKASI CLASS IMBALANCE]`

### 2.6.2 Panjang dan Bahasa Review

`[GAMBAR + KEPUTUSAN MAX TOKEN + MIXED LANGUAGE]`

### 2.6.3 Volume Review per Destinasi

`[GAMBAR + POPULARITY BIAS + MINIMUM SUPPORT]`

### 2.6.4 Kandidat Aspek dan Co-Occurrence

`[DISTRIBUSI ASPEK + HEATMAP + ALASAN MULTILABEL]`

### 2.6.5 Repeated Text, Negasi, Recency

`[TEMUAN DAN IMPLIKASI CLEANING/MODEL]`

## 2.7 EDA Metadata dan Geospasial

`[TYPE, STATUS, FEE, HOURS, FACILITIES, COORDINATE COVERAGE, OUTLIERS, SUPPORTING SERVICES]`

**Gambar 2.4. Geographic Data Coverage**  
`[SISIPKAN PETA]`

## 2.8 Bias dan Risiko Data

| Risiko | Bukti | Dampak | Mitigasi |
| --- | --- | --- | --- |
| Popularity bias | `[BUKTI]` | `[DAMPAK]` | Smoothing/min support |
| Rating imbalance | `[BUKTI]` | `[DAMPAK]` | Macro F1/class weights |
| Platform bias | `[BUKTI/ASUMSI]` | `[DAMPAK]` | Limitation |
| Staleness | `[BUKTI]` | `[DAMPAK]` | Freshness indicator |
| Missing metadata | `[BUKTI]` | `[DAMPAK]` | Insufficient Data |

## 2.9 Rumusan Masalah dan Hipotesis

1. `[PERTANYAAN ASPECT DETECTION]`
2. `[PERTANYAAN AGREGASI SAMPEL KECIL]`
3. `[PERTANYAAN PRIORITY RANKING]`
4. `[PERTANYAAN EVIDENCE/RESPONSIBLE AI]`

| ID | Hipotesis | Cara Uji | Metric |
| --- | --- | --- | --- |
| H1 | `[MODEL VS BASELINE]` | `[UJI]` | Macro F1 |
| H2 | `[ALERT QUALITY]` | `[UJI]` | Alert Precision |
| H3 | `[PRODUCT UTILITY]` | `[UJI]` | Time saved/evidence correctness |

## 2.10 Kesimpulan Analisis Permasalahan

`[ALASAN MEMILIH REVIEW INTELLIGENCE DAN INTERVENTION RANKING]`

---

# BAB III — DESAIN SOLUSI DAN INDIKATOR KEBERHASILAN

## 3.1 Konsep dan Value Proposition

> Arahan: Tulis one-sentence pitch, mekanisme kerja, dan nilai bagi pengguna.

`[SIPATURE MENGUBAH ...]`

## 3.2 Prinsip Desain

- Evidence before recommendation.
- Human verification before action.
- No issue berbeda dari insufficient data.
- Score components transparan.
- Batch-first dan offline-capable.
- Privacy by design.

`[JELASKAN IMPLIKASI SETIAP PRINSIP]`

## 3.3 Arsitektur Konseptual

```text
Raw CSV -> cleaning/entity resolution -> annotation/training
-> batch inference -> aggregation -> health/priority engine
-> API -> SIPATURE -> human verification
```

**Gambar 3.1. Arsitektur SIPATURE**  
`[SISIPKAN DIAGRAM DAN DESKRIPSI KOMPONEN]`

## 3.4 Fitur Utama

### 3.4.1 Regional Overview

`[HEALTH, ALERTS, COVERAGE, ISSUE DISTRIBUTION, TOP TARGETS]`

### 3.4.2 Intelligence Map

`[LAYERS, FILTERS, CONFIDENCE, COVERAGE, OFFLINE FALLBACK]`

### 3.4.3 Destination Evidence Page

`[SCORES, ISSUES, EVIDENCE, METADATA CONFLICT, VERIFICATION]`

### 3.4.4 Intervention Queue

`[PRIORITY, ISSUE, SUPPORT, CONFIDENCE, NEXT STEP, STATUS]`

### 3.4.5 Intervention Simulator

`[INPUT, ASSUMPTION, OUTPUT, NON-CAUSAL LABEL]`

### 3.4.6 Live Analyzer

`[REAL-TIME PREDICTION DAN STATUS MODEL/BASELINE]`

## 3.5 User Flow

```text
Overview -> map/filter -> destination -> evidence
-> priority explanation -> verification -> intervention status
```

**Gambar 3.2. User Flow**  
`[SISIPKAN DIAGRAM]`

## 3.6 Taxonomy dan Output Model

| Grup | Aspek | Definisi |
| --- | --- | --- |
| Lingkungan | cleanliness, waste, sanitation, crowding | `[DEFINISI]` |
| Infrastruktur | access, parking, public_facilities | `[DEFINISI]` |
| Pengalaman | scenery, comfort, safety, price_transparency | `[DEFINISI]` |
| Operasional | staff_service, maintenance, opening_hours | `[DEFINISI]` |

Polarity: `positive | negative | neutral`. Severity negatif: `low | medium | high` atau `[TAXONOMY AKTUAL]`.

## 3.7 Desain Health dan Priority Score

### 3.7.1 Aspect Health

```text
AspectHealth = 100 * (1 - SmoothedWeightedComplaintRate)
```

`[WEIGHT, FRESHNESS, DUPLICATE DISCOUNT, BAYESIAN SMOOTHING]`

### 3.7.2 Tourism Health

```text
0.25 environmental + 0.20 sanitation + 0.15 infrastructure
+ 0.15 safety + 0.15 operational + 0.10 visitor_experience
```

`[VALIDASI BOBOT, SENSITIVITY, MISSING COMPONENT]`

### 3.7.3 Priority Score

```text
0.25 severity + 0.20 frequency + 0.15 confidence
+ 0.15 persistence + 0.10 exposure + 0.10 facility_gap
+ 0.05 feasibility
```

`[NORMALISASI, MISSING FEATURE, LABEL CRITICAL/HIGH/MEDIUM/MONITOR]`

## 3.8 Indikator Keberhasilan

### 3.8.1 Data dan Model

| Metric | Target | Hasil Aktual | Status |
| --- | ---: | ---: | --- |
| Entity Resolution F1 | `[ ]` | `[ ]` | `[ ]` |
| False-merge rate | `[ ]` | `[ ]` | `[ ]` |
| Aspect Macro F1 | `[ ]` | `[ ]` | `[ ]` |
| Aspect Micro F1 | `[ ]` | `[ ]` | `[ ]` |
| Alert Precision | `[ ]` | `[ ]` | `[ ]` |
| Polarity Macro F1 | `[ ]` | `[ ]` | `[ ]` |
| High-severity precision | `[ ]` | `[ ]` | `[ ]` |

### 3.8.2 Sistem dan Dampak

| Metric | Target | Hasil/Status |
| --- | ---: | --- |
| Evidence correctness | `[ ]` | `[ ]` |
| Unsupported alert rate | `[ ]` | `[ ]` |
| NDCG@10 | `[ ]` | `[ ]` |
| Analysis time saved | `[ ]` | `[HASIL/RENCANA]` |
| Destinations analyzed | `[ ]` | `[ ]` |

## 3.9 Diferensiasi dan Kebaruan

| Pendekatan Umum | SIPATURE |
| --- | --- |
| Sentiment dashboard | Aspect-specific issue dan severity |
| Review summary | Evidence verbatim dan confidence |
| Ranking opaque | Transparent intervention priority |
| Environmental verdict | Reported issue untuk verifikasi |
| Generic action | Human-reviewed verification/action mapping |

## 3.10 Responsible AI by Design

`[PRIVACY, MINIMUM SUPPORT, CALIBRATION, POPULARITY BIAS, HUMAN OVERSIGHT, REJECTION WORKFLOW]`

---

# BAB IV — PERENCANAAN IMPLEMENTASI

## 4.1 Strategi Pengembangan

`[DATA -> ANNOTATION -> BASELINES -> INDOBERT -> ENGINE -> PRODUCT -> EVALUATION]`

## 4.2 Work Breakdown Structure

| Fase | Aktivitas | Output | PIC | Status |
| --- | --- | --- | --- | --- |
| Data | Inventory, EDA, cleaning | `[ ]` | `[ ]` | `[ ]` |
| Annotation | Guideline, labels, agreement | `[ ]` | `[ ]` | `[ ]` |
| Model | Baselines, IndoBERT, calibration | `[ ]` | `[ ]` | `[ ]` |
| Engine | Aggregation, scoring, ranking | `[ ]` | `[ ]` | `[ ]` |
| Product | API, UI, deployment | `[ ]` | `[ ]` | `[ ]` |

## 4.3 Timeline

| Hari/Tanggal | Target | Definition of Done |
| --- | --- | --- |
| `[H1]` | Data dan EDA | `[OUTPUT]` |
| `[H2]` | Annotation | `[OUTPUT]` |
| `[H3]` | Baselines | `[OUTPUT]` |
| `[H4]` | IndoBERT | `[OUTPUT]` |
| `[H5]` | Intelligence engine | `[OUTPUT]` |
| `[H6]` | Product integration | `[OUTPUT]` |
| `[H7]` | Evaluation/submission | `[OUTPUT]` |

## 4.4 Teknologi dan Sumber Daya

| Layer | Teknologi | Alasan |
| --- | --- | --- |
| Data | Python, Pandas/Polars, Parquet | `[ALASAN]` |
| Baseline | scikit-learn | `[ALASAN]` |
| Model | PyTorch, Transformers, IndoBERT | `[ALASAN]` |
| Experiment | Google Colab GPU | `[ALASAN]` |
| API | FastAPI | `[ALASAN]` |
| Web | Next.js, Leaflet | `[ALASAN]` |
| Deployment | Docker, DGX B200 | `[ALASAN]` |

## 4.5 Integrasi dan Deployment

`[BATCH UNTUK DASHBOARD, REAL-TIME ANALYZER, JSON/DB, VERSIONING]`

```text
sipature-web -> Next.js
sipature-api -> FastAPI + inference
sipature-db  -> PostgreSQL/PostGIS atau SQLite MVP
```

`[DOCKER, OFFLINE MODEL, HEALTH CHECK, CPU/MAP FALLBACK]`

## 4.6 Rencana Pilot

1. Pilih 5–10 destinasi beragam.
2. Generate historical alerts.
3. Expert menilai tanpa melihat model ranking.
4. Bandingkan expert vs model.
5. Field verification top alerts.
6. Catat confirmed/rejected/uncertain.
7. Refine taxonomy, threshold, bobot.

## 4.7 Risiko dan Mitigasi

| Risiko | Kemungkinan | Dampak | Mitigasi | Residual Risk |
| --- | --- | --- | --- | --- |
| Sparse labels | `[L/M/H]` | `[L/M/H]` | Sampling/weights | `[ ]` |
| Popularity bias | `[ ]` | `[ ]` | Smoothing/min support | `[ ]` |
| False alert | `[ ]` | `[ ]` | Alert threshold | `[ ]` |
| Entity false merge | `[ ]` | `[ ]` | Conservative matching | `[ ]` |
| Data staleness | `[ ]` | `[ ]` | Freshness indicator | `[ ]` |
| Deployment failure | `[ ]` | `[ ]` | Docker/offline fallback | `[ ]` |

## 4.8 Keberlanjutan

`[FEEDBACK DARI VERIFIED/REJECTED ALERT, RETRAINING, ADOPTION, COST, GOVERNANCE]`

---

# BAB V — MODELLING

## 5.1 Pipeline Modelling

```text
Gold data -> schema validation -> destination split
-> Keyword + TF-IDF -> IndoBERT aspect
-> threshold calibration -> polarity -> severity
-> locked test -> batch inference
```

**Gambar 5.1. Training Flow**  
`[SISIPKAN DIAGRAM]`

## 5.2 Data Preparation

### 5.2.1 Cleaning

`[NFKC, WHITESPACE, NEGATION, DUPLICATES, RATING-ONLY]`

### 5.2.2 Entity Resolution

`[BLOCKING, SIMILARITY, THRESHOLD, MANUAL REVIEW, FALSE MERGE]`

### 5.2.3 Sampling dan Annotation

`[STRATIFICATION, RARE ASPECTS, PILOT, DOUBLE ANNOTATION, ADJUDICATION]`

### 5.2.4 Inter-Annotator Agreement

| Task | Metric | Hasil | Interpretasi |
| --- | --- | ---: | --- |
| Aspect | Kappa/Jaccard | `[ ]` | `[ ]` |
| Polarity | Kappa | `[ ]` | `[ ]` |
| Severity | Weighted kappa | `[ ]` | `[ ]` |

## 5.3 Leakage-Safe Split

| Split | Destinasi | Review | Persentase |
| --- | ---: | ---: | ---: |
| Train | `[N]` | `[N]` | `[ ]` |
| Validation | `[N]` | `[N]` | `[ ]` |
| Test | `[N]` | `[N]` | `[ ]` |

`[JELASKAN DESTINATION GROUPING, DUPLICATE GROUPS, RARE LABEL DISTRIBUTION]`

## 5.4 Keyword Baseline

`[LEXICON, NEGATION WINDOW, CONTRAST, INTENSITY, LIMITATIONS]`

## 5.5 TF-IDF dan Logistic Regression

`[WORD/CHAR N-GRAM, ONE-VS-REST, CLASS WEIGHTS, TUNING]`

## 5.6 IndoBERT Aspect Detection

```text
IndoBERT -> pooled representation -> linear head -> sigmoid
```

`[MODEL ID, LICENSE, MAX LENGTH, BCE/POS_WEIGHT]`

## 5.7 Aspect-Conditioned Polarity

```text
[ASPECT=SANITATION] + review -> positive | negative | neutral
```

`[INSTANCE GENERATION, MODEL, LOSS, DISTRIBUTION]`

## 5.8 Severity Model

`[LOW/MEDIUM/HIGH ATAU BINARY; ALASAN BERDASARKAN SUPPORT/AGREEMENT]`

## 5.9 Hyperparameter dan Tracking

| Parameter | Keyword | TF-IDF | IndoBERT |
| --- | --- | --- | --- |
| Seed | `[ ]` | `[ ]` | `[ ]` |
| Features/model | `[ ]` | `[ ]` | `[MODEL ID]` |
| Learning rate | N/A | N/A | `[ ]` |
| Batch size | N/A | N/A | `[ ]` |
| Epoch | N/A | N/A | `[ ]` |
| Threshold | `[ ]` | `[ ]` | Per label |

## 5.10 Class Imbalance

`[CLASS WEIGHT, POS_WEIGHT, OVERSAMPLING/FOCAL LOSS YANG BENAR-BENAR DIUJI]`

## 5.11 Threshold dan Calibration

`[DETECTION VS ALERT THRESHOLD, VALIDATION-ONLY SELECTION, CALIBRATION]`

## 5.12 Inference, Evidence, Aggregation

`[OUTPUT SCHEMA, PROBABILITIES, MODEL VERSION, VERBATIM SPANS, PROVENANCE, SMOOTHING]`

## 5.13 Reproducibility

`[SEED, GIT COMMIT, DATA/CONFIG HASH, MODEL VERSION, PACKAGES, HARDWARE]`

---

# BAB VI — EVALUASI MODEL

## 6.1 Protokol Evaluasi

> Arahan: Jelaskan locked test set, baseline pada split sama, validation-only tuning, dan kapan test dibuka.

`[PROTOKOL EVALUASI]`

## 6.2 Aspect Detection

| Model | Micro F1 | Macro F1 | Exact Match | Hamming Loss | Alert Precision |
| --- | ---: | ---: | ---: | ---: | ---: |
| Keyword | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| TF-IDF | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| IndoBERT | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |

**Gambar 6.1. Model Comparison**  
`[GROUPED BAR + INTERPRETASI]`

## 6.3 Evaluasi Per Label

| Aspect | Support | Precision | Recall | F1 | Threshold |
| --- | ---: | ---: | ---: | ---: | ---: |
| cleanliness | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| sanitation | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| `[ASPECT]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` | `[ ]` |

**Gambar 6.2. Per-Label F1 dan Support**  
`[VISUAL + LABEL LEMAH/KUAT]`

## 6.4 Polarity Evaluation

| Metric | Hasil |
| --- | ---: |
| Macro F1 | `[ ]` |
| Balanced Accuracy | `[ ]` |
| Negative Precision | `[ ]` |

**Gambar 6.3. Polarity Confusion Matrix**  
`[MATRIX + INTERPRETASI]`

## 6.5 Severity Evaluation

| Metric | Hasil |
| --- | ---: |
| Macro F1 | `[ ]` |
| High-severity precision | `[ ]` |
| High-severity recall | `[ ]` |
| Weighted kappa | `[ ]` |

**Gambar 6.4. Severity Confusion Matrix**  
`[SOROT HIGH->LOW ERRORS]`

## 6.6 Precision-Recall dan Threshold

**Gambar 6.5. Precision-Recall Curves**  
`[ASPEK UTAMA + OPERATING POINT]`

**Gambar 6.6. Threshold vs Precision/Recall/F1**  
`[ALASAN DETECTION/ALERT THRESHOLD]`

## 6.7 Calibration

| Metric | Hasil |
| --- | ---: |
| Expected Calibration Error | `[ ]` |
| Brier Score | `[ ]` |

**Gambar 6.7. Reliability Diagram**  
`[INTERPRETASI CONFIDENCE]`

## 6.8 Entity Resolution Evaluation

| Metric | Hasil |
| --- | ---: |
| Pairwise Precision | `[ ]` |
| Pairwise Recall | `[ ]` |
| Pairwise F1 | `[ ]` |
| False-merge rate | `[ ]` |

`[JELASKAN SAMPLING PAIRS DAN ERROR PALING BERISIKO]`

## 6.9 Intervention Ranking Evaluation

| Metric | Hasil | Ground Truth |
| --- | ---: | --- |
| NDCG@5 | `[ ]` | `[EXPERT CASES]` |
| NDCG@10 | `[ ]` | `[EXPERT CASES]` |
| Spearman | `[ ]` | `[EXPERT RANKING]` |
| Kendall's tau | `[ ]` | `[EXPERT RANKING]` |

**Gambar 6.8. Expert vs Model Ranking**  
`[SCATTER/NDCG COMPARISON]`

## 6.10 System-Level Evaluation

| Metric | Hasil | Metode |
| --- | ---: | --- |
| Evidence correctness | `[ ]` | Human review |
| Unsupported alert rate | `[ ]` | Human review |
| Intervention relevance | `[ ]` | Expert review |
| Analysis time saved | `[ ]` | User test/pilot |

**Gambar 6.9. Evidence Correctness**  
`[SUPPORTED/PARTIAL/UNSUPPORTED STACKED BAR]`

## 6.11 Latency dan Resource

| Komponen | p50 | p95 | Memory | Hardware |
| --- | ---: | ---: | ---: | --- |
| Model inference | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| API | `[ ]` | `[ ]` | `[ ]` | `[ ]` |
| Page interaction | `[ ]` | `[ ]` | N/A | `[ ]` |

## 6.12 Training/Learning Curves

**Gambar 6.10. Train/Validation Loss dan F1**  
`[ANALISIS OVERFITTING DAN EARLY STOPPING]`

**Gambar 6.11. Learning Curve**  
`[JIKA TERSEDIA: APAKAH ANNOTATION TAMBAHAN MASIH MEMBANTU]`

## 6.13 Error Analysis

| Error Category | Jumlah | Contoh Anonim | Mitigasi |
| --- | ---: | --- | --- |
| Negation | `[ ]` | `[ ]` | `[ ]` |
| Implicit complaint | `[ ]` | `[ ]` | `[ ]` |
| Mixed language | `[ ]` | `[ ]` | `[ ]` |
| Aspect boundary | `[ ]` | `[ ]` | `[ ]` |
| Annotation disagreement | `[ ]` | `[ ]` | `[ ]` |

`[BAHAS 50 FP, 50 FN, HIGH-SEVERITY ERRORS, RESIDUAL RISK]`

## 6.14 Kesimpulan Evaluasi

> Arahan: Jawab apakah primary model benar-benar lebih baik dari baseline dan apakah layak menjadi early-warning layer. Jangan menyembunyikan label lemah.

`[KESIMPULAN EVALUASI]`

---

# BAB VII — HASIL DAN PEMBAHASAN

## 7.1 Hasil Data Engineering

`[RAW -> CLEAN -> LINKED COUNTS, COVERAGE, DATA QUALITY IMPROVEMENT]`

**Gambar 7.1. Final Data Coverage Map**  
`[SUFFICIENT/LOW/INSUFFICIENT/MISSING COORDINATES]`

## 7.2 Hasil Model dan Pemilihan Model

`[SINTESIS KEYWORD VS TF-IDF VS INDOBERT, TRADE-OFF ACCURACY/LATENCY/EXPLAINABILITY]`

## 7.3 Hasil Destination-Level Signals

| Indikator | Hasil |
| --- | ---: |
| Destinasi dianalisis | `[ ]` |
| Destinasi sufficient data | `[ ]` |
| High/Critical alerts | `[ ]` |
| Alerts dengan evidence cukup | `[ ]` |
| Dominant issue | `[ ]` |

**Gambar 7.2. Distribusi Sinyal per Aspek**  
`[VISUAL + INTERPRETASI]`

## 7.4 Studi Kasus Utama

### 7.4.1 Kondisi Awal

`[DESTINASI, RATING, REVIEW VOLUME, METADATA]`

### 7.4.2 Sinyal Tersembunyi

`[ASPECT, POLARITY, SEVERITY, CONFIDENCE, SUPPORT]`

### 7.4.3 Evidence

> `[KUTIPAN VERBATIM ANONIM]`

`[JELASKAN MENGAPA EVIDENCE MENDUKUNG ALERT]`

### 7.4.4 Priority Explanation

`[KONTRIBUSI SEVERITY, FREQUENCY, CONFIDENCE, PERSISTENCE, EXPOSURE, GAP]`

**Gambar 7.3. Priority Component Waterfall**  
`[SISIPKAN VISUAL]`

### 7.4.5 Recommended Verification dan Intervention

`[APA YANG HARUS DIVERIFIKASI DAN CANDIDATE ACTION; BUKAN JAMINAN]`

## 7.5 Hasil Produk SIPATURE

### 7.5.1 Overview dan Map

`[SCREENSHOT + VALUE]`

### 7.5.2 Destination Evidence

`[SCREENSHOT + VALUE]`

### 7.5.3 Intervention Queue

`[SCREENSHOT + VALUE]`

### 7.5.4 Simulator

`[SCREENSHOT + ASUMSI + NON-CAUSAL DISCLAIMER]`

## 7.6 Pembahasan Hipotesis

| Hipotesis | Hasil | Status | Pembahasan |
| --- | --- | --- | --- |
| H1 | `[HASIL]` | Didukung/tidak | `[ALASAN]` |
| H2 | `[HASIL]` | Didukung/tidak | `[ALASAN]` |
| H3 | `[HASIL]` | Didukung/belum diuji | `[ALASAN]` |

## 7.7 Dampak dan Relevansi

`[DAMPAK PADA EFISIENSI INSPEKSI, KUALITAS PENGELOLAAN, KEBERLANJUTAN, STAKEHOLDER]`

## 7.8 Keterbatasan

- `[LABEL/DATA SPARSITY]`
- `[PLATFORM/POPULARITY BIAS]`
- `[MODEL ERROR/CALIBRATION]`
- `[STALE DATA]`
- `[ENTITY MATCHING]`
- `[NO CAUSAL CLAIM]`
- `[PILOT BELUM/TERBATAS]`

## 7.9 Implikasi dan Rencana Lanjut

`[ANNOTATION TAMBAHAN, THRESHOLD, PILOT, FEEDBACK LOOP, DEPLOYMENT, GOVERNANCE]`

## 7.10 Kesimpulan Hasil

`[RINGKAS TEMUAN, NILAI SOLUSI, DAN APA YANG BELUM TERBUKTI]`

---

# BAB VIII — DEKLARASI PENGGUNAAN AI

## 8.1 Pernyataan Penggunaan AI

> Arahan: Nyatakan semua AI yang digunakan untuk model, coding, penulisan, annotation suggestion, atau visual. Jangan menyembunyikan penggunaan AI generatif.

`[PERNYATAAN RESMI PENGGUNAAN AI]`

## 8.2 AI dalam Solusi SIPATURE

| Komponen | Model/Metode | Fungsi | Status |
| --- | --- | --- | --- |
| Aspect detection | `[MODEL]` | Multilabel classification | Trained/baseline |
| Polarity | `[MODEL]` | Aspect-level polarity | `[STATUS]` |
| Severity | `[MODEL]` | Negative issue severity | `[STATUS]` |
| Ranking | `[METODE]` | Transparent priority | Deterministic |

## 8.3 AI dalam Proses Pengembangan

| Tool | Penggunaan | Verifikasi Manusia | Output yang Dipakai |
| --- | --- | --- | --- |
| `[TOOL]` | `[CODING/IDE/ANNOTATION SUGGESTION]` | `[PROSES REVIEW]` | `[OUTPUT]` |

## 8.4 Batas Penggunaan AI

- AI/LLM tidak menjadi ground truth annotation tanpa human verification.
- AI tidak membuat evidence baru.
- AI tidak menentukan tindakan lapangan tanpa human review.
- Simulator bukan causal prediction.
- `[BATASAN LAIN]`

## 8.5 Human Oversight

`[JELASKAN ANNOTATION, ADJUDICATION, ERROR REVIEW, ALERT VERIFICATION, REJECTION WORKFLOW]`

## 8.6 Privasi dan Etika

`[ANONYMIZATION, PII EXCLUSION, PROVENANCE, REPUTATIONAL HARM, POPULARITY BIAS]`

## 8.7 Lisensi dan Data Eksternal

| Komponen | Sumber | Lisensi | Tanggal Akses | Penggunaan |
| --- | --- | --- | --- | --- |
| IndoBERT `[ID]` | `[URL]` | `[LICENSE]` | `[DATE]` | Model |
| Basemap | `[SOURCE]` | `[LICENSE]` | `[DATE]` | Map |
| `[DATA/TOOL]` | `[SOURCE]` | `[LICENSE]` | `[DATE]` | `[USE]` |

## 8.8 Intended Use, Limitations, Misuse Risks

**Intended users:** `[PENGGUNA]`  
**Intended use:** `[PENGGUNAAN]`  
**Out-of-scope:** `[BATAS]`  
**Known limitations:** `[LIMITATIONS]`  
**Misuse risks:** `[RISKS]`  
**Mitigations:** `[MITIGATIONS]`

## 8.9 Deklarasi Kejujuran Hasil

> Kami menyatakan bahwa seluruh metric yang dilaporkan berasal dari evaluasi aktual pada data dan protokol yang dijelaskan. Target, asumsi simulator, dan hasil aktual dibedakan secara eksplisit. Kutipan evidence berasal dari dataset dan tidak difabrikasi.

`[NAMA TIM / TANGGAL / PERSETUJUAN ANGGOTA]`

---

# DAFTAR PUSTAKA

> Arahan: Gunakan satu format konsisten, misalnya IEEE atau APA. Sertakan paper IndoBERT, multilabel classification, calibration, Wilson/Bayesian smoothing, ranking metrics, Responsible AI, dan sumber eksternal.

1. `[REFERENSI]`
2. `[REFERENSI]`

---

# LAMPIRAN

## Lampiran A — Data Dictionary

`[FIELD, TYPE, DEFINISI, CONTOH, MISSING VALUE]`

## Lampiran B — Known Data Issues

`[ISSUE, FILE, JUMLAH, DAMPAK, HANDLING]`

## Lampiran C — Annotation Guideline Ringkas

`[TAXONOMY, DEFINISI, EXAMPLES, BOUNDARIES]`

## Lampiran D — Experiment Configuration

`[MODEL ID, HYPERPARAMETER, SEED, HASH, ENVIRONMENT]`

## Lampiran E — Full Metrics

`[PER-LABEL CLASSIFICATION REPORT, CALIBRATION, LATENCY]`

## Lampiran F — Error Cases

`[ANONYMIZED FP/FN/HIGH-SEVERITY ERRORS]`

## Lampiran G — Architecture dan API

`[COMPONENT, ENDPOINTS, SCHEMA, DEPLOYMENT]`

## Lampiran H — Reproducibility Instructions

```text
[ENVIRONMENT SETUP]
[DATA PLACEMENT]
[CLEANING COMMAND]
[TRAINING COMMAND]
[EVALUATION COMMAND]
[INFERENCE COMMAND]
[APP RUN COMMAND]
```

## Lampiran I — Rubric Traceability

| Rubrik | Bab/Subbab Bukti |
| --- | --- |
| Kebaruan/problem framing | Bab I, II, III.9 |
| Dampak/relevansi | Bab I.7, III.8, VII.7 |
| AI/data quality | Bab II.5–8, V, VI |
| Kelayakan/keberlanjutan | Bab IV, VII.9 |
| Pemanfaatan data Toba | Bab II.5–7, V.2, VII.1 |
| Komunikasi/demo/dokumentasi | Ringkasan, Bab III, VII, Lampiran |

---

## Finalisasi Dokumen

- [ ] Delapan bab wajib tersedia dan berurutan.
- [ ] Seluruh arahan/placeholder yang tidak dipakai dihapus.
- [ ] Semua hasil adalah aktual dan traceable.
- [ ] Tidak ada identitas institusi pendidikan.
- [ ] Tidak ada PII reviewer.
- [ ] Seluruh gambar/tabel terbaca dan dirujuk dalam teks.
- [ ] Target, asumsi, dan hasil aktual berbeda label.
- [ ] Referensi/lisensi lengkap.
- [ ] PDF akhir maksimal 25 MB.
- [ ] Nama file: `[NamaTim] - LaporanAnalisis.pdf`.
