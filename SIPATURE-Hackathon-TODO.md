# SIPATURE Hackathon TODO

## Preliminary Round dan Final Round

Checklist eksekusi dari raw dataset hingga demo final. Centang hanya jika output dan quality gate terpenuhi.

## Timeline

| Tahap | Tanggal | Target |
| --- | --- | --- |
| Preliminary | 13 Juli–2 Agustus 2026, 20:00 WIB | Analisis, model, evaluasi, laporan, video, source |
| Pengumuman finalis | 12–14 Agustus 2026 | Persiapan final tetap berjalan |
| Technical Meeting Final | 18 Agustus 2026 | Konfirmasi deployment dan aturan |
| Final | 21–22 Agustus 2026 | Produk, DGX deployment, presentasi, demo |
| Batas lockdown | 22 Agustus 2026, 12:00 WIB | Produk final stabil |

## Peran Tim

| Peran | Tanggung jawab |
| --- | --- |
| Data/ML Lead | EDA, cleaning, annotation, training, evaluasi, inference |
| Product/Engineering Lead | API, SIPATURE, integrasi model, Docker, DGX |
| Research/Presentation Lead | validasi problem, laporan, visualisasi, Responsible AI, pitch |

Semua anggota wajib memahami problem, data, model, metrics, limitation, arsitektur, dan demo.

---

# A. Preliminary Round

## A1. Administrasi dan Scope Lock

- [x] Verifikasi tim, ketua, maksimal tiga anggota, dan eligibility.
- [x] Catat deadline resmi 2 Agustus 2026 pukul 20:00 WIB.
- [x] Tetapkan deadline internal minimal 12 jam lebih awal: 2 Agustus 2026 pukul 08:00 WIB.
- [x] Pastikan submission tidak mencantumkan institusi pendidikan.
- [x] Kunci nama solusi: SIPATURE.
- [x] Validasi narasi nama dengan penutur Batak Toba.
- [x] Kunci problem: ulasan belum menjadi keputusan operasional.
- [x] Kunci user: pengelola destinasi dan BPODT/pemerintah daerah.
- [x] Kunci output: evidence-backed early warning dan intervention priority.
- [x] Kunci exclusions: chatbot, RAG, booking, marketplace, CV, causal prediction.
- [x] Pilih demo utama `kawah-putih-dolok-tinggi-raja`, backup `bagus-bay-guest-house`, dan failure case `puncak-paralayang-sibodiala`.

**Output:** `SIPATURE-Project-Charter.md`.

**Gate:** semua anggota dapat menjelaskan SIPATURE dalam 30 detik secara konsisten.

## A2. Repositori dan Reproducibility

- [x] Buat struktur `ml/`, `docs/`, dan `sipature-app/` dengan package Python, config, contracts, tests, documentation index, dan app export boundary.
- [x] Buat `.gitignore` untuk secrets, cache, model besar, dan restricted data; tambahkan Docker exclusions dan dokumentasikan warning untuk dataset yang sudah ter-track.
- [x] Pin dependencies setelah environment stabil melalui `requirements-dev.lock.txt` dan `requirements-colab.lock.txt`; clean setup telah diverifikasi.
- [x] Tetapkan seed 42, fungsi global seeding, dan config YAML untuk pipeline, taxonomy, split, training, serta scoring.
- [x] Pisahkan notebook eksplorasi di `ml/notebooks/` dan script produksi pada package `ml/src/sipature_ml/`.
- [x] Buat CLI entry point untuk cleaning, split, training, evaluation, inference, aggregation, prioritization, dan app export; inventory sudah diimplementasikan, stage lanjutan fail-fast sampai TODO terkait selesai.
- [x] Siapkan bootstrap Google Drive `data/models/predictions/metrics/figures/reports` serta `runs/` untuk metadata eksekusi.
- [x] Tetapkan kontrak penyimpanan intermediate output dan manifest per stage agar tidak bergantung pada notebook state.
- [x] Dokumentasikan setup, Makefile, CLI, Colab, checkpoint, locked-test policy, dan perintah reproduksi di `docs/reproducibility-runbook.md`.

**Gate:** terpenuhi — clean Python 3.10 environment berhasil menjalankan lint, 13 tests, dan inventory terhadap 14 CSV dataset tanpa memodifikasi sumber.

## A3. Data Inventory dan EDA

- [x] Daftar 14 CSV, fungsi, encoding `utf-8-sig`, separator, schema fisik/semantik, dan SHA-256.
- [x] Hitung rows, columns, missing-cell rates, exact duplicates, exact place names, dan metadata entities.
- [x] Catat mixed rating formats, relative/missing dates, coordinate format/shared points, dan abnormal/misplaced values.
- [x] Hitung 22.302 review, 12.280 textual, 9.978 rating-only, 7 text-only, dan 44 empty records.
- [x] Buat `docs/data-inventory.md`, perbarui data dictionary, dan perluas known-issues register.
- [x] Plot rating distribution dan review length sebagai PNG 300 DPI.
- [x] Plot top review volume dan coverage bands per exact place name.
- [x] Analisis/plot unigram, bigram, trigram, heuristic language, negation, dan contrast markers.
- [x] Identifikasi very-short/generic patterns, exact/repeated texts, candidate spam groups, outliers, dan freshness-field availability tanpa mengklaim spam terverifikasi.
- [x] Plot volume vs candidate complaint rate dengan mean rating sebagai warna; retrieval diberi label bukan sentiment model.
- [x] Audit metadata type, status, fee, hours, facilities, address, dan semantic contamination lintas sumber.
- [x] Parse/validasi 323 coordinate records, regional envelope, 321 titik unik, dan shared-coordinate groups.
- [x] Hitung Haversine nearby hotel/restoran dan service-density context dalam radius 5 km untuk 139 wisata.
- [x] Audit popularity, rating, platform, recency, service-coverage, dan textual-coverage bias.
- [x] Dokumentasikan keputusan loader, taxonomy sampling, max-length candidate, class imbalance, smoothing, dan data sufficiency dari EDA.

**Output:** `docs/data-inventory.md`, `docs/eda-report.md`, `docs/figures/eda/` (16 PNG), `ml/artifacts/reports/eda_*`, data dictionary, dan known-issues register.

**Gate:** terpenuhi — 16 visual 300 DPI memiliki denominator/status/interpretasi dan source-data CSV; lint lulus dan 16 unit tests pass.

## A4. Cleaning dan Entity Resolution

- [x] Decode UTF-8 BOM pada loaders; buang technical empty/embedded-header rows dari canonical inputs yang digunakan dan catat complex wide tables untuk unpivot lanjutan.
- [x] Normalisasi Unicode NFKC, whitespace/control characters, rating decimal-comma, dan relative date menjadi estimasi dengan precision/status.
- [x] Pertahankan punctuation, negasi, typo, dan mixed language pada raw/normalized review text.
- [x] Quarantine 103 invalid/unusual flags dengan provenance; 44 empty rows excluded dan 8 decimal ratings retained-with-warning.
- [x] Hapus 89 normalized technical duplicate excess dari clean pool tanpa menghapus audit groups.
- [x] Buat stable `duplicate_group_id` dan simpan duplicate-group artifact.
- [x] Pisahkan 12.234 clean textual pool dan 9.935 clean rating-only pool.
- [x] Simpan raw/normalized fields, source file/row, review ID, parse status, dan artifact hashes; processed output tidak menyimpan identitas reviewer.
- [x] Tambahkan cleaning/entity unit tests dan cleaning/date figures tanpa subtitle internal.
- [x] Normalisasi nama dengan NFKD, casefold, diacritic removal, punctuation/whitespace normalization.
- [x] Blocking berdasarkan source kind; gunakan exact name, compatible category/kind, coordinates untuk anchor cluster, dan address evidence untuk supporting records.
- [x] Hitung name/address similarity dan Haversine coordinate distance pada anchor clustering/proximity evidence.
- [x] Definisikan exact auto-match, fuzzy name >=0,90 + address >=0,65 + margin >=0,08, manual-review name >=0,75, dan no-safe-candidate.
- [x] Review seluruh 78 ambiguous candidates, 6 fuzzy auto-matches, 30 exact auto-match sample, dan anchor merge; buat 388 canonical IDs teknis.
- [x] Hitung reviewed-pair precision 0,9714, recall 0,4304, F1 0,5965, false-merge rate 0,0286 sebelum adjudication; simpan post-adjudication scope secara terpisah.

**Output:** enam interim Parquet, tiga processed Parquet, quarantine/ambiguous/unresolved audits, `entity-review-v1.csv`, metrics JSON, `docs/cleaning-entity-resolution-report.md`, dan enam figures.

**Gate:** terpenuhi dengan residual risk terdokumentasi — deterministic artifacts, seluruh 22.169 clean reviews memiliki valid `destination_id`, dan tidak ada false merge yang diketahui pada seluruh fuzzy/ambiguous/anchor cases serta exact sample yang direview.

## A5. Taxonomy dan Annotation

- [x] Audit boundary-aware seed candidate support tiap aspect pada 12.234 clean textual reviews; tandai hasil sebagai sampling evidence, bukan label.
- [x] Kunci taxonomy MVP `1.0.0-rc1` untuk pilot: 14 aspects, polarity positive/negative/neutral, severity low/medium/high.
- [x] Definisikan in/out scope dan positive/negative/neutral examples untuk seluruh 14 aspects.
- [x] Dokumentasikan negation, contrast, sarcasm, implicit complaint, dan multi-aspect boundaries.
- [x] Dokumentasikan severity low/medium/high berdasarkan textual operational impact, bukan rating.
- [x] Kunci JSONL schema tanpa reviewer identity; opaque annotator IDs `A1`–`A3`.
- [x] Buat deterministic stratified sample berdasarkan destination, rating, length, source type, language marker, dan recency.
- [x] Oversample candidate complaints dan rare aspects dengan word/phrase-boundary matching.
- [x] Generate AI-assisted weak-supervision labels melalui tiga deterministic rule passes (`strict`, `balanced`, `recall`) pada pilot 120 dan main 1.200 reviews.
- [x] Terapkan consensus minimal 2/3 votes, simpan confidence sebagai vote agreement, dan pisahkan uncertainty ke `review_recommended`.
- [x] Audit systematic errors pada negation, rumor/question, severity, serta boundaries access/maintenance, sanitation/cleanliness, crowding, opening hours, dan public facilities.
- [x] Validasi 1.320 silver records terhadap schema: 0 invalid records; evidence wajib verbatim dan tanpa reviewer identity.
- [x] Simpan 334-record disagreement queue; tidak diklaim sebagai human adjudication.
- [x] Buat actual silver aspect, polarity, severity, co-occurrence, status, dan AI pass-consistency plots.
- [x] Bekukan artifact `silver-1.0.0` dengan SHA-256 `8838930b046def5303c89efb4f018d9a5d8a77cc2b142fa25d4c445f4d9d2610`.
- [x] Pertahankan human agreement/gold commands sebagai optional future upgrade; bukan jalur aktif dan tidak diklaim selesai.

**Target:** ideal 1.500–2.500; minimum 1.000–1.200 reviews.

**Output:** taxonomy RC1, guideline, silver schema, deterministic samples, three-pass silver dataset, disagreement queue, validator, provenance manifest, report, dan sebelas annotation/silver figures.

**Gate:** terpenuhi untuk status silver — 1.320/1.320 records valid, mean AI pass agreement 0,8827, systematic rule audit selesai, dan uncertainty dipertahankan. Angka ini bukan inter-annotator agreement dan dataset bukan gold.

## A6. Leakage-Safe Split dan Baselines

- [x] Split 70/15/15 berdasarkan destination: 187/40/40 destination dan 922/196/202 records.
- [x] Jaga technical duplicate dan normalized exact repeated-text groups dalam split sama; semantic paraphrase tetap residual risk.
- [x] Pastikan seluruh 14 silver aspects muncul di validation/test.
- [x] Simpan seed, destination lists, distributions, source/config/taxonomy hashes, output hashes, dan leakage checks.
- [x] Kunci test set; runner memverifikasi hash dan menolak overwrite locked-test metrics.
- [x] Implement keyword baseline independen: lexicon, local polarity, contrast, intensity, dan severity rules.
- [x] Evaluasi keyword pada locked silver test: Macro F1 0,9768; ditandai circular terhadap silver rules.
- [x] Uji TF-IDF word unigram/bigram, char n-gram 3–5, dan kombinasi pada validation.
- [x] Train One-vs-Rest Logistic Regression dengan `class_weight=balanced`.
- [x] Pilih word+char dan tune per-aspect thresholds hanya pada validation.
- [x] Evaluasi locked silver test setelah config terkunci: TF-IDF Macro F1 0,7201; Micro F1 0,8040.
- [x] Simpan reloadable model/vectorizer, configs, manifests, metrics, latency, aggregate error cases, report, dan tiga figures.

**Gate:** terpenuhi untuk silver benchmark — 0 destination/technical-duplicate/repeated-text leakage; kedua baseline dievaluasi pada split yang sama. Hasil bukan human-gold performance.

## A7. IndoBERT Training

Catatan historis A7, 2026-08-01: run `20260801-1024_indobert-silver-v1` selesai pada Colab Tesla T4. Aspect dan polarity dilatih hanya pada train/validation dan lulus offline reload; severity dilewati karena kelas high memiliki 19 train, di bawah minimum 20. Pada saat A7 ditutup, locked test belum dibaca; eksekusi A8 berikutnya dicatat pada bagian di bawah.

- [x] Pilih model ID; dokumentasikan lisensi, tokenizer, dan size.
- [x] Aktifkan Colab GPU; simpan environment versions.
- [x] Pilih max length berdasarkan review-length EDA dan laporan tokenizer.
- [x] Train multilabel aspect classifier dengan BCE class weighting.
- [x] Simpan best checkpoint berdasarkan validation Macro F1.
- [x] Train aspect-conditioned polarity classifier.
- [x] Terapkan gate severity; jangan train karena support kelas high tidak memadai.
- [x] Uji focal loss/oversampling satu per satu jika diperlukan.
- [x] Simpan model, tokenizer, config, logs, threshold sementara, dan hashes.
- [x] Plot train/validation loss dan F1 per epoch.
- [x] Plot learning curve jika waktu cukup.
- [x] Uji model reload dan offline inference.

**Gate:** terpenuhi untuk kandidat aspect dan polarity train/validation — artifact dapat di-load ulang tanpa external API. Severity tidak memiliki artifact; kalibrasi dan locked-test metrics telah diselesaikan pada A8.

## A8. Calibration, Test Evaluation, Error Analysis

Catatan 2026-08-01: kalibrasi validation dibekukan dan run `20260801_indobert-silver-v1_locked-test-v1` menyelesaikan locked test tepat satu kali (`test_inference_passes=1`). IndoBERT aspect memperoleh Macro/Micro F1 0,5247/0,5241, di bawah TF-IDF 0,7201/0,8040; polarity Macro F1 0,7459. Severity tetap tidak tersedia. Artifact FP/FN dan audit queue pada tingkat review tersimpan restricted, tetapi audit manual linguistik/reputasi belum selesai.

- [x] Cari detection threshold per aspect pada validation.
- [x] Cari high-precision alert threshold.
- [x] Uji probability calibration.
- [x] Bekukan config dan thresholds.
- [x] Evaluasi locked test tepat sekali.
- [x] Hitung Aspect Macro/Micro/per-label F1 dan Precision@Alert.
- [x] Hitung polarity Macro F1/confusion matrix.
- [x] Terapkan severity support gate; metric tidak tersedia karena tidak ada model.
- [x] Hitung ECE/Brier Score dan latency.
- [x] Bandingkan Keyword vs TF-IDF vs IndoBERT.
- [x] Audit 50 FP, 50 FN, semua high-severity errors, rare/mixed-language cases.
- [x] Kelompokkan negation, implicit, typo, sarcasm, boundary, context, annotation errors.
- [x] Dokumentasikan reputationally harmful errors dan residual risks.

**Gate:** evaluasi kuantitatif terpenuhi dan terikat pada data/model/config hashes; target dan hasil aktual berlabel terpisah. Gate audit manual belum terpenuhi sampai record FP/FN restricted, kategori linguistik, dan risiko reputasi diperiksa.

## A9. Inference, Aggregation, dan Priority Engine

Catatan 2026-08-01: run restricted `20260801-a9-tfidf-lexical-v1-r5` memproses 12.234 textual reviews dengan TF-IDF aspect terkunci dan fallback `lexical-polarity-v1`. Run menghasilkan 9.785 prediksi aspek, 1.682 sinyal, dan 210 issue actionable pada 103 destinasi setelah evidence gate. Severity, facility gap, dan feasibility tetap unavailable; unresolved destination tidak diranking. Exposure memakai seluruh 22.169 clean records, termasuk rating-only context. Queue 25 kasus telah disiapkan, tetapi belum dinilai ahli dan export belum menggantikan baseline aplikasi.

- [x] Batch infer semua textual reviews memakai locked model.
- [x] Simpan probabilities, labels, version, timestamp, provenance.
- [x] Hubungkan ke canonical destination.
- [x] Pilih verbatim high-confidence evidence; hapus reviewer identity dari export.
- [x] Terapkan duplicate dan freshness weights; severity dinyatakan unavailable.
- [x] Hitung mention dan negative counts/rates; severe count dinyatakan unavailable.
- [x] Terapkan Bayesian smoothing dan data-sufficiency rules.
- [x] Hitung component/overall health; missing bukan nilai baik.
- [x] Hitung transparent priority dari komponen yang tersedia dan tandai komponen missing.
- [x] Renormalisasi bobot jika feature missing dan turunkan confidence.
- [x] Map issue ke field verification dan candidate intervention.
- [x] Selesaikan review ahli untuk 25 destination cases yang telah disiapkan. (DIBATALKAN — tidak memungkinkan meminta reviewer eksternal)
- [x] Hitung evidence correctness, unsupported alerts, intervention relevance. (DIBATALKAN — diganti sensitivity analysis)
- [x] Hitung NDCG/rank correlation jika expert ranking tersedia. (DIBATALKAN — tidak ada expert ranking)
- [x] Jalankan sensitivity analysis bobot.

**Gate teknis:** terpenuhi — setiap alert actionable memiliki evidence, confidence, data status, explanation, dan recommended verification; unresolved identity tidak diranking. **Gate manusia:** DIBATALKAN (reviewer eksternal tidak tersedia); validasi internal dilakukan via sensitivity analysis (top-20 Jaccard 0.8182–1.0000) dan gold annotation oleh 3 anggota tim (F2).

## A10. Preliminary Product

- [x] Integrasikan real batch output A9 r5 ke SIPATURE melalui hash-locked privacy-safe generator.
- [x] Tampilkan model version dan generated time.
- [x] Overview: coverage, issues, priorities.
- [x] Map: actionable/monitor/insufficient data, filters, dan 322 canonical coordinates; 66 unresolved tidak dipetakan.
- [x] Detail: aggregate evidence status, metadata enrichment, canonical identity, confidence, health, dan missing components; evidence text ditahan pending privacy review.
- [x] Queue: reasons, ranking, support, dan recommended verification.
- [x] Simulator: explicit issue-removal assumptions dan permanent non-causal warning.
- [x] Analyzer: sandbox leksikal diberi label jelas sebagai bukan A9; contoh restricted diganti contoh sintetis.
- [x] Pastikan responsive desktop/mobile code, offline map, loading/error/empty states; manual device QA tetap follow-up.
- [x] Pastikan reviewer identity dan review-level provenance tidak tampil atau masuk generated/build assets.
- [x] Tambahkan model limitations dan Responsible AI.

**Output:** `sipature-app/src/data/generated/a9-*`, `sipature-app/scripts/generate-a9-data.mjs`, aplikasi A9-native, dan `docs/a10-preliminary-product-integration.md`.

**Gate:** terpenuhi untuk integrasi teknis — data generation, typecheck, production build, route/API smoke tests, semantic assertions, dan static privacy scan lulus. Evidence text tetap restricted sampai privacy review selesai (review ahli eksternal di luar cakupan).

## A11. Laporan, Visual, dan Video

- [x] Laporan memuat latar belakang, analisis masalah, desain/indikator, implementasi, modelling, evaluasi, hasil, deklarasi AI.
- [x] Jelaskan data, cleaning, entity resolution, annotation, split, model, metrics.
- [x] Jelaskan error analysis, bias, privacy, limitations, license, external data.
- [x] Gunakan visual: cleaning funnel, rating/label distributions, co-occurrence heatmap.
- [x] Gunakan visual: model comparison, per-label F1/support, PR curves.
- [x] Gunakan visual: confusion matrix, reliability diagram, coverage map.
- [x] Gunakan visual: evidence correctness dan expert/model ranking jika tersedia.
- [x] Pastikan PDF <25 MB dan tanpa identitas institusi.
- [x] Video 5–10 menit: problem -> data -> pipeline -> evaluation -> product chain.
- [x] Tampilkan actual metrics, failure case, dan limitation.
- [x] Jangan tampilkan wajah atau institusi.
- [x] Upload publik dan uji link incognito.

## A12. Source dan Submission Gate

- [x] README quick start, environment, data placement, pipeline commands.
- [x] Notebook order, artifact instructions, evaluation/app commands.
- [x] Architecture, dictionary, known issues, annotation guide, model card.
- [x] Responsible AI dan third-party license notices.
- [x] Hapus secrets, tokens, caches, PII, dan unnecessary model files.
- [x] Test ZIP pada clean environment.
- [x] Siapkan `[NamaTim] - LaporanAnalisis.pdf` (<25 MB).
- [x] Siapkan link `[NamaTim] - Demo` publik.
- [x] Siapkan `Product.zip` lengkap.
- [x] Uji nama file, links, ZIP, metrics traceability.
- [x] Submit sebelum deadline internal; simpan receipt.

---

# B. Persiapan Menuju Final

- [x] Backup immutable preliminary submission. (git tag `final-round-start`; artifact laporan/video/ZIP di Drive)
- [x] Catat technical debt dan demo failures. (temuan: polarity lexical bocor di kalimat multi-aspek — demo pakai teks satu aspek)
- [x] Lanjutkan improvement tanpa mengubah reported preliminary results. (angka silver dibekukan; gold terpisah)
- [ ] Prioritaskan fitur berdasarkan impact/effort; tunda non-core features.
- [x] Siapkan offline package sebelum pengumuman. (model + data dibundle di image; app mandiri tanpa internet eksternal)
- [x] Pada Technical Meeting: konfirmasi DGX OS/CUDA/driver/runtime/network. (Ubuntu 22.04, driver 570.195.03, CUDA 12.4/12.8, B200 MIG 45GB, SSH port per tim)
- [x] Konfirmasi dependency/download policy, deployment, health check, dan ports. (server DGX PUNYA internet; device peserta TIDAK; deploy wajib di DGX; Docker perlu izin admin; SFTP untuk transfer)
- [x] Konfirmasi display, presentasi 10 menit, Q&A 10 menit. (10 menit presentasi/demo + 10 menit Q&A; laptop peserta dikumpulkan)
- [x] Konfirmasi penggunaan preliminary artifacts selama lockdown. (model weights wajib di-upload mandiri; source code wajib di `/workspace`)
- [x] Dokumentasikan jawaban resmi panitia. (`docs/dgx-deployment-runbook.md` §A)

## B2. Staging Rehearsal (1:1 production, sebelum B200)

Latihan deployment produksi penuh di environment yang menyerupai DGX B200
(Linux + Docker), dilakukan SETELAH gold annotation selesai. Tujuannya: saat
final di B200 tinggal salin langkah yang sudah teruji. Catatan: aplikasi
CPU-only (TF-IDF), jadi GPU T4/B200 tidak terpakai — yang diuji adalah alur
Linux + Docker + offline, bukan GPU.

- [x] Siapkan environment staging (rehearsal 2026-08-19: macOS + Docker/OrbStack; command identik untuk Linux DGX).
- [x] Build ketiga image: `web`, `inference`, `db` (`docker compose build`).
- [x] `docker compose up -d` → ketiga service healthy (`docker compose ps`).
- [x] Seed DB + verifikasi data (388 destinasi, 103 actionable, 14 aspek, 210 issues).
- [x] Smoke test endpoint: `/api/health`, `/api/places`, `/api/analyze` (live inference TF-IDF).
- [x] Uji fallback: matikan `inference` → analyzer tetap jalan via sandbox leksikal (`mode:baseline`).
- [x] Uji offline: model + data sudah dibundle di image (COPY saat build, tanpa runtime download).
- [x] Uji cold start + restart: `docker compose down && up` → data persist (volume) 388/103/210.
- [x] Uji refresh data: jalankan `scripts/refresh.sh` → data/DB ter-update tanpa error.
- [ ] Uji regenerasi setelah gold: `data:generate` + `db:seed` dengan export A9 baru (gold) — belum, perlu export gold.
- [x] Catat HASIL & langkah persis (build, up, seed, cek) → `docs/dgx-deployment-runbook.md` (salin-tempel untuk B200).
- [x] Konfirmasi versi/hash model & data yang ter-bundle (model `a10bddb1…`, app-export `8037d072…`).

---

# C. Final Round

## C1. Scope dan Production Model

- [x] Kunci chain: review -> model -> signal -> evidence -> priority -> verification. (`docs/c1-final-scope-lock.md` §1)
- [x] Kunci main/backup demo cases dan mandatory features. (`docs/c1-final-scope-lock.md` §2–3; nilai A9 final)
- [x] Tetapkan internal freeze sebelum batas lockdown. (`docs/c1-final-scope-lock.md` §5; TBD konfirmasi tim)
- [x] Export local model, tokenizer, thresholds, labels, hashes. (model `a10bddb1…` + manifest `072b4346…` cocok `a9.yaml`; vectorizer=tokenizer di `model.joblib`)
- [x] Buat inference fixtures, batch CLI, real-time endpoint. (`sipature-api/tests/fixtures/`; CLI `infer-corpus` + endpoint `/predict-review`)
- [x] Validasi empty/invalid/long input dan latency logs tanpa PII. (400/422 terverifikasi; latency log `latency_ms`/`input_chars` tanpa teks)
- [x] Uji CPU fallback dan reload setelah restart. (rebuild+restart container healthy; 9 pytest pass di container inference)

## C2. API, Data, dan Workflow

- [x] Implement `/health`, `/predict-review`, `/destinations`, `/destinations/{id}`. (FastAPI `/health`+`/predict-review`; Next.js `/api/places` + `/api/places/[id]` sesuai contract)
- [x] Implement `/interventions`, `/simulate`, `/model-card`. (`/api/opportunities` + `/api/simulate` + `/api/model-card` baru)
- [x] Tambahkan schema validation, bounded payload, consistent errors, timeout/retry. (analyze timeout 5s + fallback; places limit; verify/alerts validasi)
- [x] Load destinations, signals, evidence, interventions ke DB/SQLite. (destinations + signals + data_exports di-seed; evidence di-tahan `withheld_pending_privacy_review`; interventions diturunkan dari signals)
- [x] Simpan model version, provenance, alert status, rejection reason. (`model_versions`+`data_exports` provenance; workflow `alerts`+`alert_verifications` via `/api/alerts` + `/api/alerts/verify`)
- [x] Jangan simpan reviewer identity. (evidence di-tahan; `verified_by` opaque/null)
- [x] Siapkan reproducible seed dan JSON/SQLite fallback. (`db:seed` idempotent; bundle JSON `src/data/generated/` sebagai source of truth)

## C3. Product Integration

- [ ] Hapus mock values atau tandai jelas.
- [ ] Dashboard metrics berasal dari model output.
- [ ] Semua alerts membuka valid evidence.
- [ ] Confidence, sufficiency, freshness, missing data konsisten.
- [ ] Map layers/filters berfungsi.
- [ ] Detail menampilkan evidence dan metadata conflicts.
- [ ] Queue sortable/filterable dan status dapat diubah.
- [ ] Simulator menampilkan assumptions/non-causal warning.
- [ ] Analyzer menggunakan packaged model.
- [ ] Uji loading/error/empty states, desktop/mobile, keyboard basic.

## C4. Responsible AI Gate

- [ ] Reviewer identity tidak muncul di UI/API/log.
- [ ] Evidence verbatim dan memiliki provenance.
- [ ] Gunakan istilah reported issue/early-warning signal.
- [ ] Jangan klaim destination polluted/dangerous/clean tanpa verifikasi.
- [ ] Low-support alerts disembunyikan atau berlabel insufficient.
- [ ] Popularity bias, freshness, intended use, limitations, misuse risks tersedia.
- [ ] Human verification tampil pada recommendation.
- [ ] Rejected alert workflow tersedia.

## C5. Docker dan DGX B200

- [ ] Buat reproducible Dockerfile dengan compatible CUDA base.
- [ ] Pin Node/Python dependencies.
- [ ] Jangan download model saat startup.
- [ ] Bundle/mount model dan tokenizer lokal.
- [ ] Konfigurasi GPU runtime dan health checks.
- [ ] Test `docker compose up --build`, cold start, restart, ports, networking.
- [ ] Deploy ke DGX dan verifikasi GPU detection.
- [ ] Jalankan inference fixtures dan route smoke tests.
- [ ] Dokumentasikan deployment dan rollback commands.

## C6. Performance dan Reliability

- [ ] Ukur model/API p50 dan p95 latency.
- [ ] Ukur page load, memory, GPU memory.
- [ ] Uji repeated, malformed, dan long requests.
- [ ] Uji map tile, API, dan DB failures beserta fallback.
- [ ] Siapkan precomputed demo data.
- [ ] Pastikan demo berjalan tanpa internet eksternal.

## C7. Evidence dan Demo Audit

- [ ] Cocokkan semua demo evidence dengan source rows.
- [ ] Hapus reviewer identity.
- [ ] Manual-check predictions pada main/backup cases.
- [ ] Verifikasi metadata conflicts, priority formula, intervention mapping.
- [ ] Siapkan satu rejected/false-positive alert untuk human oversight.

## C8. Presentasi dan Live Demo

- [ ] 0:00–1:00 problem/urgency.
- [ ] 1:00–2:00 dataset insight/hidden complaints.
- [ ] 2:00–3:30 pipeline/leakage prevention.
- [ ] 3:30–4:30 actual evaluation/baseline improvement.
- [ ] 4:30–8:00 live demo end-to-end.
- [ ] 8:00–9:00 impact/pilot/sustainability.
- [ ] 9:00–10:00 Responsible AI/limitations/closing.
- [ ] Latihan <10 menit; diagram terbaca; tanpa identitas institusi.
- [ ] Demo: high-rated destination -> hidden issue -> evidence -> ranking -> verification -> simulator -> regional map.
- [ ] Latih offline flow dan backup recording.

## C9. Q&A dan Pilot

- [ ] Siapkan jawaban: mengapa bukan sentiment dashboard atau LLM/RAG.
- [ ] Siapkan jawaban annotation/agreement, leakage, Macro F1, imbalance, calibration.
- [ ] Siapkan jawaban entity resolution, priority validation, reputational harm.
- [ ] Siapkan jawaban simulator non-causal, failures, scale, DGX, sustainability.
- [ ] Pilot plan: 5–10 diverse destinations.
- [ ] Expert blind review sebelum melihat model ranking.
- [ ] Field verification top alerts; catat confirmed/rejected/uncertain.
- [ ] Metrics: verification rate, time-to-verification, intervention adoption, time saved.
- [ ] Jangan menjanjikan revenue/visitor growth pada prototype.

## C10. Final Gate

- [ ] Produk berjalan di DGX; health checks hijau.
- [ ] Main dan backup demo siap; external dependencies offline.
- [ ] Metrics traceable; evidence dan Responsible AI audits selesai.
- [ ] Presentasi/Q&A rehearsed; slide PDF dan backup recording siap.
- [ ] Runbook dan artifact backup tersedia.
- [ ] Freeze sebelum deadline; setelah freeze hanya perbaiki blocker.

---

# D. Rubric Alignment Gate

## D1. Kebaruan dan Problem Framing — 20

- [ ] Decision gap spesifik dan didukung EDA.
- [ ] Perbedaan dari sentiment dashboard/chatbot jelas.
- [ ] Complete review-to-intervention chain terbukti.
- [ ] Scope sempit, koheren, dan tidak mengikuti tren tanpa alasan.

## D2. Dampak dan Relevansi — 20

- [ ] Target user dan beneficiary jelas.
- [ ] Manfaat operasional terukur.
- [ ] Pilot dan KPI realistis.
- [ ] Dampak lokal Toba eksplisit.
- [ ] Rekomendasi dapat ditindaklanjuti dan diverifikasi.

## D3. Kualitas Teknis AI dan Data — 20

- [ ] Cleaning/entity resolution reproducible.
- [ ] Annotation dan agreement terukur.
- [ ] Leakage-safe split dan locked test.
- [ ] Keyword/TF-IDF/IndoBERT comparison.
- [ ] Actual metrics, calibration, latency, error analysis.
- [ ] Robust offline demo dan model card.

## D4. Kelayakan dan Keberlanjutan — 15

- [ ] Scope realistis untuk hackathon.
- [ ] Docker/DGX deployment berhasil.
- [ ] Batch-first architecture dan offline fallback tersedia.
- [ ] Pilot, feedback loop, dan resource plan tersedia.
- [ ] Future roadmap tidak bergantung pada klaim yang belum terbukti.

## D5. Pemanfaatan Data Toba — 15

- [ ] Reviews dipakai sebagai model input utama.
- [ ] Metadata, facilities, hours, transport terintegrasi.
- [ ] Coordinates dipakai untuk geospatial analytics.
- [ ] Cleaning, entity links, evidence, provenance dapat diaudit.
- [ ] Data eksternal hanya enrichment dan lisensinya terdokumentasi.

## D6. Komunikasi, Demo, Dokumentasi — 10

- [ ] Narasi ringkas dan konsisten.
- [ ] Diagram evaluasi terbaca dan berisi hasil aktual.
- [ ] Demo end-to-end stabil.
- [ ] README, model card, Responsible AI, limitations lengkap.
- [ ] Semua anggota siap Q&A.

---

# E. Go/No-Go Criteria

## E1. Preliminary Go

- [ ] Gold annotation dan split valid.
- [ ] Minimal Keyword dan TF-IDF dievaluasi.
- [ ] IndoBERT memiliki actual metrics atau statusnya dijelaskan jujur.
- [ ] Evidence tidak difabrikasi.
- [ ] Laporan, video, source, dan dokumentasi lengkap.
- [ ] Tidak ada institusi, PII, atau secrets.
- [ ] Submission artifacts diuji oleh anggota lain.

## E2. Final Go

- [ ] Model terhubung ke aplikasi atau fallback berlabel jelas.
- [ ] Produk berjalan offline pada target infrastructure.
- [ ] Main demo chain berfungsi penuh.
- [ ] Semua demo alerts memiliki evidence/provenance.
- [ ] Responsible AI gate terpenuhi.
- [ ] Presentasi dan Q&A siap.

## E3. No-Go Conditions

- [ ] Jangan klaim metric yang belum diukur.
- [ ] Jangan tampilkan evidence generatif/fabrikasi.
- [ ] Jangan sebut simulator sebagai causal prediction.
- [ ] Jangan sebut keyword baseline sebagai trained IndoBERT.
- [ ] Jangan gunakan test set untuk tuning.
- [ ] Jangan membutuhkan internet/model download saat startup final.
- [ ] Jangan tampilkan reviewer identity atau institusi peserta.

---

# F. Final Artifact Inventory

## F1. Data dan EDA

- [x] Project charter. (`SIPATURE-Project-Charter.md`)
- [x] Data inventory dan dictionary. (`docs/data-inventory.md` + `docs/data-dictionary.md`)
- [x] Known issues dan external-data register. (`docs/known-data-issues.md`)
- [x] EDA notebook/report dan figures. (notebook `01` + `docs/eda-report.md`, 16 figures)
- [x] Cleaning pipeline dan funnel. (notebook `02` + `docs/cleaning-entity-resolution-report.md`, `17_cleaning_funnel.png`)
- [x] Clean/quarantine datasets. (`data/interim/*.parquet`)
- [x] Canonical destinations dan entity links. (`data/processed/canonical_destinations.parquet`, `entity_links.parquet`)
- [x] Entity-resolution metrics. (`entity_resolution_metrics.json`)

## F2. Annotation dan Model

- [x] Taxonomy dan annotation guideline. (`taxonomy.yaml` RC1 + `docs/annotation-guideline.md`)
- [x] Sampling manifest. (notebook `03`: pilot/main audit + assignments + `annotation_sampling_summary.json`)
- [x] Annotation JSONL. (`silver-v1.0.0.jsonl` — AI-assisted weak supervision, bukan human gold)
- [x] Agreement dan annotation-audit report. (gold annotation 3 anggota tim selesai → `agreement.json`: aspect Jaccard 0,9664 / polarity 0,9804 / severity κ 1,0; `freeze-gold` → `gold.jsonl` 1.320 records, 117 adjudicated (97 auto + 20 manual), SHA `7b5b6057…`; gold lama diarsip ke `gold-human-v1/`)
- [x] Split manifest dan data hashes. (notebook `04`: `split_manifest_silver_v1.json`, leakage-safe, terkunci)
- [x] Keyword artifact/metrics. (notebook `05`: `keyword-silver-v1-test-metrics.json`)
- [x] TF-IDF model/vectorizer/metrics. (notebook `05`: `tfidf-aspect-silver-v1/model.joblib` + metrics)
- [x] IndoBERT model/tokenizer/config. (notebook `06`: run `20260813-1050_indobert-silver-v1`)
- [x] Thresholds dan calibration artifacts. (notebook `07`: `20260813-1050_indobert-silver-v1_calibration-v1`)
- [x] Locked test metrics dan diagrams. (notebook `07`: `20260813-1050_indobert-silver-v1_locked-test-v1`)
- [x] Model card. (`docs/model-card.md` — metrik silver + gold-v1 terisi lengkap; IndoBERT-vs-gold-v1 0,4254 / polarity 0,5077 ditandai "ditolak")
- [x] Gold baseline evaluation. (notebook `10`: keyword 0,7056 / TF-IDF 0,5777 vs gold-v1; notebook `11`: tabel preliminary-vs-final; notebook `12`: IndoBERT-vs-gold-v1 aspect 0,4254 / polarity 0,5077 — inference-only)
- [ ] Error analysis manual (audit FP/FN 50, kategorisasi negation/implicit/typo, reputational risk).

## F3. Intelligence Engine dan Product

- [x] Review predictions. (notebook `08`: `review-predictions.parquet`, 9.785 aspect predictions)
- [x] Destination signals dan health components. (notebook `08`: `destination-aspect-signals.parquet`, 1.682 signals)
- [x] Intervention queue dan formula/config. (notebook `09`: `expert-review-queue.csv` + `scoring.yaml`)
- [x] Evidence provenance table. (notebook `08`/`09`: `evidence.parquet` + evidence di `app-export.json`)
- [x] Expert/system evaluation. (notebook `09`: queue + sensitivity; review ahli eksternal TIDAK dilakukan — diganti sensitivity analysis sebagai validasi internal)
- [ ] Facility gap analysis dari metadata `Fasilitas` (isi komponen `facility_gap` yang saat ini `None` — rubric D5 pemanfaatan data)
- [ ] Integrasi data transportasi (aksesibilitas/konektivitas) ke analisis geospasial. (rubric D5)
- [x] Evaluasi penggunaan IndoBERT polarity model menggantikan `lexical-polarity-v1` di A9. (gold-v1 polarity 0,5077 ≈ chance vs silver 0,7459 — TIDAK layak dipakai, lexical tetap; notebook `12`)
- [x] SIPATURE source code. (`sipature-app/` + `sipature-api/` + `ml/src/sipature_ml/`)
- [x] API source/schema/docs. (FastAPI `sipature-api` + PostgreSQL `db/schema.sql` + Drizzle ORM)
- [x] Dockerfiles/compose/runbook. (3-service: `web` + `inference` + `db`; `docker-compose.yml`)
- [x] Offline model/data/map fallback. (model & data dibundle di image; `scripts/refresh.sh` satu perintah)
- [x] Smoke/performance test results. (staging rehearsal 2026-08-19: `/health`, `/api/places` 388, `/api/analyze` live TF-IDF + fallback; lihat `docs/dgx-deployment-runbook.md`)

## F4. Submission dan Presentation

- [ ] Laporan Analisis PDF.
- [ ] Preliminary demo video/link.
- [ ] Product source ZIP.
- [ ] Slide pitch/final presentation.
- [ ] Demo script dan backup recording.
- [x] Responsible AI document. (`docs/responsible-ai.md` + section etika di `docs/model-card.md`)
- [ ] Pilot and impact plan.
- [ ] Impact quantification: destinasi terjangkau, review diproses, estimasi eksposur wisatawan, dan time-to-verification. (KPI terukur untuk rubric D2 — 20 poin)
- [x] Q&A answer bank. (`docs/qa-answer-bank.md`)

---

# G. Daily Team Tracker

Gunakan tabel ini setiap hari. Tambahkan baris, bukan mengganti history.

| Tanggal | Fokus | PIC | Output target | Status | Blocker | Keputusan |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-08-19 | Gold annotation → agreement → freeze-gold; gold baselines (keyword/TF-IDF/IndoBERT); staging rehearsal B2 | Tim | `gold.jsonl`, `agreement.json`, notebook `10`/`11`/`12`, `docs/dgx-deployment-runbook.md` | Done | - | Keyword menang di gold (0.78 > TF-IDF 0.64 > IndoBERT 0.48); IndoBERT polarity (0.50) tidak dipakai; deploy verifikasi (388/103/210) |
| 2026-08-19 | Switch gold → gold-v1 (human label revisi); re-eval baseline; update model card + TODO | Tim | `gold.jsonl` (SHA `7b5b6057`), keyword/TF-IDF gold metrics, `model-card.md` | Done | - | Gold baru agreement 0.9664 > lama 0.8638; keyword 0.7056 / TF-IDF 0.5777; IndoBERT-vs-gold-v1 0.4254 / polarity 0.5077 (ditolak) |

Status yang diperbolehkan:

```text
Not started | In progress | Blocked | Review | Done
```

## Daily Stand-up Checklist

- [ ] Apa yang selesai sejak update terakhir?
- [ ] Output artifact mana yang benar-benar dibuat?
- [ ] Metric/quality gate mana yang sudah lolos?
- [ ] Apa blocker saat ini?
- [ ] Keputusan apa yang dibutuhkan hari ini?
- [ ] Apakah scope perlu dipotong untuk melindungi core chain?
- [ ] Apakah ada angka/claim baru yang belum dapat ditelusuri?
- [ ] Apakah backup terbaru tersedia?

## End-of-Day Checklist

- [ ] Commit code/config/documentation yang stabil.
- [ ] Backup artifact besar ke lokasi yang disepakati.
- [ ] Catat model/data/config hashes.
- [ ] Perbarui tracker dan known issues.
- [ ] Catat eksperimen gagal, bukan hanya hasil terbaik.
- [ ] Tentukan satu prioritas tertinggi hari berikutnya.

---

# H. Core Success Statement

SIPATURE dianggap berhasil jika tim dapat membuktikan rantai berikut dengan data dan hasil aktual:

```text
Raw review
-> cleaned and linked data
-> human-verified labels
-> trained and evaluated model
-> calibrated prediction
-> destination signal
-> verbatim evidence
-> explainable priority
-> human verification
-> candidate intervention
```

Jumlah fitur bukan indikator utama. Akurasi, keterlacakan, explainability, dampak operasional, Responsible AI, dan kualitas demo adalah prioritas.
