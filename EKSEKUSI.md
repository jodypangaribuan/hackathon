# MARTAHUTA — Rencana Eksekusi Preliminary & Final

> Dokumen operasional. Bukan ide, bukan spesifikasi — ini **daftar apa yang dikerjakan, siapa, kapan, dan kapan dianggap selesai.**
> Pendamping: [`IDEAS.md`](./IDEAS.md) (analisis & ide) · [`IDE-1-MARTAHUTA-Detail.md`](./IDE-1-MARTAHUTA-Detail.md) (spesifikasi model)
>
> **Disusun 26 Juli 2026 · Sisa waktu preliminary: 7 hari**

---

## Daftar Isi

**BAGIAN A — PRELIMINARY ROUND**
1. [Kalender & titik kritis](#1-kalender--titik-kritis)
2. [Pembagian peran tim](#2-pembagian-peran-tim)
3. [Setup H0 (hari ini, 2 jam)](#3-setup-h0-hari-ini-2-jam)
4. [Protokol pelabelan — bottleneck utama](#4-protokol-pelabelan--bottleneck-utama)
5. [Rencana harian H1–H8](#5-rencana-harian-h1h8)
6. [Struktur LaporanAnalisis.pdf (8 bab wajib)](#6-struktur-laporananalisispdf-8-bab-wajib)
7. [Skrip video demo](#7-skrip-video-demo)
8. [Checklist submission](#8-checklist-submission)
9. [Mode kegagalan & rencana cadangan](#9-mode-kegagalan--rencana-cadangan)

**BAGIAN B — MASA TUNGGU (3–20 Agustus)**
10. [Yang dikerjakan selama menunggu](#10-yang-dikerjakan-selama-menunggu)

**BAGIAN C — FINAL ROUND**
11. [Kalender final](#11-kalender-final)
12. [Persiapan sebelum berangkat](#12-persiapan-sebelum-berangkat)
13. [Rencana lockdown jam-per-jam](#13-rencana-lockdown-jam-per-jam)
14. [Deployment di DGX B200](#14-deployment-di-dgx-b200)
15. [Skrip presentasi 10 menit + Q&A](#15-skrip-presentasi-10-menit--qa)

**BAGIAN D — APLIKASINYA**
16. [Arsitektur & tech stack](#16-arsitektur--tech-stack)
17. [Empat layar, wireframe lengkap](#17-empat-layar-wireframe-lengkap)
18. [Kontrak API](#18-kontrak-api)
19. [Aturan emas: precompute semuanya](#19-aturan-emas-precompute-semuanya)

---
---

# BAGIAN A — PRELIMINARY ROUND

## 1. Kalender & Titik Kritis

| Hari | Tanggal | Fokus | Titik kritis |
|---|---|---|---|
| **H1** | Min, 26 Jul | Setup + parsing tanggal + **mulai pelabelan** | Pelabelan harus mulai hari ini |
| **H2** | Sen, 27 Jul | Entity resolution + pelabelan | — |
| **H3** | Sel, 28 Jul | **Pelabelan SELESAI** + baseline TF-IDF | 🔴 Bila pelabelan belum selesai, semua mundur |
| **H4** | Rab, 29 Jul | Fine-tune IndoBERT + evaluasi | 🔴 Angka F1 final harus ada malam ini |
| **H5** | Kam, 30 Jul | Friction Index + geo gap + bias audit | — |
| **H6** | Jum, 31 Jul | UMKM + file Tier-1 + semua grafik | 🔴 **Freeze analisis.** Setelah ini tidak ada angka baru |
| **H7** | Sab, 1 Agu | Rekam video + tulis laporan | — |
| **H8** | Min, 2 Agu | Buffer + **submit pukul 18:00** | 🔴 Submit 2 jam sebelum deadline 20:00 |

> **Aturan freeze:** setelah H6 malam, tidak boleh ada eksperimen model baru. Angka apa pun yang belum jadi pada saat itu **dibuang**, bukan dikejar. Laporan dan video yang belum selesai membunuh nilai lebih cepat daripada F1 yang kurang 0,03.

---

## 2. Pembagian Peran Tim

Maksimal 3 orang (§14). Peran tetap, tapi **pelabelan dikerjakan bertiga**.

| | Peran | Tanggung jawab utama | File yang dimiliki |
|---|---|---|---|
| **A** | Data Engineer | Parsing tanggal, entity resolution, geospasial, integrasi Tier-1 | `1_parse_dates.py`, `2_entity_resolve.py`, `6_geo_gap.py` |
| **B** | ML Engineer | Pelabelan tooling, training, evaluasi, Friction Index | `3_absa_label.py`, `4_absa_train.py`, `5_friction_index.py` |
| **C** | Analyst & Comms | Laporan, grafik, video, slide, mockup aplikasi, model card | `demo.ipynb`, laporan, video |

**Aturan koordinasi:**
- Stand-up 15 menit tiap pagi (09.00) dan sore (20.00). Tiga pertanyaan: kemarin apa, hari ini apa, terhambat apa.
- Semua ke Git sejak H1. Commit minimal 2× sehari.
- C **tidak menunggu** A dan B selesai. C menulis bab laporan yang tidak bergantung angka (Latar Belakang, Analisis Permasalahan) sejak H1.

---

## 3. Setup H0 (hari ini, 2 jam)

Kerjakan bertiga, sekarang, sebelum apa pun yang lain.

```bash
mkdir -p martahuta/{data/raw,data/interim,src,notebooks,outputs,figures,docs}
cd martahuta && git init

# Salin dataset, JANGAN pernah diubah
cp "/Users/jody/Documents/Hackathon/Datasets/"*.csv data/raw/

python3 -m venv .venv && source .venv/bin/activate
pip install pandas numpy scikit-learn matplotlib seaborn \
            rapidfuzz transformers torch datasets \
            statsmodels folium geopy jupyter
pip freeze > requirements.txt
```

`README.md` awal — isi 5 baris saja: nama produk, satu kalimat masalah, cara menjalankan, struktur folder, status. Diperbarui tiap hari.

**Definition of done H0:** ketiga anggota bisa `git clone`, jalankan `jupyter notebook`, dan membaca `data/raw/` tanpa error.

---

## 4. Protokol Pelabelan — Bottleneck Utama

**Ini satu-satunya hal yang bisa menggagalkan seluruh rencana.** Tanpa data berlabel, tidak ada F1; tanpa F1, kriteria 3 (20 poin) hilang.

### 4.1 Target

| Item | Angka |
|---|---|
| Total review dilabeli | **500** |
| Overlap untuk κ (dilabeli ketiganya) | 60 |
| Pembagian sisanya | 440 ÷ 3 ≈ 147 per orang |
| Kecepatan realistis | 60–80 review/jam |
| Total waktu per orang | ± 3 jam, dipecah 3 sesi |

### 4.2 Sampling — jangan asal ambil

Sampling **stratified**, bukan acak, dan **bukan hanya yang negatif**:

```
Per aspek (10 aspek), ambil:
  - 25 review yang mengandung kata kunci aspek & rating 4–5   (contoh POSITIF)
  - 25 review yang mengandung kata kunci aspek & rating 1–3   (contoh NEGATIF)
Plus 100 review acak tanpa kata kunci                          (contoh NETRAL / tanpa aspek)
```

> ⚠️ Kalau hanya melabeli review negatif, model belajar bahwa "menyebut toilet = keluhan", padahal *"toiletnya bersih"* adalah sinyal positif yang justru menjadi penyebut dalam `neg_rate`. Ini kesalahan paling umum dan paling mematikan.

### 4.3 Format label

Satu review bisa punya 0, 1, atau banyak aspek.

| kolom | isi |
|---|---|
| `review_id` | id unik |
| `text` | teks review |
| `aspect` | salah satu dari 10 aspek, atau `none` |
| `sentiment` | `positif` / `negatif` / `netral` |
| `evidence` | potongan teks pendukung (opsional tapi sangat berguna untuk demo) |
| `labeler` | A / B / C |

### 4.4 Pedoman keputusan (sepakati di awal, tulis di `docs/labeling_guide.md`)

- **Pungli vs mahal biasa** — *"tiketnya mahal"* = `harga_pungli` negatif. *"harga wajar"* = `harga_pungli` positif. *"bayar parkir 10K padahal di luar"* = `harga_pungli` negatif (bukan `parkir`).
- **Implisit tetap dihitung** — *"udah pakai air Danau Toba minta bayar lagi"* = `harga_pungli` negatif, meski tidak ada kata "pungli". Inilah yang membuat model mengalahkan keyword matching.
- **Sarkasme** → ikuti maksud, bukan kata.
- **Bahasa Batak / singkatan** → kalau ragu, tandai `unsure` dan bahas saat stand-up. Jangan tebak diam-diam.
- **Review satu kata** (*"keren"*, *"mantap"*) → `none`.

### 4.5 Kontrol kualitas

Setelah 60 review overlap selesai (H1 malam), **hitung Cohen's κ sebelum melanjutkan**.

| κ | Tindakan |
|---|---|
| > 0,7 | Lanjut, pedoman sudah cukup jelas |
| 0,5–0,7 | Diskusi 30 menit, perjelas pedoman, lanjut |
| < 0,5 | **Berhenti.** Pedoman rusak. Perbaiki definisi aspek, ulangi 60 review |

Angka κ ini **masuk ke laporan** — ia bukti bahwa label Anda kredibel, dan hampir tidak ada tim hackathon yang melaporkannya.

---

## 5. Rencana Harian H1–H8

### H1 — Minggu, 26 Juli · *Fondasi + mulai melabeli*

| Siapa | Tugas | Selesai bila |
|---|---|---|
| A | `1_parse_dates.py`: tangani `"a year ago"`, `"2 tahun lalu di"`, `"Edited 3 months ago"`, 279 kosong | `date_est` (YYYY-MM) terisi, laporkan % berhasil parse + histogram per tahun |
| B | Bangun `3_absa_label.py` (skrip CLI/notebook sederhana), siapkan sampel stratified 500 | File `to_label.csv` siap dibagi |
| C | Tulis `docs/labeling_guide.md` + mulai Bab 1–2 laporan | Pedoman disepakati bertiga |
| **Bertiga** | **Labeli 60 review overlap**, hitung κ | κ terhitung dan tercatat |

**Output H1:** `data/interim/reviews_dated.csv`, `docs/labeling_guide.md`, nilai κ.

---

### H2 — Senin, 27 Juli · *Menyatukan entitas*

| Siapa | Tugas | Selesai bila |
|---|---|---|
| A | `2_entity_resolve.py` bertingkat: exact → fuzzy (rapidfuzz ≥85) → blocking geo <200 m → embedding. Tangani `Pondok Siliwangi 27–31` | `outputs/places_unified.csv` (±330 baris) |
| A | **Buat ground truth manual 75 pasangan** untuk mengukur P/R | Tanpa ini tidak ada metrik — jangan dilewati |
| B | Selesaikan tooling, mulai bagian labelnya | 147 review B selesai |
| C | Bab 2 laporan + grafik eksplorasi (distribusi rating, sebaran review per tempat) | 3 grafik jadi di `figures/` |
| **Bertiga** | Lanjut labeli bagian masing-masing | ≥ 250 dari 500 selesai |

**Output H2:** `places_unified.csv` + P/R/F1 entity resolution.

---

### H3 — Selasa, 28 Juli · *🔴 Pelabelan tuntas + baseline*

| Siapa | Tugas | Selesai bila |
|---|---|---|
| **Bertiga** | **Selesaikan 500 label** — prioritas nomor satu hari ini | `outputs/labels.csv` lengkap |
| B | `4_absa_train.py` baseline: TF-IDF + LogReg, split 70/15/15 stratified | macro-F1 baseline tercatat |
| A | Mulai `6_geo_gap.py`: haversine tiap destinasi → fasilitas terdekat | Matriks jarak jadi |
| C | Bab 3 (Desain & Indikator Keberhasilan) | Draf jadi |

**Gerbang keputusan malam H3:** kalau label < 400, potong ke 6 aspek (buang `rumah_ibadah`, `jam_operasional`, `keamanan_sikap`, `sinyal`) dan lanjut. **Jangan mundurkan jadwal.**

---

### H4 — Rabu, 29 Juli · *🔴 Model utama*

| Siapa | Tugas | Selesai bila |
|---|---|---|
| B | Fine-tune IndoBERT (`indobenchmark/indobert-base-p1`), 3–5 epoch, early stopping | macro-F1 per aspek + confusion matrix |
| B | Jalankan model ke **seluruh 12.280 review** | `outputs/absa_predictions.csv` |
| B | (bila sempat) LLM few-shot sebagai pembanding ketiga | Tabel 3 model |
| A | Integrasi `transportasi.csv` (Tier 1): variabel `public_transport_access` | Kolom masuk ke tabel geo |
| C | Bab 5 (Modelling): tulis arsitektur & alasan pemilihan metode | Draf jadi |

**Output H4 — tabel yang WAJIB ada malam ini:**

| Model | macro-F1 | F1 per aspek | Latency | Catatan |
|---|---|---|---|---|
| TF-IDF + LogReg | ? | ? | ms | baseline |
| IndoBERT | ? | ? | ms | produksi |
| LLM few-shot | ? | ? | s | pembanding |

> Isi tanda tanya dengan hasil nyata. **Jangan pernah menulis angka perkiraan di laporan** — angka 0,60/0,78/0,80 yang saya sebut sebelumnya adalah tebakan, bukan hasil.

---

### H5 — Kamis, 30 Juli · *Indeks + validasi silang*

| Siapa | Tugas | Selesai bila |
|---|---|---|
| B | `5_friction_index.py`: mention_rate × Wilson LB × severity | `outputs/friction_index.csv` |
| B | **Bias audit**: tabel ranking sebelum vs sesudah Wilson LB | 1 grafik + 1 tabel |
| A | Regresi gap infrastruktur → complaint rate | R² / AUC + confidence interval |
| A | Integrasi `kuliner.csv` sebagai leksikon babi → jelaskan 298 keluhan halal | Analisis 1 paragraf + grafik |
| C | Bab 6 (Evaluasi Model) | Semua angka masuk |

**Ini hari paling bernilai untuk nilai juri.** Bias audit dan validasi silang adalah dua hal yang hampir pasti tidak dilakukan tim lain.

---

### H6 — Jumat, 31 Juli · *🔴 Freeze analisis*

| Siapa | Tugas | Selesai bila |
|---|---|---|
| B | `umkm_opportunities.csv` | Minimal 15 peluang konkret berlokasi |
| A | Tier 2 bila sempat: `addons` dari `tempat-wisata-v1` sebagai variabel aktivitas | Opsional — **buang bila mepet** |
| C | **Semua grafik final** untuk laporan & slide | `figures/` lengkap, resolusi cetak |
| C | Mockup 4 layar aplikasi (Figma / bahkan gambar tangan rapi) | 4 gambar |
| Bertiga | Rapikan `demo.ipynb` supaya bisa dijalankan dari atas ke bawah tanpa error | Restart & Run All berhasil |

**Pukul 22.00 H6: FREEZE.** Tidak ada model baru, tidak ada angka baru. Sisa dua hari murni untuk komunikasi.

---

### H7 — Sabtu, 1 Agustus · *Video + laporan*

| Siapa | Tugas |
|---|---|
| C | Rekam video (skrip di §7). Rekam 2–3 take, pilih terbaik |
| A+B | Selesaikan laporan bab 4, 7, 8 |
| A | `model_card.md`, `README.md` final, bersihkan repo |
| Bertiga | Baca ulang laporan bergiliran, cek §17 terpenuhi semua |

**Cek wajib video:** tanpa wajah, tanpa nama institusi, tanpa logo kampus, durasi 5–10 menit, link Google Drive/YouTube **publik** (uji buka di mode incognito).

---

### H8 — Minggu, 2 Agustus · *Submit 18:00*

| Jam | Kegiatan |
|---|---|
| 09.00–12.00 | Buffer perbaikan. Cek ulang semua nama file |
| 12.00–15.00 | Uji akhir: clone repo bersih → jalankan → berhasil? |
| 15.00–17.00 | Ekspor PDF (< 25 MB), zip source code, uji link publik |
| **18.00** | **SUBMIT** |
| 18.00–20.00 | Cadangan bila platform bermasalah |

> Jangan submit pukul 19.50. Server lomba selalu tersendat di jam terakhir.

---

## 6. Struktur LaporanAnalisis.pdf (8 Bab Wajib)

Nama file: `[Nama Tim] - LaporanAnalisis.pdf` · maks 25 MB · **tanpa nama institusi**

| Bab (§17) | Isi | Hal |
|---|---|---|
| **a. Latar Belakang** | 751.225 wisatawan, 1,31 hari, Simalungun 2,6 juta. Toba sebagai koridor transit | 1–2 |
| **b. Analisis Permasalahan** | Profiling dataset: 72% bintang 5 → rating sinyal mati. Tabel 11 kategori keluhan. Bias popularitas | 2–3 |
| **c. Desain & Indikator Keberhasilan** | Arsitektur 3 output. Indikator: macro-F1 ≥ X, P/R entity resolution, R² gap model | 2 |
| **d. Perencanaan Implementasi** | Pilot Balige 3 bulan, kebutuhan sumber daya, integrasi Dinas Pariwisata/BPODT, rencana aplikasi final | 2 |
| **e. Modelling** | Pipeline 6 tahap, alasan IndoBERT, rumus Friction Index + Wilson LB | 3–4 |
| **f. Evaluasi Model** | Tabel 3 model, F1 per aspek, confusion matrix, κ, P/R, R², **bias audit** | 3–4 |
| **g. Hasil & Pembahasan** | 10 destinasi friksi tertinggi, peluang UMKM, temuan halal–kuliner babi, keterbatasan | 4–5 |
| **h. Deklarasi Penggunaan AI** | Jujur: AI dipakai untuk apa (bantuan kode, draf teks), tidak dipakai untuk apa | 0,5 |

Lampiran: ringkasan penggunaan data 15 file (§11 dokumen detail), model card, link repo.

---

## 7. Skrip Video Demo

Durasi 5–10 menit. Rekam layar + narasi suara. **Tanpa wajah, tanpa identitas institusi.**

| Waktu | Yang ditampilkan | Yang dikatakan |
|---|---|---|
| 0:00–1:00 | Slide angka: 751.225 / 1,31 hari / 2,6 juta | "Toba bukan kekurangan wisatawan. Toba kehilangan mereka dalam 1,31 hari." |
| 1:00–2:00 | Terminal: jalankan `2_entity_resolve.py` | Tunjukkan `Pondok Siliwangi 27–31` menyatu. Sebut P/R/F1 |
| 2:00–4:00 | Notebook: 3 review Sipinsur → output JSON | "Model menangkap 'minta bayar lagi' sebagai pungli tanpa kata pungli" |
| 4:00–5:30 | Tabel perbandingan 3 model + confusion matrix | "Baseline keyword 0,XX. IndoBERT 0,YY. Selisih ini buktinya bukan grep" |
| 5:30–7:00 | Tabel Friction Index + grafik sebelum/sesudah Wilson LB | "Tanpa koreksi, tempat 5 review terlihat lebih buruk dari tempat 800 review" |
| 7:00–8:00 | Scatter plot gap → complaint rate, R² | "Asosiasi, bukan kausalitas. Uji kausal butuh pilot A/B" |
| 8:00–9:00 | Output UMKM + mockup peta | Contoh warung halal Bukit Holbung |
| 9:00–10:00 | Slide keterbatasan & etika | Bias platform, privasi, rencana final |

**Tips teknis:** rekam dengan OBS, resolusi 1080p, zoom terminal agar teks terbaca. Narasi direkam terpisah lalu digabung — jauh lebih rapi daripada bicara sambil mengetik.

---

## 8. Checklist Submission

```
[ ] [Nama Tim] - LaporanAnalisis.pdf     (< 25 MB, 8 bab lengkap)
[ ] [Nama Tim] - Demo                    (link Google Drive/YouTube PUBLIK)
[ ] Product                              (source code .ZIP)
[ ] Slide pitching
[ ] Repo: README, requirements.txt, model_card.md, LICENSE
[ ] outputs/friction_index.csv           (deliverable utama)
[ ] outputs/umkm_opportunities.csv
[ ] outputs/eval_report.md

VERIFIKASI ANTI-DISKUALIFIKASI:
[ ] TIDAK ada nama institusi di file mana pun (cek juga metadata PDF & nama file!)
[ ] TIDAK ada wajah di video
[ ] TIDAK ada logo kampus di slide
[ ] Nama reviewer sudah di-hash, tidak muncul di output mana pun
[ ] Link diuji di browser incognito
[ ] Semua sumber data eksternal dicantumkan (§12.2)
```

> Cek metadata PDF: `exiftool laporan.pdf | grep -i author`. Nama kampus sering menyelinap lewat template Word atau akun Google Docs.

---

## 9. Mode Kegagalan & Rencana Cadangan

| Risiko | Gejala | Rencana cadangan |
|---|---|---|
| Pelabelan telat | H3 malam < 400 label | Potong dari 10 → 6 aspek. Jangan geser jadwal |
| IndoBERT tidak konvergen | F1 < baseline | Pakai baseline TF-IDF sebagai model utama, laporkan jujur. Baseline yang jujur > model besar yang gagal |
| Tidak ada GPU | Training terlalu lambat | Google Colab gratis, atau DistilBERT multilingual |
| R² gap model jelek | Tidak ada korelasi | **Laporkan sebagai hasil negatif.** Itu tetap temuan ilmiah, dan kejujuran dinilai |
| κ rendah terus | < 0,5 setelah 2 iterasi | Kurangi jadi 5 aspek yang paling jelas batasannya |
| Waktu habis | H6 masih berantakan | Buang Tier 2, buang LLM few-shot, buang tren 3 tahun. **Jangan buang: bias audit & evaluasi** |

---
---

# BAGIAN B — MASA TUNGGU

## 10. Yang Dikerjakan Selama Menunggu

Pengumuman finalis **12–14 Agustus**. Ada ±10 hari kosong. Ini keunggulan besar bila dipakai, dan sebagian besar tim akan menyia-nyiakannya.

### 3–11 Agustus — bangun kerangka aplikasi

Guidebook §18 menyatakan final adalah *"pengembangan aplikasi/produk AI **berdasarkan model dari tahap preliminary**"*. Membangun kerangka aplikasi lebih awal adalah persis yang diminta, bukan kecurangan.

| Kegiatan | Hasil |
|---|---|
| Kerangka FastAPI + React kosong yang jalan | Repo `martahuta-app` |
| Peta MapLibre dengan 330 titik dummy | Layar 1 berfungsi |
| Dockerfile + docker-compose | Siap dideploy |
| **Unduh offline map tiles** untuk bbox Toba | Cadangan bila internet DGX bermasalah |
| Latihan presentasi 10 menit, direkam, ditonton ulang | 3× iterasi |
| Siapkan 20 pertanyaan juri + jawaban | `docs/qna.md` |

### 18 Agustus — Technical Meeting

**Pertanyaan yang wajib diajukan ke panitia:**
1. Apakah boleh membawa kode yang ditulis sebelum lockdown? Sejauh mana?
2. Spesifikasi akses DGX B200 — SSH? Docker? Port apa yang boleh dibuka?
3. Apakah ada internet saat lockdown? Boleh `pip install`?
4. Apakah boleh membawa model weights hasil preliminary?
5. Format presentasi — laptop sendiri atau panitia?

> Jawaban nomor 1 dan 5 menentukan seluruh strategi lockdown. Tanyakan, jangan berasumsi.

### 19–20 Agustus — logistik

Laptop, charger, kabel HDMI + adapter, mouse, colokan, model weights di flash disk, repo di-clone offline, semua dependency ter-cache (`pip download`), **pakaian formal/batik (§20)**.

---
---

# BAGIAN C — FINAL ROUND

## 11. Kalender Final

| Waktu | Kegiatan |
|---|---|
| **Jum, 21 Agu** | Daftar ulang → Opening Ceremony → Technical Meeting → **lockdown dimulai** |
| **Sab, 22 Agu 12:00** | **Lockdown berakhir — deploy di DGX wajib sudah jalan** |
| Sab, 22 Agu siang | Presentasi & demo (20 menit: 10 presentasi + 10 Q&A) |
| Sab, 22 Agu sore | Pengumuman pemenang |

**Waktu bangun efektif: ±20–24 jam, termasuk tidur.** Ini sangat sempit. Ponsel dikarantina, tidak boleh komunikasi keluar, aktivitas dimonitor real-time.

---

## 12. Persiapan Sebelum Berangkat

Bawa dalam keadaan **sudah jadi dan sudah diuji**:

```
✓ friction_index.csv, umkm_opportunities.csv, places_unified.csv   ← precomputed
✓ Model weights IndoBERT (hasil H4)                                 ← jangan latih ulang saat lockdown
✓ Kerangka FastAPI + React yang sudah jalan di laptop
✓ Dockerfile teruji
✓ Offline map tiles bbox Toba
✓ Semua pip package ter-cache offline
✓ Slide presentasi versi 1 (tinggal ganti screenshot)
✓ docs/qna.md
```

**Strategi inti:** lockdown dipakai untuk **merangkai dan memoles**, bukan membangun dari nol atau melatih model. Tim yang melatih model saat lockdown akan gagal deploy.

Deklarasikan terbuka apa yang dibawa saat technical meeting. Aktivitas dimonitor real-time — transparansi jauh lebih murah daripada tuduhan.

---

## 13. Rencana Lockdown Jam-Per-Jam

Asumsi lockdown mulai ±16.00 tanggal 21 Agustus.

| Jam | Target | Definition of done |
|---|---|---|
| 16.00–17.00 | Setup: akses DGX, clone repo, cek GPU, cek port | `nvidia-smi` jalan, port terbuka |
| 17.00–19.00 | **Deploy kerangka kosong ke DGX lebih dulu** | URL bisa dibuka dari browser 🔴 |
| 19.00–21.00 | Layar 1 (Peta) dengan data asli | 139 titik berwarna |
| 21.00–23.00 | Layar 2 (Rapor Destinasi) + bukti verbatim | Klik titik → detail muncul |
| 23.00–01.00 | Layar 4 (Live Analyzer) — inferensi model nyata | Tempel review → JSON keluar |
| 01.00–02.00 | Layar 3 (Peluang UMKM) | Tabel + peta |
| 02.00–05.00 | **TIDUR BERGILIRAN** — minimal 2 orang tidur 3 jam | Wajib. Presentasi butuh otak jernih |
| 05.00–07.00 | Simulasi Intervensi (fitur pamungkas) | Slider "perbaiki toilet" → indeks turun |
| 07.00–09.00 | Poles UI, responsif, dark mode, loading state | Enak dilihat di proyektor |
| 09.00–10.00 | **Uji demo lengkap 3× berturut-turut tanpa error** | 🔴 Gerbang mutlak |
| 10.00–11.30 | Latihan presentasi 3× dengan timer | Pas 10 menit |
| 11.30–12.00 | Freeze. Screenshot cadangan semua layar. Rekam video demo cadangan | Bila live gagal, video jalan |

> **Aturan 19.00:** kalau kerangka kosong belum tayang di DGX pada pukul 19.00, hentikan pengembangan fitur dan selesaikan deployment. Aplikasi cantik yang tidak ter-deploy bernilai nol (§19 mewajibkan deployment DGX).

> **Aturan tidur:** tim yang begadang penuh akan kalah di sesi Q&A 10 menit. Q&A bernilai setara dengan demo.

---

## 14. Deployment di DGX B200

DGX B200 adalah server GPU. Kemungkinan besar akses via SSH + container.

```bash
# 1. Cek lingkungan
nvidia-smi
docker ps

# 2. Bangun & jalankan
docker compose up -d --build

# 3. Verifikasi dari luar
curl http://<dgx-host>:8000/api/health
```

`docker-compose.yml` minimal:

```yaml
services:
  api:
    build: ./backend
    ports: ["8000:8000"]
    volumes: ["./outputs:/app/outputs:ro", "./models:/app/models:ro"]
    environment: [ "PRECOMPUTED=1" ]
  web:
    build: ./frontend
    ports: ["3000:80"]
    depends_on: [api]
```

**Rencana cadangan berlapis:**
1. Utama: aplikasi jalan di DGX, diakses dari browser laptop
2. Bila jaringan DGX bermasalah: jalankan lokal di laptop, **jelaskan terus terang** dan tunjukkan bukti sudah pernah jalan di DGX (screenshot + log)
3. Bila aplikasi rusak total: **video demo cadangan** yang direkam pukul 11.30
4. Bila proyektor bermasalah: slide PDF di flash disk

Siapkan keempatnya. Tidak butuh waktu lama, dan menyelamatkan lomba.

---

## 15. Skrip Presentasi 10 Menit + Q&A

### Presentasi (10 menit) — bagi bertiga, semua bicara

| Menit | Siapa | Isi |
|---|---|---|
| 0:00–1:30 | C | **Masalah.** 751.225 wisatawan, 1,31 hari. "Toba adalah koridor transit." Tunjukkan 3 kutipan review asli |
| 1:30–3:00 | A | **Data & pipeline.** 22.302 review, 72% bintang 5 → rating sinyal mati. Entity resolution, angka P/R |
| 3:00–5:00 | B | **Model.** ABSA, perbandingan 3 model, F1, Wilson LB, bias audit |
| 5:00–8:30 | C | **DEMO LIVE.** Peta → klik Sipinsur → rapor + bukti → Live Analyzer tempel review → Simulasi Intervensi |
| 8:30–10:00 | A | **Dampak & keberlanjutan.** Pilot Balige, integrasi BPODT, keterbatasan, etika |

**Demo harus tetap 3,5 menit.** Latih dengan timer. Kalau demo molor, bagian dampak terpotong, dan itu 20 poin.

### Q&A (10 menit) — semua anggota ikut menjawab

Sepuluh pertanyaan tersedia lengkap dengan jawabannya di [`IDE-1-MARTAHUTA-Detail.md`](./IDE-1-MARTAHUTA-Detail.md) §10. Tambahan khas final:

| Pertanyaan | Inti jawaban |
|---|---|
| "Bagaimana scalability ke seluruh Sumut?" | Pipeline agnostik lokasi; yang dibutuhkan hanya review + koordinat. Biaya inferensi ±X jam GPU per 100k review |
| "Keamanan sistem?" | Tidak ada data pribadi disimpan; nama reviewer di-hash saat ingest; API read-only |
| "Bagaimana menjaga data tetap segar?" | Rencana scraping berkala + endpoint ingest; Friction Index dihitung ulang bulanan |
| "Kenapa bukan chatbot saja?" | Chatbot melayani wisatawan yang sudah datang. Masalah Toba ada di sisi penawaran. Kami melayani pihak yang bisa memperbaiki |
| "Siapa yang membiayai setelah hackathon?" | Dinas Pariwisata sebagai pengguna utama; model B2G dengan biaya langganan dashboard |

**Aturan Q&A:** kalau tidak tahu, katakan *"kami belum menguji itu, tapi cara mengujinya adalah ..."*. Juri jauh lebih menghargai batas yang jujur daripada karangan. Satu jawaban mengarang bisa meruntuhkan kepercayaan pada seluruh angka Anda.

---
---

# BAGIAN D — APLIKASINYA

## 16. Arsitektur & Tech Stack

```
┌─────────────────────────────────────────────────────────┐
│  BROWSER                                                │
│  React + Vite + Tailwind + MapLibre GL                  │
│  4 layar: Peta · Rapor · UMKM · Live Analyzer           │
└───────────────────────┬─────────────────────────────────┘
                        │ REST JSON
┌───────────────────────▼─────────────────────────────────┐
│  BACKEND — FastAPI (Python)                             │
│  ├── /api/places        → baca friction_index.csv       │
│  ├── /api/places/{id}   → detail + evidence             │
│  ├── /api/opportunities → umkm_opportunities.csv        │
│  ├── /api/analyze       → INFERENSI LIVE IndoBERT       │
│  └── /api/simulate      → hitung ulang indeks           │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│  DATA (precomputed saat preliminary)                    │
│  friction_index.csv · umkm_opportunities.csv            │
│  places_unified.csv · absa_predictions.csv              │
│  models/indobert-absa/                                  │
└─────────────────────────────────────────────────────────┘
                   Semua di DGX B200
```

### Pilihan teknologi & alasannya

| Komponen | Pilihan | Alasan |
|---|---|---|
| Backend | **FastAPI** | Python — kode pipeline langsung dipakai ulang, tanpa port ulang |
| Frontend | **React + Vite + Tailwind** | Cepat dibangun, terlihat profesional di proyektor |
| Peta | **Leaflet + tile raster CARTO** | Open source, **tanpa API key**, tersedia basemap terang & gelap. Dipilih di atas MapLibre vektor karena vektor menuntut WebGL + style JSON + glyph + sprite; raster hanya PNG, jadi titik gagalnya lebih sedikit. Sediakan cadangan peta SVG luring yang aktif otomatis bila tile gagal |
| Data | **CSV / DuckDB** | 330 tempat & 22k review itu kecil. Postgres = kerumitan tanpa manfaat |
| Model | **IndoBERT via transformers** | Sudah dilatih di preliminary; hanya inferensi |
| Deploy | **Docker Compose** | Satu perintah, reprodusibel di DGX |

> **Jangan** pakai Streamlit untuk final. Cepat dibangun, tapi terlihat seperti prototipe internal, dan kriteria final menilai *user experience*.
> **Jangan** pakai Postgres/Kafka/microservice. Juri akan bertanya "kenapa?" dan tidak ada jawaban yang bagus untuk 330 baris data.

---

## 17. Empat Layar, Wireframe Lengkap

### Layar 1 — Peta Friksi (halaman utama)

```
┌────────────────────────────────────────────────────────────────┐
│ MARTAHUTA          [Peta] [UMKM] [Analyzer]         🔍 Cari    │
├──────────────┬─────────────────────────────────────────────────┤
│ FILTER       │                                                 │
│              │           ● Sipinsur (2,4)                      │
│ Kabupaten    │      ●               ● Holbung (2,1)            │
│ ☑ Toba       │            DANAU TOBA                           │
│ ☑ Samosir    │        ●        ○         ●                     │
│ ☑ Humbahas   │              ● Bul-bul (1,9)                    │
│              │         ○           ●                           │
│ Aspek        │                                                 │
│ ☑ Semua      │   ● merah   = friksi tinggi                     │
│ ☐ Pungli     │   ● kuning  = sedang                            │
│ ☐ Toilet     │   ● hijau   = rendah                            │
│ ☐ Kebersihan │   ○ abu-abu = data tidak cukup (37 tempat)      │
│ ☐ Halal      │                                                 │
│              ├─────────────────────────────────────────────────┤
│ ☐ Tampilkan  │ 10 FRIKSI TERTINGGI                             │
│   low-conf   │ 1. Geosite Sipinsur      2,4  pungli, toilet    │
│              │ 2. Bukit Holbung         2,1  sampah, kuliner   │
│ [Reset]      │ 3. Pantai Bul-bul        1,9  sikap, pungutan   │
└──────────────┴─────────────────────────────────────────────────┘
```

**Detail penting:** titik abu-abu (37 destinasi tanpa review) **harus ditampilkan**. Itu bukan kekosongan — itu rekomendasi: "prioritas survei lapangan". Juri akan menghargai tim yang menampilkan ketidaktahuannya secara eksplisit.

---

### Layar 2 — Rapor Destinasi

```
┌────────────────────────────────────────────────────────────────┐
│ ← Kembali                                                      │
│                                                                │
│ GEOSITE SIPINSUR                          Humbang Hasundutan   │
│ Friction Index 2,4  ·  peringkat 12/139  ·  412 review berteks │
│ ────────────────────────────────────────────────────────────── │
│                                                                │
│ PRIORITAS PERBAIKAN                                            │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ 1  HARGA / PUNGLI            59% negatif   dampak −1,8★    │ │
│ │    ████████████████████░░░░░░░░░░  88 dari 412 menyebut    │ │
│ │    💬 "Harga tiket naik 10x lipat, tidak ada perubahan"     │ │
│ │    💬 "Semua serba bayar, parkir 10K"                       │ │
│ │    📈 Tren 3 tahun: NAIK ▲                                  │ │
│ ├────────────────────────────────────────────────────────────┤ │
│ │ 2  TOILET / SANITASI         51% negatif   dampak −1,4★    │ │
│ │    ██████████████░░░░░░░░░░░░░░░░  47 dari 412 menyebut    │ │
│ │    💬 "Toilet airnya mati / tidak hidup"                    │ │
│ │    📈 Tren: STABIL ─                                        │ │
│ ├────────────────────────────────────────────────────────────┤ │
│ │ 3  PARKIR                    34% negatif   dampak −0,7★    │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                │
│ GAP INFRASTRUKTUR          [Simulasi Intervensi ▸]             │
│ Toilet layak    3,1 km ⚠   Angkutan umum  terakhir 17.00 ⚠     │
│ Faskes          8,4 km ⚠   Warung halal   4,2 km ⚠             │
└────────────────────────────────────────────────────────────────┘
```

**Kutipan verbatim adalah jantung layar ini.** Inilah yang membuat pengelola percaya, dan jawaban langsung atas §12.3 (*"tim perlu menjelaskan dasar rekomendasi"*).

---

### Layar 3 — Peluang UMKM

```
┌────────────────────────────────────────────────────────────────┐
│ PELUANG USAHA  ·  urut: potensi ▾    Kabupaten: Semua ▾        │
├────────────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ 🍽  WARUNG NASI & LAUK HALAL                    potensi ●●●│ │
│ │    Lokasi   : sekitar Bukit Holbung, Samosir               │ │
│ │    Bukti    : 47 keluhan ketiadaan makanan halal           │ │
│ │    Pasar    : 1.363 review/tahun · budget 400–800rb/hari   │ │
│ │    Pesaing  : 0 warung halal dalam radius 3 km             │ │
│ │    Kenapa   : kuliner dominan kawasan berbasis babi        │ │
│ │               (saksang, BPK, B2) → 298 keluhan halal       │ │
│ │    💬 "warung muslim pun gk jualan makanan"                 │ │
│ └────────────────────────────────────────────────────────────┘ │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ 🚻  PENGELOLAAN TOILET BERBAYAR LAYAK          potensi ●●○ │ │
│ │    Lokasi : Geosite Sipinsur                               │ │
│ │    Bukti  : 31 keluhan toilet + 61 keluhan pungli          │ │
│ └────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

---

### Layar 4 — Live Analyzer *(layar pembuktian AI)*

```
┌────────────────────────────────────────────────────────────────┐
│ LIVE ANALYZER — uji model dengan review apa pun                │
├────────────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ Tempatnya bagus tapi kamar mandinya udah pakai air danau   │ │
│ │ minta bayar lagi, terus parkirnya 10 ribu padahal di luar  │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                            [ Analisis ]        │
│ ────────────────────────────────────────────────────────────── │
│ HASIL MODEL                              inferensi 47 ms       │
│                                                                │
│  harga_pungli    NEGATIF  ████████████ 0,91                    │
│     └ "minta bayar lagi", "parkirnya 10 ribu"                  │
│  toilet_sanitasi NEGATIF  █████████░░░ 0,74                    │
│     └ "kamar mandinya udah pakai air danau"                    │
│  pemandangan     POSITIF  ███████████░ 0,88                    │
│     └ "tempatnya bagus"                                        │
│                                                                │
│ ⓘ Perhatikan: tidak ada kata "pungli" di teks ini.             │
│   Baseline keyword gagal. IndoBERT berhasil.                   │
└────────────────────────────────────────────────────────────────┘
```

> **Layar ini yang membuat juri percaya AI-nya nyata.** Tanpa ini, semua angka Anda hanyalah tabel yang bisa saja dibuat manual. Siapkan 3 contoh review yang sudah diuji sebelumnya — dan satu contoh yang **model-nya salah**, untuk ditunjukkan secara jujur bila juri bertanya soal keterbatasan.

---

### Fitur pamungkas — Simulasi Intervensi

```
┌────────────────────────────────────────────────────────────────┐
│ SIMULASI INTERVENSI — Geosite Sipinsur                         │
│                                                                │
│ Bila keluhan berikut diselesaikan:                             │
│   ☑ Toilet diperbaiki           −0,42 indeks                   │
│   ☑ Tarif ditertibkan           −0,68 indeks                   │
│   ☐ Parkir dibenahi             −0,19 indeks                   │
│   ────────────────────────────────────────────                 │
│   Friction Index  2,40  →  1,30    peringkat 12 → 47           │
│                                                                │
│ ⚠ Proyeksi berbasis asosiasi historis, bukan jaminan kausal.   │
└────────────────────────────────────────────────────────────────┘
```

Fitur ini mengubah aplikasi dari *alat pelaporan* menjadi **alat pengambilan keputusan** — persis yang dinilai pada kriteria dampak. Peringatan kausalitas di bawahnya **jangan dihapus**; itu justru menunjukkan kedewasaan yang dicari juri.

---

## 18. Kontrak API

| Endpoint | Method | Respons |
|---|---|---|
| `/api/health` | GET | `{"status":"ok","model_loaded":true}` |
| `/api/places` | GET | daftar: `id, name, lat, lon, friction_index, rank, top_aspect, confidence` |
| `/api/places/{id}` | GET | detail + array aspek + evidence + tren + gap infrastruktur |
| `/api/opportunities` | GET | daftar peluang UMKM, terurut potensi |
| `/api/analyze` | POST | `{text}` → aspek + sentimen + skor + evidence + latency |
| `/api/simulate` | POST | `{place_id, fixes[]}` → indeks & peringkat baru |

Contoh `/api/places/WIS-042`:

```json
{
  "id": "WIS-042",
  "name": "Geosite Sipinsur",
  "kabupaten": "Humbang Hasundutan",
  "friction_index": 2.4,
  "rank": 12,
  "n_reviews_text": 412,
  "confidence": "high",
  "aspects": [
    {"aspect":"harga_pungli","n_mention":88,"neg_rate":0.59,
     "severity":-1.8,"rank":1,"trend":"naik",
     "evidence":["Harga tiket naik 10x lipat...","Semua serba bayar, parkir 10K"]}
  ],
  "infra_gap": {
    "toilet_km":3.1,"faskes_km":8.4,"halal_km":4.2,
    "public_transport_last_departure":"17:00"
  }
}
```

---

## 19. Aturan Emas: Precompute Semuanya

**Satu-satunya inferensi live adalah `/api/analyze` di Layar 4.** Semua yang lain dibaca dari CSV yang sudah dihitung sejak preliminary.

| Alasan | Penjelasan |
|---|---|
| Kecepatan demo | Peta muncul < 200 ms. Tidak ada spinner di depan juri |
| Keandalan | Bila GPU bermasalah, 3 dari 4 layar tetap jalan |
| Kejujuran | Angka yang didemokan **identik** dengan angka di laporan preliminary. Juri bisa memverifikasi silang — dan itu poin kredibilitas besar |
| Waktu lockdown | Tidak ada waktu melatih apa pun dalam 20 jam |

> Kegagalan paling umum di final hackathon: aplikasi yang melakukan inferensi saat halaman dibuka, lalu menggantung 30 detik di depan juri. Jangan.

---

## Ringkasan Satu Halaman

**Preliminary (7 hari):** bangun **mesin**, bukan aplikasi. Enam skrip Python → `friction_index.csv`. Bottleneck-nya pelabelan 500 review — mulai hari ini. Freeze H6, submit H8 pukul 18.00.

**Masa tunggu (10 hari):** bangun kerangka aplikasi, latihan presentasi, siapkan pertanyaan technical meeting.

**Final (20 jam):** rangkai, jangan bangun. Deploy kerangka kosong ke DGX sebelum pukul 19.00. Empat layar. Tidur bergiliran. Uji demo 3× sebelum tampil.

**Aplikasinya:** dashboard peta + rapor destinasi + peluang UMKM + live analyzer, dengan simulasi intervensi sebagai penutup. Semua precomputed kecuali satu layar yang membuktikan modelnya nyata.

---

> **MARTAHUTA** — *Marsipature Hutana Be*
> Del AI Hackathon 2026
