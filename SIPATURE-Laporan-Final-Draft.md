# SIPATURE

## Sistem Pemantauan Ulasan dan Prioritas Tindak Lanjut Pariwisata Toba

**Laporan Final Round — Del AI Hackathon 2026**

**Nama tim:** `[NAMA TIM]`

**Ketua:** `[ANGGOTA 1 - KETUA]`

**Anggota:** `[ANGGOTA 2]`, `[ANGGOTA 3]`

> Dokumen submission tidak mencantumkan identitas institusi pendidikan. Versi PDF maksimal 25 MB.

---

## Ringkasan Eksekutif

Ulasan wisata menyimpan informasi yang lebih rinci daripada *rating* rata-rata. Destinasi dengan *rating* tinggi tetap dapat menyembunyikan keluhan berulang tentang toilet, akses jalan, pungutan, parkir, atau pelayanan. Ketika volume ulasan mencapai ribuan, pengelola kesulitan membaca semuanya secara rutin dan menentukan isu mana yang perlu diverifikasi lebih dahulu.

SIPATURE adalah *dashboard* dan sistem pendukung keputusan yang mengubah ulasan menjadi **sinyal operasional per destinasi**. Sistem membaca ulasan, memilah isu ke 14 aspek, menentukan arah penilaian, mempertahankan kutipan bukti, dan menyusun prioritas verifikasi. SIPATURE tidak menyatakan bahwa keluhan pasti benar dan tidak menggantikan inspeksi lapangan.

*Pipeline* mengolah 22.302 *record* mentah menjadi 22.169 *record* bersih; 12.234 di antaranya berteks. Benchmark final memakai **human-gold** 1.320 *review* dari tiga anotator (agreement *Jaccard* aspek 0,9664). Terhadap *gold-v1*, deteksi aspek TF-IDF memperoleh *Macro F1* 0,5777 — di bawah *Keyword* (0,7056) tetapi di atas IndoBERT (0,4254). TF-IDF tetap dipilih sebagai model produksi karena merupakan model yang belajar dari data, interpretable, dan CPU-only; *gold* adalah *benchmark evaluasi*, bukan data *training*.

Produk final berjalan sebagai tiga layanan *Docker* (`web` + `inference` + `db`) yang di-deploy ke DGX B200 IT Del secara offline, dengan *latency* p50 2,1 ms per *review*, *alert verification workflow* (konfirmasi/tolak/tidak pasti + alasan), dan *fallback* peta SVG saat tanpa internet. Keluaran operasional mencakup 103 destinasi *actionable* dan 210 isu. Keterbatasan utama: model *severity* tidak tersedia (support kelas `high` < 20), dan *evidence* verbatim ditahan dari aplikasi publik sampai pemeriksaan privasi selesai.

| Indikator Utama | Hasil Aktual | Keterangan |
| --- | ---: | --- |
| *Review* bersih | 22.169 | dari 22.302 *raw* |
| *Review* berteks | 12.234 | *input* NLP |
| *Gold annotation* | 1.320 | 3 anotator, *Jaccard* 0,9664 |
| *Aspect Macro F1* (gold-v1) | 0,5777 | TF-IDF (produksi) |
| IndoBERT aspect (gold-v1) | 0,4254 | ditolak |
| *Canonical destination* | 388 | 322 *anchor* + 66 *unresolved* |
| Destinasi *actionable* | 103 | 210 isu |
| *Latency* `/predict-review` | p50 2,1 ms | CPU-only |

---

# 1. Latar Belakang dan Permasalahan

## 1.1 Konteks Pariwisata Danau Toba

Kawasan Danau Toba memiliki ekosistem pariwisata yang saling bergantung. Pengalaman wisatawan ditentukan bukan hanya oleh daya tarik destinasi, tetapi juga oleh kebersihan, akses jalan, parkir, toilet, keamanan, harga, pelayanan, akomodasi, kuliner, dan transportasi. Masalah pada satu unsur dapat memengaruhi kenyamanan dan citra kawasan secara keseluruhan.

Peningkatan kualitas membutuhkan informasi yang dapat ditindaklanjuti: bukan hanya tempat mana yang populer, tetapi masalah apa yang berulang, berapa banyak bukti yang tersedia, dan apa yang perlu diperiksa lebih dahulu — agar sumber daya terbatas diarahkan pada kebutuhan paling relevan.

## 1.2 Kondisi Data

Dataset panitia mencakup objek wisata, akomodasi, kuliner, transportasi, fasilitas, lokasi, harga, jam operasional, *rating*, dan ulasan. Cakupan ini memungkinkan analisis pariwisata sebagai satu ekosistem. Namun data masih mentah: informasi tersebar di sejumlah file dengan struktur berbeda, nama tempat tidak konsisten, sebagian *field* kosong, dan tidak semua *review* berteks. Data tidak dapat langsung dimasukkan ke model tanpa pembersihan, integrasi, dan penghubungan entitas.

## 1.3 Kesenjangan Keputusan (Decision Gap)

*Rating* rata-rata tidak menjelaskan penyebab pengalaman. Dua destinasi dengan *rating* sama dapat menghadapi masalah berbeda. Membaca ulasan satu per satu juga tidak efisien ketika jumlahnya ribuan; keluhan penting dapat tertutup oleh *review* positif atau tempat bervolume besar. Kebutuhan utamanya bukan sentimen umum, melainkan **aspek yang dibicarakan**, **potongan bukti**, **jumlah dan kecukupan data**, dan **prioritas verifikasi** — tanpa menyatakan keluhan sebagai fakta lapangan.

## 1.4 Rumusan Masalah

> Bagaimana membantu pengelola mengubah ribuan ulasan tersebar menjadi daftar isu spesifik, didukung sinyal yang dapat ditelusuri, dan dapat diprioritaskan untuk verifikasi?

## 1.5 Relevansi dengan Challenge

| Nilai | Kontribusi SIPATURE |
| --- | --- |
| Informatif | Ulasan → 14 aspek + *evidence* + prioritas terjelaskan |
| Efisien | Mengurangi pembacaan manual; *latency* 2,1 ms/*review* |
| Berkelanjutan | Fokus kebersihan/sanitasi/akses; *feedback loop* verifikasi |
| Bernilai | Dasar keputusan operasional untuk pengelola & BPODT |

---

# 2. Analisis Permasalahan

## 2.1 Pemangku Kepentingan

| *Stakeholder* | Kebutuhan | Hambatan |
| --- | --- | --- |
| Pengelola destinasi | Menemukan isu berulang & menentukan pemeriksaan | Volume ulasan besar, tidak terstruktur |
| BPODT/pemerintah | Pola lintas destinasi, alokasi sumber daya | Data tersebar, tidak terintegrasi |
| Wisatawan | Pengalaman lebih baik | Umpan balik belum tertutup |
| Pelaku lokal | Tindak lanjut terarah | Kurang sinyal terstruktur |

## 2.2 Profil Data

Dua file *review* utama (`wisata-v2.csv` 12.691 + `resto-hotel-v2.csv` 9.611) adalah sumber bahasa. Tiga file *metadata* utama menyediakan identitas dan lokasi. File lain berfungsi *enrichment* (jam, fasilitas, transportasi, kuliner). Pemisahan peran mencegah artikel/field pendukung diperlakukan sebagai *ground truth* keliru.

## 2.3 Temuan EDA

- **Skala:** 22.302 *raw* → 22.169 *clean* (12.234 textual, 9.935 rating-only).
- **Rating imbalance:** 15.595 dari 22.243 *rating* integer adalah bintang lima; model mayoritas bisa terlihat baik tanpa menemukan keluhan.
- **Volume vs complaint:** persentase tinggi pada sample kecil tidak stabil → *Bayesian smoothing* + *minimum support*.
- **Metadata:** nama/alamat/koordinat hampir lengkap; fasilitas & jam operasional tidak merata — *field* kosong diperlakukan sebagai "data belum cukup", bukan "tidak ada fasilitas".

## 2.4 Risiko dan Mitigasi

| Risiko | Mitigasi |
| --- | --- |
| Popularity bias | *smoothing*, *minimum support*, *log exposure* |
| *False alert* → reputasi | bahasa netral + verifikasi manusia + *rejected-alert workflow* |
| Sparse label / rare aspect | *stratified sampling*, *Macro F1*, *class weighting* |
| Entity *false merge* | *conservative resolution*, *unresolved placeholder* |
| Data usang | bobot *freshness*, status `Insufficient Data` |

---

# 3. Pendekatan AI dan Modelling

## 3.1 Rantai Solusi

Rantai lengkap dari ulasan mentah hingga tindak lanjut terverifikasi:

![Rantai solusi SIPATURE](docs/figures/diagrams/solution-chain.png)

**Gambar 1. Rantai solusi SIPATURE — dari ulasan menjadi tindak lanjut terverifikasi.**

Tujuh tahap: ulasan mentah dibersihkan dan dihubungkan ke destinasi (*entity resolution*), diproses model deteksi aspek (TF-IDF + lexical polarity), diagregasi menjadi sinyal dan bukti verbatim per destinasi, diprioritaskan secara *missing-aware*, diverifikasi manusia (`confirmed`/`rejected`/`uncertain`), lalu menjadi kandidat tindak lanjut. *Severity* tidak tersedia (support kelas `high` < 20) sehingga tidak diimputasi.

## 3.2 Taxonomy

14 aspek dalam empat kelompok: lingkungan (kebersihan, sampah, sanitasi, kepadatan), infrastruktur (akses, parkir, fasilitas publik), pengalaman (pemandangan, kenyamanan, keamanan, transparansi harga), dan operasional (pelayanan, perawatan, jam operasional).

## 3.3 Annotation

- **Silver** (AI-assisted weak supervision, 3 *rule passes*) untuk *training* dan *benchmark* awal — *bukan* label manusia.
- **Gold** (human, 3 anotator) untuk *benchmark evaluasi*: 1.320 *record*, *agreement* aspek *Jaccard* 0,9664, *polarity* 0,9804, *severity* κ 1,0; 117 *record* di-adjudikasi (97 *auto* + 20 *manual*).

## 3.4 Model yang Dibandingkan

| Model | Metode | Peran |
| --- | --- | --- |
| Keyword | *lexicon* + konteks + kontras | *ceiling* referensi (sirkular di silver) |
| TF-IDF | *word+char* n-gram → OVR *Logistic Regression* | **produksi** |
| IndoBERT | *fine-tune* `indobenchmark/indobert-base-p1` | kandidat (ditolak) |

## 3.5 Split Leakage-Safe

1.320 *record* dibagi **per destinasi** (bukan acak per *review*): 922 train / 196 validation / 202 locked test, 0 *leakage* destinasi/duplikat/teks berulang, seluruh 14 aspek muncul di validation/test.

## 3.6 Polarity & Severity

- **Polarity** produksi: `lexical-polarity-v1` (deterministik, tanpa probabilitas). Kandidat IndoBERT *polarity* ditolak (gold-v1 0,5077 ≈ *chance*).
- **Severity:** `unavailable_no_supported_model` (support kelas `high` 19 < *gate* 20).

---

# 4. Proses Pengembangan Solusi

## 4.1 Tahapan

| Tahap | Output | Status |
| --- | --- | --- |
| Data (inventory, EDA, cleaning, ER) | `canonical_reviews.parquet` | Done |
| Annotation (silver + gold) | `gold.jsonl` (SHA `7b5b6057`) | Done |
| Model (keyword/TF-IDF/IndoBERT) | `tfidf-aspect-silver-v1` | Done |
| Engine (inference, aggregation, priority) | `a9-tfidf-lexical-v1.0.4` | Done |
| Product (API + web + workflow) | 3-service Docker | Done |

## 4.2 Reproducibility

*Seed* 42, konfigurasi YAML per *stage*, *manifest* + SHA-256 di setiap *stage*, dependensi terkunci (`requirements-dev.lock.txt`), dan *locked-test policy* (test dievaluasi sekali, metrik tidak boleh ditimpa).

## 4.3 Teknologi

| Layer | Teknologi |
| --- | --- |
| Data | Python, Pandas, Parquet |
| Model | scikit-learn (TF-IDF), PyTorch (IndoBERT kandidat) |
| API | FastAPI |
| Web | Next.js 15, Leaflet |
| Deployment | Docker Compose, DGX B200 |

---

# 5. Implementasi Produk dan Deployment

## 5.1 Arsitektur

![Deployment tiga layanan di DGX B200](docs/figures/diagrams/deployment-dgx.png)

**Gambar 2. Deployment tiga layanan di host DGX B200.**

Aplikasi *web* (Next.js) membaca data precomputed dari *bundle* A9 yang di-seed ke PostgreSQL, dan memanggil layanan *inference* (FastAPI TF-IDF) untuk analisis *review* live. Ketiga layanan berjalan dalam satu host DGX B200 secara offline.

## 5.2 Fitur

1. **Overview** — metrik, *coverage*, *issues*, prioritas.
2. **Map** — filter kabupaten/kind/aspek/confidence, *fallback* SVG luring.
3. **Detail** — *evidence*, *metadata*, *confidence*, *health*, komponen *missing*.
4. **Queue** — *ranking*, *support*, rekomendasi verifikasi.
5. **Simulator** — asumsi eksplisit + *non-causal warning* permanen.
6. **Analyzer** — model TF-IDF live (mode tercermin di respons).
7. **Verification workflow** — konfirmasi/tolak/tidak pasti + alasan penolakan.

## 5.3 Deployment DGX B200

Docker Compose tiga layanan; model & data di-*bundle* ke image (tanpa *download* saat startup). Offline penuh: map tile eksternal turun ke SVG luring; analyzer turun ke *baseline* bila inference mati. *Health check*, *cold start*, dan *restart* terverifikasi.

## 5.4 Performa

| Metrik | Nilai |
| --- | --- |
| `/predict-review` latency | p50 2,1 ms · p95 3,1 ms |
| `/api/analyze` latency | p50 6,5 ms · p95 9,8 ms |
| *Page load* | 0,05–0,14 s |
| Memory | web 95 MiB · inference 133 MiB · db 23 MiB |

---

# 6. Evaluasi dan Hasil

## 6.1 Benchmark Gold-v1 (human)

![Benchmark deteksi aspek silver vs gold-v1](docs/figures/diagrams/benchmark-gold-v1.png)

**Gambar 3. Perbandingan Macro F1 deteksi aspek pada silver (locked) vs gold-v1 (human).**

| Model | Silver (locked) | Gold-v1 |
| --- | ---: | ---: |
| Keyword | 0,9768 (sirkular) | 0,7056 |
| **TF-IDF (produksi)** | 0,7201 | **0,5777** |
| IndoBERT (aspek) | 0,5247 | 0,4254 |
| IndoBERT (polarity) | 0,7459 | 0,5077 (≈ chance) |

## 6.2 Keputusan Model

TF-IDF tetap menjadi detektor aspek karena merupakan **model yang belajar dari data** (interpretable, CPU-only, cepat), sedangkan *gold* dipakai sebagai **benchmark evaluasi**, bukan data *training*. Menggunakan *gold* untuk melatih akan membuat evaluasi sirkular (1.320 *review* yang sama dipakai evaluasi). *Keyword* lebih tinggi di gold (0,7056) tetapi merupakan *rule engine* yang sama dengan pembuat *silver* — dilaporkan terpisah sebagai *ceiling*.

## 6.3 Entity Resolution

*Reviewed-pair precision* 0,9714, *recall* 0,4304, *false-merge rate* 0,0286; *unresolved* tidak diberi prioritas operasional.

## 6.4 Error Analysis

- **Negasi:** "pungli tidak ada" dapat ter-flag *negative* (limitation *lexical polarity*).
- **Klausa kontras:** "tempat bagus, tapi jalan jelek" → akses kadang `neutral`.
- **Rare aspect:** `opening_hours` *support* kecil → F1 tidak stabil.
- **False-positive case (didokumentasikan):** Danau Sidihoni `scenery` — empat *review* "negatif" ternyata pujian; di-*reject* lewat workflow.

---

# 7. Dampak dan Potensi Pengembangan

## 7.1 Manfaat per Stakeholder

| Pihak | Manfaat | Indikator |
| --- | --- | --- |
| Pengelola destinasi | Temukan isu berulang, mulai dari yang paling didukung | *time-to-verification* |
| BPODT/pemerintah | Pola lintas destinasi, alokasi sumber daya | *coverage* + prioritas |
| Wisatawan | Pengalaman lebih bersih/aman/terawat | tindak lanjut terarah |

## 7.2 Rencana Pilot

5–10 destinasi beragam; *blind review* pengelola sebelum melihat *ranking* model; verifikasi lapangan *top alerts* (catat `confirmed`/`rejected`/`uncertain`); KPI: *verification rate*, *time-to-verification*, *intervention adoption*, *time saved*. Tidak menjanjikan *revenue*/*visitor growth* pada prototipe.

## 7.3 Keberlanjutan

*Feedback* dari *verified/rejected alert* dipakai memperbaiki *taxonomy*, *threshold*, dan bobot; *retraining* periodik; *governance* akses *evidence*; *cost* rendah (CPU-only, model ringan).

## 7.4 Skalabilitas

Arsitektur *batch-first* + SQL; TF-IDF inferensi linear; *entity resolution* berbasis *blocking*; PostgreSQL + indeks; dapat diparalelkan per *batch* untuk wilayah lebih luas.

---

# 8. Responsible AI dan Etika

- **Privasi:** identitas reviewer, review ID, source file/row tidak masuk bundle aplikasi; `verified_by` opaque.
- **Evidence:** verbatim + provenance internal; teks ditahan dari aplikasi publik (`withheld_pending_privacy_review`).
- **Bahasa:** reported issue / early-warning signal, bukan vonis "kotor/berbahaya/tidak layak".
- **Low-support:** Insufficient Data, tidak diranking; unresolved identity tidak diberi prioritas.
- **Human oversight:** setiap alert = kandidat verifikasi; rejected-alert workflow tersedia.
- **Simulator:** non-kausal, asumsi eksplisit.

## 8.1 Kebijakan Data Terbatas (Restricted Data Policy)

![Lapisan data dan kebijakan akses](docs/figures/diagrams/data-pipeline-restricted.png)

**Gambar 4. Lima lapisan data — dari mentah (restricted) ke agregat aman (published).**

Data SIPATURE dibagi lima lapisan dengan tingkat akses berbeda. Lapisan mentah hingga *evidence* hanya dapat diakses tim ML (`restricted`); hanya **agregat aman** yang dipublikasikan ke aplikasi tanpa identitas reviewer:

| Lapisan | Konten | Identitas reviewer | Akses |
| --- | --- | --- | --- |
| Raw CSV | 22.302 record (`wisata-v2`, `resto-hotel-v2`) | ADA (`reviewer-id`, `name`) | restricted |
| Clean Parquet | 22.169 canonical | `review_id` hash | restricted |
| Annotation | 1.320 silver + gold | teks review | restricted |
| Aggregate | 1.682 sinyal + evidence | evidence verbatim | restricted |
| Safe product | app bundle (103 destinasi, 210 isu) | **TIDAK ADA** | published |

![Matriks akses data terbatas](docs/figures/diagrams/restricted-data-policy.png)

**Gambar 5. Matriks akses tiga peran × lima komponen data.**

- **Publik / juri** → hanya agregat aman (*read*).
- **Pengelola destinasi** → agregat aman + workflow verifikasi.
- **Tim Data/ML** → seluruh artefak (*admin*), termasuk raw/annotation/evidence untuk audit.

Prinsip inti: identitas reviewer, review ID, source file/row, teks *evidence*, dan prediksi tingkat *review* **tidak pernah** masuk *bundle* aplikasi publik. *Evidence* ditahan sampai pemeriksaan privasi dan hak akses selesai; generator ekspor memverifikasi *forbidden privacy keys* sebelum publikasi (lihat `docs/restricted-data-policy.md`).

---

# 9. Deklarasi Penggunaan AI

## 9.1 AI dalam Solusi

| Komponen | Model/Metode | Status |
| --- | --- | --- |
| Aspect detection | TF-IDF + OVR Logistic Regression | dilatih (silver) |
| Polarity | lexical fallback (`lexical-polarity-v1`) | deterministik |
| Severity | — | `unavailable_no_supported_model` |

Kandidat IndoBERT (`indobenchmark/indobert-base-p1`) dilatih dan dievaluasi, tetapi **ditolak** untuk produksi (aspect 0,4254 / polarity 0,5077 vs gold-v1).

## 9.2 AI dalam Proses Pengembangan

AI generatif digunakan untuk membantu perancangan solusi, pengembangan kode, *debugging*, audit aturan, dan penyusunan dokumentasi. *AI-assisted weak supervision* menghasilkan *silver labels* (bukan gold). Seluruh *output* AI diperiksa manusia (*lint*, *unit test*, *schema validation*, *hash verification*, pembacaan hasil).

## 9.3 Batas Penggunaan AI

- AI tidak menjadi *ground truth* tanpa verifikasi manusia.
- AI tidak membuat *evidence* baru (kutipan verbatim dari sumber).
- AI tidak menentukan tindakan lapangan otomatis.
- Simulator bukan *causal prediction*.

## 9.4 Deklarasi Kejujuran Hasil

> Seluruh metrik berasal dari evaluasi aktual pada data dan protokol yang dijelaskan. Target, asumsi simulator, dan hasil aktual dibedakan secara eksplisit. Kutipan *evidence* berasal dari dataset dan tidak difabrikasi.

---

## Referensi dan Traceability

1. Del AI Hackathon 2026, *Technical Meeting Final Round*, 19 Agustus 2026.
2. *Scope lock* final: `docs/c1-final-scope-lock.md`.
3. *Model selection & evaluation*: `docs/model-selection-and-evaluation.md`.
4. *Model card*: `docs/model-card.md`.
5. *Performance & reliability*: `docs/c6-performance-reliability.md`.
6. *Evidence & demo audit*: `docs/c7-evidence-demo-audit.md`.
7. *Deployment runbook*: `docs/dgx-deployment-runbook.md`.
8. *Responsible AI*: `docs/responsible-ai.md`.
9. *Restricted data policy*: `docs/restricted-data-policy.md`.
10. *Reproducibility*: `docs/reproducibility-runbook.md`.

**Tabel 20. Hubungan klaim dengan artifact teknis**

| Klaim utama | Artifact |
| --- | --- |
| Gold-v1 (1.320 record) | `ml/data/annotations/gold/gold.jsonl` (SHA `7b5b6057`) |
| Agreement anotasi | `ml/data/annotations/gold/agreement.json` |
| Benchmark gold-v1 | `ml/artifacts/metrics/{keyword,tfidf,indobert}-gold-v1-test-metrics.json` |
| Model produksi | `ml/artifacts/models/tfidf-aspect-silver-v1/` (SHA `a10bddb1`) |
| Inferensi korpus + agregasi | `ml/artifacts/a9/20260813-1713_a9-tfidf-lexical-v1-*` |
| Proyeksi aplikasi | `sipature-app/src/data/generated/{places,interventions,corpus}.json` |
| Latency/performa | `docs/c6-performance-reliability.md` |

> *Raw data*, teks *evidence*, *review-level predictions*, *annotation*, *split records*, model *artifact*, dan *error cases* bersifat *restricted* dan tidak dipublikasikan tanpa pemeriksaan lisensi, privasi, dan hak akses.
