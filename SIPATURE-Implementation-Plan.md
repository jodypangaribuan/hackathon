# SIPATURE

## Rencana Implementasi Data, AI, Training, dan Produk

> SIPATURE mengubah ulasan wisatawan menjadi sinyal peringatan dini yang dapat dijelaskan, prioritas verifikasi lapangan, dan kandidat intervensi untuk kualitas destinasi Danau Toba.

## 1. Sasaran Sistem

Pertanyaan utama:

> Masalah destinasi mana yang perlu diverifikasi terlebih dahulu, apa buktinya, seberapa yakin sistem, dan intervensi apa yang relevan?

Unit analisis:

| Tingkat | Unit | Output |
| --- | --- | --- |
| Review | Satu ulasan | Aspek, polaritas, severity, confidence |
| Destination-aspect | Satu isu pada satu destinasi | Frekuensi, persistence, evidence, health |
| Destination | Satu destinasi | Tourism Health dan prioritas intervensi |

Rantai pembuktian:

```text
Raw CSV -> EDA -> cleaning -> entity resolution -> annotation
-> destination-based split -> baseline -> IndoBERT -> calibration
-> test evaluation -> batch inference -> destination aggregation
-> priority engine -> API -> aplikasi -> verifikasi manusia
```

SIPATURE bukan chatbot, sistem booking, sensor lingkungan, atau prediktor kausal keberhasilan intervensi.

## 2. Struktur Proyek

```text
hackathon/
├── Datasets/
├── sipature-app/
├── ml/
│   ├── configs/
│   ├── data/{raw,interim,processed,annotations,splits}/
│   ├── notebooks/
│   │   ├── 01_data_inventory.ipynb
│   │   ├── 02_review_eda.ipynb
│   │   ├── 03_metadata_eda.ipynb
│   │   ├── 04_entity_resolution.ipynb
│   │   ├── 05_annotation_audit.ipynb
│   │   └── 06_error_analysis.ipynb
│   ├── src/
│   │   ├── ingest.py
│   │   ├── clean.py
│   │   ├── entities.py
│   │   ├── sampling.py
│   │   ├── split.py
│   │   ├── train_tfidf.py
│   │   ├── train_indobert.py
│   │   ├── calibrate.py
│   │   ├── evaluate.py
│   │   ├── infer.py
│   │   ├── aggregate.py
│   │   └── prioritize.py
│   ├── tests/
│   └── artifacts/{models,metrics,figures,reports}/
└── docs/
    ├── data-dictionary.md
    ├── annotation-guideline.md
    ├── model-card.md
    └── responsible-ai.md
```

Notebook untuk eksplorasi. Script untuk pipeline reproducible. Raw data tidak dimodifikasi.

## 3. Inventarisasi Data

| Dataset | Penggunaan |
| --- | --- |
| `wisata-v2.csv` | Ulasan destinasi, training dan inference utama |
| `resto-hotel-v2.csv` | Ulasan layanan pendukung |
| `wisata-metadata.csv` | Identitas, koordinat, tipe, rating, status, tiket, jam |
| `tempat-wisata-v1.csv` | Fasilitas dan metadata tambahan |
| `waktu operasional destinasi.csv` | Jam dan fasilitas |
| `hotel-metadata.csv` | Konteks akomodasi dan proximity |
| `resto-metadata.csv` | Konteks kuliner dan proximity |
| `transportasi.csv` | Konteks akses dan transportasi |
| Artikel/informasi destinasi | Konteks, bukan model ground truth |

Untuk setiap file catat encoding, separator, ukuran, schema, missing values, duplikasi, rentang rating/tanggal, entitas unik, koordinat, nilai abnormal, dan hash sumber.

Output:

```text
artifacts/reports/data_inventory.csv
artifacts/reports/known_data_issues.csv
docs/data-dictionary.md
```

Gunakan `encoding="utf-8-sig"`. Jangan memakai `errors="ignore"` tanpa audit.

## 4. Exploratory Data Analysis

EDA harus menghasilkan keputusan teknis, bukan hanya grafik.

### 4.1 EDA Struktur

Periksa embedded header, kolom `Unnamed`, decimal-comma rating, koordinat string, variasi nama tempat, tanggal relatif, mixed format, review kosong, dan outlier panjang teks.

Ringkasan minimum:

- Total review, review berteks, dan rating-only.
- Total destinasi dan destinasi berkoordinat.
- Missing-value matrix.
- Exact/near-duplicate summary.
- Data coverage per file dan destinasi.

### 4.2 EDA Review

Analisis:

- Distribusi panjang karakter/token.
- Distribusi rating 1–5.
- Volume review per destinasi.
- Bahasa Indonesia, Batak, Inggris, dan campuran.
- Unigram, bigram, trigram.
- Negasi dan contrast marker: `tidak`, `kurang`, `tetapi`, `namun`, `tapi`.
- Review generik, repeated text, spam, dan review sangat panjang.
- Recency dan freshness.
- Review volume vs rating dan complaint-keyword rate.

### 4.3 EDA Kandidat Aspek

Gunakan seed keywords hanya untuk mengukur support awal, mencari sinonim lokal, rare aspects, dan implied complaints. Output keyword bukan ground truth.

```python
SEEDS = {
  "cleanliness": ["bersih", "kotor", "jorok", "bau"],
  "waste": ["sampah", "plastik", "berserakan"],
  "sanitation": ["toilet", "wc", "kamar mandi", "mck"],
  "crowding": ["ramai", "padat", "penuh", "antre"],
  "access": ["akses", "jalan", "rusak", "berlubang"],
  "parking": ["parkir", "parkiran"],
  "safety": ["aman", "bahaya", "licin", "rawan"],
  "price_transparency": ["harga", "tarif", "tiket", "pungutan"],
  "staff_service": ["pelayanan", "petugas", "ramah"],
  "maintenance": ["terawat", "rusak", "perawatan"]
}
```

### 4.4 EDA Metadata dan Geospasial

Periksa status, fee, hours, facilities, koordinat invalid/outlier, konflik metadata, dan entitas bernama mirip. Plot destinasi, hotel, restoran, dan transportasi. Hitung fasilitas terdekat, fasilitas dalam radius, serta supporting-service density menggunakan Haversine.

### 4.5 Audit Bias

- Popularity bias dari volume review.
- Dominasi rating bintang 5.
- Tempat tanpa teks.
- Vocabulary leakage dari destinasi.
- Review lama vs baru.
- Platform bias pengguna Google Maps.
- Kategori destinasi dengan data minim.

Output: `eda_report.html`, figures, dan known-data-issues report.

## 5. Data Cleaning

Simpan raw dan normalized values:

```text
raw_review_text, normalized_review_text
raw_rating, normalized_rating
raw_date, normalized_date
source_file, source_row_id
```

Langkah:

1. Unicode normalization NFKC.
2. Normalisasi whitespace/newline dan control characters.
3. Pertahankan punctuation, typo, bahasa campuran, dan negasi.
4. Jangan stemming/stopword removal untuk IndoBERT.
5. Uji stopword treatment terpisah untuk TF-IDF.
6. Konversi `4,5` menjadi `4.5`; nilai di luar 0–5 masuk quarantine.
7. Hapus exact duplicate teknis.
8. Tandai near/repeated duplicate dengan `duplicate_group_id`.
9. Pisahkan `text_training_pool` dan `rating_only_pool`.

Kata `tidak`, `kurang`, `belum`, `bukan`, dan `tanpa` tidak boleh dihapus.

Output:

```text
clean_reviews.parquet
clean_metadata.parquet
quarantine_rows.parquet
cleaning_summary.json
```

## 6. Entity Resolution

Tujuan: satu `destination_id` untuk entitas lintas file.

Tahapan:

1. Normalisasi nama tanpa menghapus token lokasi pembeda.
2. Candidate blocking berdasarkan nama, wilayah, kategori, dan radius koordinat.
3. Hitung exact match, token Jaccard, Jaro-Winkler, address similarity, coordinate distance, dan category agreement.
4. Terapkan conservative matching.
5. Manual review untuk ambiguous pairs.

Contoh aturan:

```text
exact name + distance < 200 m              -> auto-match
name similarity > 0.90 + address agreement -> auto-match
similarity 0.75-0.90                       -> manual review
large distance + generic name              -> no-match
```

Simpan source row, canonical ID/name, aliases, match score/rule, distance, dan review status. Evaluasi pairwise precision/recall/F1 dan false-merge rate. False merge lebih berbahaya daripada unresolved match.

## 7. Taxonomy Label

Taxonomy MVP:

| Grup | Label |
| --- | --- |
| Lingkungan | `cleanliness`, `waste`, `sanitation`, `crowding` |
| Infrastruktur | `access`, `parking`, `public_facilities` |
| Pengalaman | `scenery`, `comfort`, `safety`, `price_transparency` |
| Operasional | `staff_service`, `maintenance`, `opening_hours` |

Task model:

1. Multilabel aspect detection.
2. Aspect-conditioned polarity: `positive | negative | neutral`.
3. Negative severity: `low | medium | high`.

Jika severity agreement rendah, gunakan `non-severe | severe`. Jangan membuat kelas kombinasi seperti `sanitation_negative_high`.

## 8. Annotation Guideline dan Sampling

Guideline per label harus memuat definisi, in/out scope, contoh positive/negative/neutral, boundary cases, negasi, sarcasm, implied complaint, konflik aspek, dan severity.

Format JSONL:

```json
{
  "review_id": "review_00001",
  "destination_id": "dest_001",
  "text": "Pemandangan indah tetapi toiletnya kotor.",
  "labels": [
    {"aspect": "scenery", "polarity": "positive", "severity": null},
    {"aspect": "sanitation", "polarity": "negative", "severity": "high"}
  ],
  "annotator_id": "A1",
  "annotation_version": "v1.0"
}
```

Target: ideal 1.500–2.500; minimum 1.000–1.200 review. Gunakan stratified sampling berdasarkan destination, rating, panjang, candidate keywords, tipe, bahasa, recency, dan rare aspects.

Contoh komposisi:

| Kelompok | Proporsi |
| --- | ---: |
| Rating 1–2 | 25% |
| Rating 3 | 20% |
| Rating 4–5 dengan complaint keyword | 25% |
| Rating 4–5 tanpa keyword | 15% |
| Rare-aspect oversampling | 15% |

## 9. Annotation dan Agreement

1. Pilot 100–150 review oleh semua annotator.
2. Analisis disagreement dan revisi guideline.
3. Double-annotate 15–20% main dataset.
4. Single-annotate sisanya.
5. Adjudicator menyelesaikan konflik.
6. Versikan taxonomy dan guideline.

Metrics:

- Per-label Cohen's kappa dan Jaccard untuk aspect multilabel.
- Cohen's kappa atau Krippendorff's alpha untuk polarity/severity.

Target praktis:

```text
Aspect kappa >= 0.70
Polarity kappa >= 0.75
Severity kappa >= 0.60
```

Audit schema, duplicate IDs, valid taxonomy, severity-only-for-negative, destination IDs, support per label, dan adjudication status.

## 10. Train, Validation, Test Split

Jangan random split per review. Split berdasarkan destination untuk mencegah vocabulary dan issue leakage.

```text
70% destination -> train
15% destination -> validation
15% destination -> test
```

Constraints:

- Satu destination hanya ada pada satu split.
- Near-duplicate group hanya ada pada satu split.
- Gunakan multilabel group stratification jika memungkinkan.
- Pastikan rare labels muncul pada validation/test.
- Kunci test set sebelum tuning.

Simpan random seed, destination list, label distribution, dataset hash, dan annotation version pada `split_manifest.json`.

## 11. Baseline Models

### 11.1 Keyword Baseline

Implementasikan aspect lexicon, negation window, contrast markers, sentiment/intensity words, dan severity rules. Evaluasi pada test set yang sama dengan model lain.

### 11.2 TF-IDF Baseline

Bandingkan word unigram/bigram, char n-gram 3–5, dan kombinasi keduanya.

```python
OneVsRestClassifier(
  LogisticRegression(class_weight="balanced", max_iter=2000)
)
```

Aspect detection menggunakan binary classifier per label. Polarity dapat memakai model global dengan token aspek:

```text
[ASPECT=sanitation] Pemandangannya indah tetapi toiletnya kotor
```

Severity dimulai dari rule atau binary classifier jika support terbatas. Tuning `C`, `min_df`, `max_features`, n-gram, dan threshold pada validation set.

## 12. Primary Model: IndoBERT

Dokumentasikan model ID, lisensi, tokenizer, ukuran, maximum length, dan pretraining source.

Arsitektur MVP:

```text
Model A: IndoBERT -> multilabel aspect head -> sigmoid
Model B: [ASPECT] + review -> polarity classifier
Model C: [ASPECT] + negative review -> severity classifier
```

Aspect loss: `BCEWithLogitsLoss(pos_weight=...)`.

Konfigurasi awal:

```yaml
max_length: 192
batch_size: 16
gradient_accumulation: 2
learning_rate: 2e-5
weight_decay: 0.01
epochs: 4
warmup_ratio: 0.1
early_stopping_patience: 2
seed: 42
mixed_precision: bf16
```

Mitigasi imbalance diuji berurutan: `pos_weight`, oversampling, focal loss, lalu augmentation terbatas. Simpan seed, git commit, data hash, annotation version, config, logs, checkpoint, tokenizer, environment, hardware, dan durasi.

## 13. Flow Training

```text
Gold annotations
-> schema validation
-> destination group split
-> keyword baseline + TF-IDF baseline
-> baseline comparison
-> IndoBERT tokenization
-> train aspect classifier
-> select checkpoint by validation Macro F1
-> calibrate threshold per aspect
-> create aspect-conditioned polarity instances
-> train polarity classifier
-> create negative-aspect severity instances
-> train severity classifier
-> lock config and thresholds
-> evaluate once on test set
-> error analysis
-> model card and export
```

## 14. Threshold dan Calibration

Jangan otomatis memakai threshold 0.5. Cari threshold per aspek pada validation set. Pisahkan `detection_threshold` dan `alert_threshold` bila perlu.

```text
sanitation detected: p >= 0.38
sanitation alert: p >= 0.72 + minimum evidence
```

Early warning mengutamakan alert precision karena false alert dapat merugikan reputasi. Evaluasi temperature/Platt/isotonic calibration dengan ECE, Brier score, dan reliability diagram.

## 15. Evaluasi Model

Aspect detection:

- Micro/Macro/per-label F1, precision, recall.
- Exact-match ratio dan Hamming loss.
- Precision pada alert threshold.

Polarity:

- Macro F1, per-class metrics, confusion matrix, per-aspect F1.

Severity:

- Macro F1, high-severity precision/recall, confusion matrix, weighted kappa.

Perbandingan wajib:

| Model | Micro F1 | Macro F1 | Alert Precision | Latency |
| --- | ---: | ---: | ---: | ---: |
| Keyword | aktual | aktual | aktual | aktual |
| TF-IDF | aktual | aktual | aktual | aktual |
| IndoBERT | aktual | aktual | aktual | aktual |

Target bukan hasil. Laporkan angka aktual secara jujur.

## 16. Error Analysis dan Model Selection

Audit minimal 50 false positive, 50 false negative, semua high-severity errors, rare labels, dan mixed-language errors. Kelompokkan negation, implied complaint, sarcasm, typo, aspect boundary, missing context, annotation error, named-entity leakage, dan text-rating conflict.

Pilih model berdasarkan Macro F1, high-severity precision, calibration, evidence correctness, latency, offline capability, stabilitas, explainability, dan unsupported-alert rate; bukan satu metric saja.

## 17. Batch Inference dan Evidence

Setelah model dikunci:

1. Load seluruh review berteks.
2. Prediksi aspek dan terapkan threshold.
3. Prediksi polarity untuk aspek terdeteksi.
4. Prediksi severity untuk aspek negatif.
5. Simpan probability lengkap, model version, timestamp, review dan destination ID.

Schema output:

```json
{
  "review_id": "review_001",
  "destination_id": "dest_001",
  "model_version": "sipature-v1.0",
  "predictions": [{
    "aspect": "sanitation",
    "aspect_probability": 0.91,
    "polarity": "negative",
    "polarity_probability": 0.88,
    "severity": "high",
    "severity_probability": 0.79
  }]
}
```

Evidence harus verbatim, high-confidence, representatif, tidak duplikat, anonim, singkat, dan memiliki provenance: source file/row, review ID, text span, aspect, confidence, date.

## 18. Destination Aggregation

Agregasi per `destination_id + aspect + time_window`:

- mention/negative/severe count.
- Complaint dan severe rate.
- Mean confidence.
- Unique review count.
- Persistence, freshness, coverage.

```text
review_weight = model_confidence * severity_weight * freshness_weight * duplicate_discount
```

Severity weight awal: low 1.0, medium 1.5, high 2.0. Lakukan sensitivity analysis.

Bayesian smoothing:

```text
SmoothedComplaintRate =
(negative_count + alpha * global_rate) / (total_mentions + alpha)
```

Ini mencegah destinasi dengan dua review negatif menjadi prioritas ekstrem.

## 19. Health dan Priority Engine

Aspect Health:

```text
AspectHealth = 100 * (1 - SmoothedWeightedComplaintRate)
```

Tourism Health:

```text
0.25 environmental
+ 0.20 sanitation
+ 0.15 infrastructure
+ 0.15 safety
+ 0.15 operational
+ 0.10 visitor_experience
```

Missing component tidak dianggap 100; tampilkan `Insufficient Data` dan component scores.

Priority Score MVP:

```text
0.25 severity
+ 0.20 complaint_frequency
+ 0.15 model_confidence
+ 0.15 persistence
+ 0.10 visitor_exposure
+ 0.10 facility_gap
+ 0.05 feasibility
```

Normalisasi setiap komponen 0–1. Jika missing, renormalisasi bobot yang tersedia dan turunkan confidence. Label: `Critical | High | Medium | Monitor | Insufficient Data`.

Recommended actions berasal dari mapping deterministik dan human-reviewed, bukan generasi bebas model.

## 20. System-Level Evaluation

Buat 20–30 destination cases dan minta evaluator menilai issue correctness, evidence support, severity, ranking, verification relevance, intervention relevance, dan misleading risk.

Metrics:

- Evidence correctness.
- Unsupported alert rate.
- Intervention relevance.
- Priority-ranking agreement.
- Time saved vs manual review.
- Spearman/Kendall, NDCG@K, Precision@K.

## 21. API dan Integrasi Aplikasi

FastAPI endpoints:

```text
GET  /health
POST /predict-review
POST /batch-predict
GET  /destinations
GET  /destinations/{id}
GET  /interventions
POST /simulate
GET  /model-card
```

Batch inference melayani dashboard; real-time hanya untuk analyzer. Next.js tidak menjalankan IndoBERT setiap page load.

Output aplikasi harus memuat model version/time, health components, issues, evidence, confidence, data sufficiency, priority, recommended verification, dan candidate intervention.

## 22. Simulator dan Responsible AI

Simulator menerima destination, aspect, intervention, assumed effectiveness, serta optional budget/capacity. Output: current/scenario scores, assumptions, component changes, uncertainty, dan verification requirement.

Label wajib:

> Estimasi skenario, bukan jaminan hasil dunia nyata atau prediksi kausal.

Safeguards:

- Hapus reviewer identity dari UI.
- Jangan membuat/fabrikasi evidence.
- Gunakan `reported issue` atau `early-warning signal`.
- Terapkan Bayesian smoothing dan minimum support.
- Bedakan no issue dari insufficient data.
- Simpan provenance internal.
- Human verification wajib sebelum tindakan/komunikasi publik.
- Status: New, Verification Planned, Verified, Intervention Planned, Resolved, Rejected.

## 23. Deployment dan Offline Readiness

```text
sipature-web   -> Next.js
sipature-api   -> FastAPI + inference
sipature-db    -> PostgreSQL/PostGIS atau SQLite MVP
```

Simpan offline model, tokenizer, precomputed outputs, map fallback, Docker images, dependencies, model card, dan demo cases. Jangan bergantung pada external model API saat lockdown/DGX deployment.

## 24. Urutan Eksekusi Praktis

### Hari 1: EDA dan Data

Inventory, cleaning, EDA, entity resolution, known issues, taxonomy draft.

**Done:** clean reviews, canonical destinations, entity links, EDA report, taxonomy v1.

### Hari 2: Annotation

Guideline, pilot, agreement, taxonomy revision, main annotation, adjudication.

**Done:** gold annotations, guideline, agreement report.

### Hari 3: Baselines

Group split, keyword, TF-IDF, metrics, error analysis.

**Done:** split manifest, baseline metrics/comparison.

### Hari 4: IndoBERT

Train aspect/polarity/severity, calibrate thresholds, test evaluation.

**Done:** checkpoints, thresholds, test metrics, model card.

### Hari 5: Intelligence Engine

Batch inference, evidence extraction, aggregation, health/priority scores, sensitivity tests.

**Done:** predictions, destination signals, intervention queue.

### Hari 6: Product Integration

Connect real outputs, map, evidence, queue, simulator, offline fallback.

**Done:** model output appears in UI with version and valid evidence.

### Hari 7: Evaluation dan Submission

System evaluation, demo story, failure case, Responsible AI, reproducibility, Docker, video.

## 25. Prioritas Jika Waktu Terbatas

Kerjakan: EDA, reproducible cleaning, conservative entity resolution, guideline, minimum 1.000 labels, destination split, keyword, TF-IDF, IndoBERT aspect detection, calibration, evidence extraction, aggregation, ranking, dashboard, dan evaluation.

Tunda: knowledge graph penuh, agentic workflow, RAG, fine-grained severity jika data tipis, real-time crowding, login, notification engine, dan complex workflow DB.

## 26. Evaluation Metrics dan Diagram

Evaluasi SIPATURE dilakukan pada lima lapisan: kualitas annotation, model review-level, data engineering, intervention ranking, dan system-level decision support. Accuracy tunggal tidak cukup karena label tidak seimbang dan keluaran sistem digunakan untuk menentukan prioritas verifikasi.

### 26.1 Aspect Detection Metrics

Task aspect detection bersifat multilabel. Gunakan:

| Metrik | Fungsi | Prioritas |
| --- | --- | --- |
| Macro F1 | Memberi bobot sama pada semua aspek, termasuk label langka | Utama |
| Micro F1 | Performa total seluruh keputusan label | Utama |
| Per-label Precision | Ketepatan prediksi untuk setiap aspek | Utama |
| Per-label Recall | Coverage aspek sebenarnya | Utama |
| Per-label F1 | Keseimbangan precision dan recall tiap aspek | Utama |
| Precision@Alert | Ketepatan pada threshold early warning | Sangat penting |
| Hamming Loss | Proporsi keputusan label yang salah | Pendukung |
| Exact Match Ratio | Proporsi review dengan seluruh set label tepat | Pendukung |

Macro F1 harus menjadi headline metric karena aspek langka seperti sanitasi atau keselamatan tidak boleh tertutup oleh label dominan.

### 26.2 Polarity Metrics

Untuk kelas `positive | negative | neutral`:

- Macro F1.
- Per-class precision, recall, dan F1.
- Balanced accuracy.
- Confusion matrix.
- Per-aspect polarity F1.

### 26.3 Severity Metrics

Untuk kelas ordinal `low | medium | high`:

- Macro F1.
- High-severity precision dan recall.
- Confusion matrix.
- Weighted Cohen's kappa.
- Ordinal MAE dengan representasi `low=0`, `medium=1`, `high=2`.

High-severity precision menjadi metric utama karena false high-severity alert berpotensi merugikan reputasi destinasi.

### 26.4 Entity Resolution Metrics

- Pairwise precision, recall, dan F1.
- False-merge rate.
- Unresolved-match rate.
- Jumlah ambiguous pairs dan manually reviewed pairs.

Prioritaskan precision dan false-merge rate. Salah menggabungkan dua destinasi lebih berbahaya daripada membiarkan match ambigu belum selesai.

### 26.5 Intervention Ranking Metrics

- NDCG@5 dan NDCG@10.
- Precision@5 dan Precision@10.
- Recall@K.
- Mean Average Precision.
- Spearman rank correlation.
- Kendall's tau.

Ground truth ranking dibuat dari penilaian stakeholder atau expert-reviewed destination cases.

### 26.6 Calibration Metrics

- Expected Calibration Error.
- Brier Score.
- Reliability diagram.
- Precision-recall curve per label.

Calibration memvalidasi apakah confidence model dapat dipercaya oleh pengguna aplikasi.

### 26.7 Diagram Evaluasi Model

#### A. Model Comparison Grouped Bar Chart

Bandingkan Keyword, TF-IDF, dan IndoBERT pada Macro F1, Micro F1, Alert Precision, dan latency. Diagram ini membuktikan nilai tambah model kompleks terhadap baseline sederhana.

#### B. Per-Label Metrics Bar Chart

Horizontal bar chart precision, recall, F1, dan support untuk setiap aspek. Support wajib ditampilkan agar label dengan data sedikit tidak disalahartikan.

#### C. Precision-Recall Curve

Buat untuk aspek utama: sanitation, waste, cleanliness, access, dan safety. Tandai detection threshold, alert threshold, dan operating point. PR curve lebih sesuai daripada ROC curve untuk label imbalanced.

#### D. Multilabel Confusion Matrix Grid

Tampilkan matrix `TP/FP/FN/TN` per aspek atau heatmap precision/recall/F1 lintas aspek. Jangan memakai satu multiclass confusion matrix untuk task multilabel.

#### E. Polarity Confusion Matrix

Matrix 3x3 untuk actual vs predicted positive, negative, dan neutral.

#### F. Severity Confusion Matrix

Matrix ordinal low, medium, high. Soroti kesalahan berat seperti actual high yang diprediksi low.

#### G. Reliability Diagram

Plot predicted confidence vs observed correctness dengan diagonal perfect calibration.

#### H. Threshold vs Precision/Recall/F1

Plot threshold pada sumbu X dan precision, recall, F1 pada sumbu Y untuk menjelaskan pemilihan threshold per aspek.

#### I. Learning Curve

Plot ukuran training set vs train/validation Macro F1. Diagram membantu menentukan apakah model memerlukan lebih banyak annotation atau perbaikan arsitektur.

#### J. Training Curve

Plot train/validation loss dan Macro F1 per epoch untuk mendeteksi overfitting dan menentukan early stopping.

### 26.8 Diagram Evaluasi Annotation dan EDA

#### A. Annotation Agreement Bar Chart

Tampilkan Cohen's kappa/Krippendorff's alpha untuk aspect, polarity, severity, dan jika memungkinkan per label.

#### B. Label Distribution

Stacked bar jumlah positive, negative, neutral per aspek. Diagram menjelaskan class imbalance dan alasan penggunaan Macro F1/class weighting.

#### C. Aspect Co-Occurrence Heatmap

Tampilkan pasangan aspek yang sering muncul bersama, misalnya sanitation-cleanliness, waste-cleanliness, access-parking, scenery-comfort. Diagram mendukung pemilihan multilabel classification.

#### D. Rating Distribution

Bar chart rating 1-5. Gunakan untuk menjelaskan dominasi rating positif dan mengapa keluhan perlu dicari pada minoritas data.

#### E. Review Length Distribution

Histogram token/karakter untuk memilih maximum sequence length IndoBERT dan mengukur truncation rate.

#### F. Error Category Bar Chart

Tampilkan jumlah error karena negation, implied complaint, typo, mixed language, aspect boundary, sarcasm, insufficient context, dan annotation disagreement.

### 26.9 Diagram Evaluasi Data Engineering

#### A. Missing Values Heatmap

Tampilkan missing rate untuk review text, coordinates, facilities, operating hours, fee, dan status per dataset.

#### B. Data Cleaning Funnel

```text
raw records
-> valid schema
-> after exact deduplication
-> textual reviews
-> linked canonical destinations
-> annotation candidates
-> model inference records
```

Funnel memperlihatkan penggunaan data secara nyata dan alasan record dikeluarkan.

#### C. Entity Resolution Evaluation Chart

Grouped bar pairwise precision/recall/F1 dengan annotation jumlah false merges dan ambiguous matches.

#### D. Geographic Coverage Map

Peta sufficient data, low confidence, no textual review, missing coordinates, dan high-priority alerts.

#### E. Review Coverage Distribution

Histogram jumlah review berteks per destinasi. Tambahkan garis threshold kategori insufficient, low, medium, dan high confidence.

### 26.10 Diagram Evaluasi Decision Support

#### A. Expert vs Model Ranking Scatter Plot

Plot model priority rank vs expert priority rank. Laporkan Spearman dan Kendall correlation. Titik dekat diagonal menunjukkan agreement tinggi.

#### B. NDCG@K Comparison Chart

Bandingkan Keyword, TF-IDF, dan IndoBERT ranking menggunakan NDCG@5 dan NDCG@10.

#### C. Evidence Correctness Stacked Bar

Kategori human evaluation: Supported, Partially Supported, Unsupported. Headline metrics: evidence correctness rate dan unsupported alert rate.

#### D. Intervention Relevance Chart

Kategori: Relevant, Needs Revision, Not Relevant, ditampilkan keseluruhan dan per aspek.

#### E. Time-Saved Box Plot

Bandingkan waktu manual review inspection dengan SIPATURE-assisted inspection. Laporkan median, IQR, dan persentase penghematan waktu. Jangan membuat angka sebelum user study dilakukan.

#### F. Alert Verification Funnel

```text
alerts generated
-> sufficient evidence
-> verification planned
-> field verified
-> intervention planned
-> resolved/rejected
```

#### G. Priority Component Waterfall

Untuk satu destination case, tampilkan kontribusi severity, frequency, confidence, persistence, exposure, facility gap, dan feasibility terhadap Priority Score. Diagram ini mendukung explainability.

#### H. Before/After Scenario Chart

Bandingkan current score dan scenario score per component. Beri label permanen bahwa hasil adalah scenario estimate, bukan causal prediction.

### 26.11 Diagram Minimum untuk Submission

Jika waktu terbatas, prioritaskan 10 visual berikut:

1. Data cleaning funnel.
2. Rating dan label distribution.
3. Aspect co-occurrence heatmap.
4. Model comparison grouped bar chart.
5. Per-label F1 + support chart.
6. Precision-recall curve label utama.
7. Polarity/severity confusion matrix.
8. Reliability diagram.
9. Expert vs model ranking atau NDCG@K chart.
10. Evidence correctness + unsupported alert chart.

Tambahkan geographic coverage map untuk demo produk dan learning curve jika ruang laporan cukup.

### 26.12 Pemetaan ke Rubrik Del AI Hackathon

Rencana evaluasi ini sesuai dengan ketentuan kompetisi:

| Rubrik | Bukti SIPATURE |
| --- | --- |
| Kebaruan dan problem framing, 20 | Evaluasi rantai review-to-intervention, bukan dashboard sentimen umum |
| Dampak dan relevansi, 20 | Ranking agreement, intervention relevance, time saved, alert verification rate |
| Kualitas teknis AI/data, 20 | Baseline comparison, Macro/Micro F1, per-label metrics, calibration, entity-resolution metrics, leakage-safe split |
| Kelayakan dan keberlanjutan, 15 | Latency, offline deployment, workflow verification, pilot metrics |
| Pemanfaatan data Toba, 15 | Cleaning funnel, coverage map, metadata integration, evidence provenance, facility-gap analysis |
| Komunikasi/demo/dokumentasi, 10 | Diagram evaluasi, model card, error analysis, evidence-backed demo |

Kesesuaian dokumen kompetisi:

- Preliminary menilai kualitas analisis, interpretasi, visualisasi, dan dampak rekomendasi.
- Video demo wajib menjelaskan eksekusi dan performa/evaluasi model.
- Submission wajib menjelaskan pemanfaatan dataset, pendekatan AI, dan evaluasi model.
- Rubrik teknis meminta performa berdasarkan metrik kuantitatif yang relevan.
- Responsible AI meminta dasar rekomendasi, keterbatasan, bias, privasi, dan risiko misuse.

Catatan penting: semua chart harus memakai hasil aktual dari locked test set atau human evaluation. Target, asumsi simulator, dan hasil aktual harus diberi label berbeda.

## 27. Artefak Akhir dan Definition of Done

Artefak:

```text
EDA report
data dictionary
known issues
cleaning pipeline
entity-resolution report
annotation guideline + gold data + agreement
split manifest
keyword + TF-IDF + IndoBERT artifacts
threshold config + test metrics + error analysis
model card
review predictions
destination aggregation
priority queue
system-level evaluation
Responsible AI document
source code + Docker image + demo video
```

Selesai jika:

1. Pipeline dapat dijalankan ulang dari raw CSV.
2. Test set tidak bocor dan hanya dievaluasi setelah model dikunci.
3. Baseline dan primary model dibandingkan pada split sama.
4. Setiap alert memiliki evidence verbatim, confidence, provenance, dan model version.
5. Missing data tidak diperlakukan sebagai kondisi baik.
6. Ranking telah diuji dengan expert-reviewed cases.
7. UI memakai bahasa early warning, bukan vonis.
8. Simulator menyatakan asumsi dan non-causal limitation.
9. Sistem berjalan offline dan dapat di-deploy dengan Docker.
10. Submission melaporkan hasil aktual, failure cases, bias, dan limitations.

Fokus utama untuk juri:

```text
Raw review
-> trained and evaluated prediction
-> destination-level signal
-> verbatim evidence
-> explainable priority
-> human-verifiable intervention
```
