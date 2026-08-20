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

Tabel ringkasan berikut merangkum indikator utama implementasi dan hasil evaluasi SIPATURE:

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

Berdasarkan kesenjangan antara ketersediaan data ulasan yang melimpah dan kebutuhan operasional pengelola di lapangan, perumusan masalah utama dalam pengembangan sistem ini diarahkan pada efektivitas ekstraksi sinyal dan prioritisasi tindak lanjut:

> Bagaimana membantu pengelola mengubah ribuan ulasan tersebar menjadi daftar isu spesifik, didukung sinyal yang dapat ditelusuri, dan dapat diprioritaskan untuk verifikasi?

## 1.5 Relevansi dengan Challenge

Pengembangan SIPATURE dirancang secara spesifik untuk menjawab tantangan tata kelola pariwisata berbasis kecerdasan buatan dengan mengedepankan empat pilar nilai utama: informatif, efisien, berkelanjutan, dan bernilai operasional. Matriks kontribusi sistem terhadap nilai-nilai tersebut dirinci pada tabel berikut:

| Nilai | Kontribusi SIPATURE |
| --- | --- |
| Informatif | Ulasan → 14 aspek + *evidence* + prioritas terjelaskan |
| Efisien | Mengurangi pembacaan manual; *latency* 2,1 ms/*review* |
| Berkelanjutan | Fokus kebersihan/sanitasi/akses; *feedback loop* verifikasi |
| Bernilai | Dasar keputusan operasional untuk pengelola & BPODT |

---

# 2. Analisis Permasalahan

## 2.1 Pemangku Kepentingan

Keberhasilan intervensi pariwisata memerlukan pemahaman menyeluruh terhadap ekosistem pemangku kepentingan di Kawasan Danau Toba. Setiap pihak memiliki kebutuhan informasi yang berbeda serta menghadapi hambatan operasional tersendiri dalam memanfaatkan umpan balik wisatawan:

| *Stakeholder* | Kebutuhan | Hambatan |
| --- | --- | --- |
| Pengelola destinasi | Menemukan isu berulang & menentukan pemeriksaan | Volume ulasan besar, tidak terstruktur |
| BPODT/pemerintah | Pola lintas destinasi, alokasi sumber daya | Data tersebar, tidak terintegrasi |
| Wisatawan | Pengalaman lebih baik | Umpan balik belum tertutup |
| Pelaku lokal | Tindak lanjut terarah | Kurang sinyal terstruktur |

## 2.2 Profil Data

Dua file *review* utama (`wisata-v2.csv` 12.691 + `resto-hotel-v2.csv` 9.611) adalah sumber bahasa. Tiga file *metadata* utama menyediakan identitas dan lokasi. File lain berfungsi *enrichment* (jam, fasilitas, transportasi, kuliner). Pemisahan peran mencegah artikel/field pendukung diperlakukan sebagai *ground truth* keliru.

## 2.3 Temuan EDA

Eksplorasi data awal (*Exploratory Data Analysis*) dilakukan untuk memahami karakteristik teks, pola distribusi rating, dan kelengkapan metadata sebelum perancangan model. Temuan-temuan kunci dari analisis ini meliputi:

- **Skala:** 22.302 *raw* → 22.169 *clean* (12.234 textual, 9.935 rating-only).
- **Rating imbalance:** 15.595 dari 22.243 *rating* integer adalah bintang lima; model mayoritas bisa terlihat baik tanpa menemukan keluhan.
- **Volume vs complaint:** persentase tinggi pada sample kecil tidak stabil → *Bayesian smoothing* + *minimum support*.
- **Metadata:** nama/alamat/koordinat hampir lengkap; fasilitas & jam operasional tidak merata — *field* kosong diperlakukan sebagai "data belum cukup", bukan "tidak ada fasilitas".

## 2.4 Risiko dan Mitigasi

Penerapan kecerdasan buatan untuk mendukung keputusan publik membawa risiko bias algoritma, kesalahan penggabungan data, dan potensi dampak negatif terhadap reputasi destinasi. Oleh karena itu, SIPATURE menerapkan strategi mitigasi ketat di setiap lapisan proses:

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

Arsitektur solusi SIPATURE dibangun sebagai rantai pemrosesan end-to-end yang mengubah ulasan mentah multi-sumber menjadi rekomendasi tindak lanjut yang dapat diverifikasi oleh pengelola:

![Rantai solusi SIPATURE](docs/figures/diagrams/solution-chain.png)

**Gambar 1. Rantai solusi SIPATURE — dari ulasan menjadi tindak lanjut terverifikasi.**

**Interpretasi Gambar 1.** Tujuh tahap: ulasan mentah dibersihkan dan dihubungkan ke destinasi (*entity resolution*), diproses model deteksi aspek (TF-IDF + lexical polarity, ditandai *focal*), diagregasi menjadi sinyal dan bukti verbatim per destinasi, diprioritaskan secara *missing-aware*, diverifikasi manusia (`confirmed`/`rejected`/`uncertain`), lalu menjadi kandidat tindak lanjut. *Severity* tidak tersedia (support kelas `high` < 20) sehingga tidak diimputasi.

## 3.2 Taxonomy

Taksonomi aspek dirancang untuk menangkap spektrum permasalahan pariwisata secara terstruktur. Sebanyak 14 aspek dikelompokkan ke dalam empat pilar operasional:
1. **Lingkungan:** `cleanliness` (kebersihan umum), `trash` (pengelolaan sampah), `sanitation` (kondisi toilet/sanitasi), dan `crowd` (kepadatan pengunjung).
2. **Infrastruktur:** `access` (akses jalan/kemudahan tempuh), `parking` (ketersediaan & tarif parkir), serta `public_facility` (sarana ibadah, gazebo, penerangan).
3. **Pengalaman:** `scenery` (daya tarik alam/keindahan visual), `comfort` (kenyamanan beraktivitas), `safety` (keamanan lingkungan), dan `price_transparency` (kewajaran harga, tarif tidak resmi/pungli).
4. **Operasional:** `service` (keramahan & sikap staf), `maintenance` (perawatan sarana), dan `opening_hours` (kesesuaian jam operasional).

## 3.3 Annotation

Untuk melatih dan menguji model deteksi aspek secara andal, SIPATURE menerapkan strategi anotasi berjenjang yang memisahkan dataset pelatihan dari dataset tolok ukur evaluasi:

- **Silver** (AI-assisted weak supervision, 3 *rule passes*) untuk *training* dan *benchmark* awal — *bukan* label manusia.
- **Gold** (human, 3 anotator) untuk *benchmark evaluasi*: 1.320 *record*, *agreement* aspek *Jaccard* 0,9664, *polarity* 0,9804, *severity* κ 1,0; 117 *record* di-adjudikasi (97 *auto* + 20 *manual*).

## 3.4 Model yang Dibandingkan

Eksperimen pemodelan mengevaluasi tiga pendekatan berbeda untuk menemukan keseimbangan optimal antara akurasi generalisasi, interpretabilitas, dan efisiensi komputasi:

| Model | Metode | Peran |
| --- | --- | --- |
| Keyword | *lexicon* + konteks + kontras | *ceiling* referensi (sirkular di silver) |
| TF-IDF | *word+char* n-gram → OVR *Logistic Regression* | **produksi** |
| IndoBERT | *fine-tune* `indobenchmark/indobert-base-p1` | kandidat (ditolak) |

## 3.5 Split Leakage-Safe

1.320 *record* dibagi **per destinasi** (bukan acak per *review*): 922 train / 196 validation / 202 locked test, 0 *leakage* destinasi/duplikat/teks berulang, seluruh 14 aspek muncul di validation/test.

## 3.6 Polarity & Severity

Penentuan arah sentimen (*polarity*) dan tingkat keparahan (*severity*) dirancang dengan prinsip kehati-hatian matematis untuk mencegah kesimpulan yang tidak didukung data:

- **Polarity** produksi: `lexical-polarity-v1` (deterministik, tanpa probabilitas). Kandidat IndoBERT *polarity* ditolak (gold-v1 0,5077 ≈ *chance*).
- **Severity:** `unavailable_no_supported_model` (support kelas `high` 19 < *gate* 20).

---

# 4. Proses Pengembangan Solusi

## 4.1 Tahapan

Pengembangan solusi SIPATURE dilaksanakan secara sistematis melalui lima fase terukur, mulai dari pengolahan data mentah hingga penyediaan sistem terintegrasi:

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

Tumpukan teknologi (*tech stack*) dipilih untuk memastikan kinerja inferensi yang cepat, konsumsi memori rendah, dan kemampuan operasional luring (*offline*):

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

Sistem SIPATURE diimplementasikan dengan arsitektur multi-layanan mandiri (*self-contained*) yang siap dijalankan pada lingkungan komputasi terisolasi:

![Deployment tiga layanan di DGX B200](docs/figures/diagrams/deployment-dgx.png)

**Gambar 2. Deployment tiga layanan di host DGX B200.**

**Interpretasi Gambar 2.** Browser (juri/demo) memanggil *web* Next.js melalui HTTPS. *Web* membaca data precomputed dari PostgreSQL (`READ`), dan untuk analisis *review* live memanggil layanan *inference* FastAPI yang memuat model TF-IDF ter-bundle (`LIVE`). Ketiga layanan berjalan dalam satu host DGX B200; model dan data sudah di-*bundle* ke image sehingga tidak ada *download* saat *startup* dan demo berjalan penuh tanpa internet eksternal.

## 5.2 Fitur

Aplikasi antarmuka SIPATURE menyediakan 7 modul fungsional utama yang saling terhubung untuk mendukung alur kerja pemantauan dan pengambilan keputusan:

1. **Overview** — Ringkasan metrik kesehatan pariwisata, *coverage* data, rekapitulasi isu, dan daftar prioritas tertinggi.
2. **Map** — Peta interaktif dengan filter kabupaten, kategori destinasi (*kind*), aspek permasalahan, dan tingkat *confidence*, dilengkapi *fallback* SVG luring.
3. **Detail** — Pemeriksaan mendalam per destinasi mencakup *evidence* ulasan, *metadata*, skor *confidence*, indikator *health*, dan komponen data yang belum lengkap (*missing*).
4. **Queue** — Antrean verifikasi operasional dengan *ranking* prioritas, tingkat dukungan bukti (*support*), dan rekomendasi tindakan.
5. **Simulator** — Alat simulasi dampak intervensi berbasis asumsi eksplisit dengan peringatan permanen sifat non-kausal (*non-causal warning*).
6. **Analyzer** — Pengujian teks ulasan interaktif secara *live* menggunakan model TF-IDF produksi.
7. **Verification workflow** — Alur validasi sinyal lapangan bagi pengelola (opsi konfirmasi, tolak, atau tidak pasti beserta alasan penolakan).

## 5.3 Deployment DGX B200

Docker Compose tiga layanan; model & data di-*bundle* ke image (tanpa *download* saat startup). Offline penuh: map tile eksternal turun ke SVG luring; analyzer turun ke *baseline* bila inference mati. *Health check*, *cold start*, dan *restart* terverifikasi.

## 5.4 Performa

Pengujian performa menunjukkan bahwa sistem beroperasi dengan latensi sangat rendah dan efisiensi memori yang tinggi pada satu node DGX B200:

| Metrik | Nilai |
| --- | --- |
| `/predict-review` latency | p50 2,1 ms · p95 3,1 ms |
| `/api/analyze` latency | p50 6,5 ms · p95 9,8 ms |
| *Page load* | 0,05–0,14 s |
| Memory | web 95 MiB · inference 133 MiB · db 23 MiB |

---

# 6. Evaluasi dan Hasil

## 6.1 Benchmark Gold-v1 (human)

Evaluasi model dilakukan secara independen terhadap dataset uji terkunci *gold-v1* (1.320 ulasan beranotasi manusia) untuk mengukur performa nyata di luar data pelatihan:

![Benchmark deteksi aspek silver vs gold-v1](docs/figures/diagrams/benchmark-gold-v1.png)

**Gambar 3. Perbandingan Macro F1 deteksi aspek pada silver (locked) vs gold-v1 (human).**

| Model | Silver (locked) | Gold-v1 |
| --- | ---: | ---: |
| Keyword | 0,9768 (sirkular) | 0,7056 |
| **TF-IDF (produksi)** | 0,7201 | **0,5777** |
| IndoBERT (aspek) | 0,5247 | 0,4254 |
| IndoBERT (polarity) | 0,7459 | 0,5077 (≈ chance) |

**Interpretasi Gambar 3.** Bar kiri adalah *agreement* terhadap *silver* (weak supervision), bar kanan terhadap *gold-v1* (manusia). *Keyword* turun drastis dari 0,9768 ke 0,7056 — menegaskan bahwa skor *silver*-nya sirkular. TF-IDF turun dari 0,7201 ke 0,5777, penurunan yang wajar karena *gold* lebih ketat; angka ini adalah ukuran jujur terhadap penilaian manusia. IndoBERT tetap paling rendah (0,4254). Karena itu TF-IDF dipertahankan sebagai model produksi, dengan alasan lengkap pada §6.2.

## 6.2 Keputusan Model — mengapa TF-IDF (dilatih silver) dipilih

**Mengapa model produksi dilatih pada *silver labels*, bukan *gold*?** Karena *gold* adalah *benchmark evaluasi*, bukan data *training*. Ketiga alasan berikut menjawab pertanyaan juri yang paling sering muncul:

1. **Circularity / leakage.** 1.320 *review* *gold* adalah persis *split* yang dipakai evaluasi. Melatih di *gold* lalu menguji di *gold* berarti model menghafal jawaban — persis seperti *Keyword* 0,9768 di *silver* yang kami ungkap sebagai *ceiling*, bukan prestasi. Nilai F1 yang dihasilkan tidak akan bermakna.
2. **Generalisasi.** *Gold* hanya 1.320 *review*, sedangkan produksi harus memprediksi 12.234 *review* berteks. *Silver* menyediakan data *training* yang sama besarnya dan sudah dipakai sejak awal untuk melatih.
3. **Independensi *benchmark*.** *Gold* dibuat justru agar independen dari model; memakainya untuk melatih akan menghancurkan fungsinya sebagai pengukur yang jujur.

**Lalu mengapa bukan *Keyword* (0,7056 > TF-IDF 0,5777 di gold)?** *Keyword* adalah *rule engine* leksikal yang *sama* dengan pembuat *silver labels* — bukan model yang belajar dari data. Ia tinggi di *silver* (0,9768) justru karena sirkular, dan tetap tinggi di *gold* karena lexikon *taxonomy*-nya kebetulan cocok dengan penilaian manusia. Memilih *Keyword* berarti memilih *rules* yang sudah kami tulis sendiri, bukan model yang menggeneralisasi. Kami melaporkan keduanya secara terpisah dan tidak menyembunyikan gap ini.

**Dan mengapa bukan IndoBERT?** IndoBERT (124,5M param, fine-tune 4 *epoch*) memperoleh aspek 0,4254 dan *polarity* 0,5077 (≈ *chance*) di *gold-v1* — keduanya di bawah TF-IDF. Pada data kecil (922 *train*) dengan label lemah dan distribusi aspek timpang, kompleksitas tidak otomatis memberi hasil lebih baik; IndoBERT juga lebih mahal (GPU) dan kurang interpretable.

**Kesimpulan:** TF-IDF + *One-vs-Rest Logistic Regression* dipilih sebagai detektor aspek karena (a) model yang benar-benar belajar dari data, (b) *interpretable* dan deterministik, (c) CPU-only dengan *latency* p50 2,1 ms, (d) dapat dimuat ulang secara offline, dan (e) hasil *gold-v1*-nya (0,5777) adalah angka jujur terhadap penilaian manusia. *Upgrade* yang benar di masa depan adalah menambah anotasi manusia (held-out set baru) lalu melatih ulang — bukan memakai *gold* yang sama sebagai *training*.

## 6.3 Entity Resolution

Resolusi entitas diterapkan secara konservatif untuk menggabungkan variasi penamaan destinasi dari berbagai sumber data tanpa menimbulkan penggabungan keliru (*false merge*). Evaluasi pada pasangan entitas teranotasi menghasilkan *reviewed-pair precision* 0,9714, *recall* 0,4304, dan *false-merge rate* sangat rendah sebesar 0,0286. Entitas yang belum dapat diselesaikan (*unresolved*) tetap disimpan secara terpisah dan tidak dimasukkan ke dalam antrean prioritas operasional guna mencegah salah sasaran.

## 6.4 Error Analysis

Analisis kualitatif terhadap kesalahan prediksi dilakukan untuk mengidentifikasi batasan linguistik model dan menyediakan konteks bagi alur verifikasi manusia:

- **Negasi:** "pungli tidak ada" dapat ter-flag *negative* (limitation *lexical polarity*).
- **Klausa kontras:** "tempat bagus, tapi jalan jelek" → akses kadang `neutral`.
- **Rare aspect:** `opening_hours` *support* kecil → F1 tidak stabil.
- **False-positive case (didokumentasikan):** Danau Sidihoni `scenery` — empat *review* "negatif" ternyata pujian; di-*reject* lewat workflow.

---

# 7. Dampak dan Potensi Pengembangan

## 7.1 Manfaat per Stakeholder

Implementasi SIPATURE mentransformasi tumpukan ulasan pasif menjadi alat pengambil keputusan yang terukur bagi seluruh pemangku kepentingan:

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

Penerapan kecerdasan buatan pada domain pelayanan publik menuntut kepatuhan ketat terhadap prinsip transparansi, privasi individu, akuntabilitas, dan pengawasan manusia. SIPATURE memegang teguh komitmen etika berikut:

- **Privasi:** identitas reviewer, review ID, source file/row tidak masuk bundle aplikasi; `verified_by` opaque.
- **Evidence:** verbatim + provenance internal; teks ditahan dari aplikasi publik (`withheld_pending_privacy_review`).
- **Bahasa:** reported issue / early-warning signal, bukan vonis "kotor/berbahaya/tidak layak".
- **Low-support:** Insufficient Data, tidak diranking; unresolved identity tidak diberi prioritas.
- **Human oversight:** setiap alert = kandidat verifikasi; rejected-alert workflow tersedia.
- **Simulator:** non-kausal, asumsi eksplisit.

## 8.1 Kebijakan Data Terbatas (Restricted Data Policy)

Perlindungan privasi data diterapkan melalui pemisahan ketat antara lingkungan pengolahan data internal dan distribusi aplikasi publik:

![Lapisan data dan kebijakan akses](docs/figures/diagrams/data-pipeline-restricted.png)

**Gambar 4. Lima lapisan data — dari mentah (restricted) ke agregat aman (published).**

**Interpretasi Gambar 4.** Data mengalir dari kiri ke kanan melalui empat transformasi, dengan **PRIVACY GATE** (ditandai aksen) sebagai batas kritis: hanya agregat aman yang menyeberang ke sisi publik. Identitas reviewer berangsur hilang — dari `reviewer-id`/`name` di lapisan *raw*, menjadi `review_id` hash, teks *review*, *evidence* verbatim, hingga **tidak ada sama sekali** di *bundle* produk. Dua jalur konsumsi (*batch* dan *live*) memakai data yang sama secara deterministik dan hash-verified.

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

**Interpretasi Gambar 5.** Empat komponen terbatas (`raw`, `clean`, *annotation*, *evidence*) hanya `Admin` bagi tim ML — publik dan pengelola `None`. Hanya **safe aggregate** yang `Read` oleh publik (sel yang ditandai aksen = batas publikasi). Matriks ini membuktikan privasi-by-design: meskipun pipeline menyimpan data mentah untuk audit, aplikasi publik hanya pernah menerima agregat tanpa identitas reviewer.

Matriks izin akses antar peran pengguna diatur dengan batasan yang tegas:
- **Publik / juri** → hanya agregat aman (*read*).
- **Pengelola destinasi** → agregat aman + workflow verifikasi.
- **Tim Data/ML** → seluruh artefak (*admin*), termasuk raw/annotation/evidence untuk audit.

Prinsip inti: identitas reviewer, review ID, source file/row, teks *evidence*, dan prediksi tingkat *review* **tidak pernah** masuk *bundle* aplikasi publik. *Evidence* ditahan sampai pemeriksaan privasi dan hak akses selesai; generator ekspor memverifikasi *forbidden privacy keys* sebelum publikasi (lihat `docs/restricted-data-policy.md`).

---

# 9. Deklarasi Penggunaan AI

## 9.1 AI dalam Solusi

Penggunaan model AI di dalam arsitektur operasional SIPATURE dibatasi pada tugas ekstraksi sinyal berbasis bukti dan diklasifikasikan berdasarkan status kesiapan produksinya:

| Komponen | Model/Metode | Status |
| --- | --- | --- |
| Aspect detection | TF-IDF + OVR Logistic Regression | dilatih (silver) |
| Polarity | lexical fallback (`lexical-polarity-v1`) | deterministik |
| Severity | — | `unavailable_no_supported_model` |

Kandidat IndoBERT (`indobenchmark/indobert-base-p1`) dilatih dan dievaluasi, tetapi **ditolak** untuk produksi (aspect 0,4254 / polarity 0,5077 vs gold-v1).

## 9.2 AI dalam Proses Pengembangan

AI generatif digunakan untuk membantu perancangan solusi, pengembangan kode, *debugging*, audit aturan, dan penyusunan dokumentasi. *AI-assisted weak supervision* menghasilkan *silver labels* (bukan gold). Seluruh *output* AI diperiksa manusia (*lint*, *unit test*, *schema validation*, *hash verification*, pembacaan hasil).

## 9.3 Batas Penggunaan AI

Untuk menjaga keandalan dan etika sistem pendukung keputusan, kami menetapkan batas tegas yang tidak boleh dilanggar oleh komponen kecerdasan buatan:

- AI tidak menjadi *ground truth* tanpa verifikasi manusia.
- AI tidak membuat *evidence* baru (kutipan verbatim dari sumber).
- AI tidak menentukan tindakan lapangan otomatis.
- Simulator bukan *causal prediction*.

## 9.4 Deklarasi Kejujuran Hasil

Komitmen terhadap integritas ilmiah dan keterbukaan hasil evaluasi dideklarasikan secara tertulis sebagai berikut:

> Seluruh metrik berasal dari evaluasi aktual pada data dan protokol yang dijelaskan. Target, asumsi simulator, dan hasil aktual dibedakan secara eksplisit. Kutipan *evidence* berasal dari dataset dan tidak difabrikasi.

---

## Referensi dan Traceability

Daftar dokumen rujukan dan panduan teknis yang menjadi acuan penyusunan solusi SIPATURE:

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

Seluruh klaim kuantitatif dan kualitatif dalam laporan ini dapat ditelusuri ke artefak teknis dan repositori data yang bersangkutan melalui matriks keterlacakan berikut:

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

