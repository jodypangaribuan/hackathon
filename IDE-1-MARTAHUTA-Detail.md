# MARTAHUTA — Spesifikasi Detail Ide #1

> *Marsipature Hutana Be* — "setiap orang membangun kampungnya sendiri."
> Dokumen ini menjelaskan **apa persisnya yang dibangun**, bukan hasil analisisnya.
> Pendamping dari [`IDEAS.md`](./IDEAS.md) · Deadline preliminary: **2 Agustus 2026, 20:00 WIB**

---

## Daftar Isi

1. [Dua hal berbeda yang dibangun](#1-dua-hal-berbeda-yang-dibangun)
2. [Produk dalam satu kalimat](#2-produk-dalam-satu-kalimat)
3. [Konkret: input → output](#3-konkret-input--output)
4. [Daftar aspek friksi](#4-daftar-aspek-friksi)
5. [Rumus Friction Index](#5-rumus-friction-index)
6. [Yang benar-benar ditulis: 6 file Python](#6-yang-benar-benar-ditulis-6-file-python)
7. [Skema output](#7-skema-output)
8. [Aplikasi (final round)](#8-aplikasi-final-round)
9. [Isi video demo preliminary](#9-isi-video-demo-preliminary)
10. [Pertanyaan juri yang harus bisa dijawab](#10-pertanyaan-juri-yang-harus-bisa-dijawab)
11. [Deklarasi pemakaian dataset (15 file)](#11-deklarasi-pemakaian-dataset-15-file)

---

## 1. Dua hal berbeda yang dibangun

Ini sumber kebingungan terbesar. Preliminary dan final menuntut artefak yang **berbeda jenis**.

| | Preliminary (2 Agustus) | Final (21–22 Agustus, onsite) |
|---|---|---|
| Yang dinilai | **Model + analisis** | **Aplikasi/produk** |
| Yang dibangun | Notebook + pipeline + angka evaluasi | Web app di atas model yang sama |
| Bukti | Video 5–10 menit **menjalankan notebook** | Demo produk live di DGX B200 |
| Web app? | **Tidak perlu sama sekali** | Wajib |

Guidebook §8A: video demo preliminary adalah *"video yang mendemonstrasikan eksekusi dan cara kerja model analisis (misalnya melalui notebook atau skrip), penjelasan performa/evaluasi model, dan nilai manfaatnya."*

> ✅ **Untuk 2 Agustus: yang dibangun adalah MESIN-nya, bukan aplikasinya.**
> Aplikasi baru dibangun saat lockdown 21–22 Agustus, di atas mesin yang sudah jadi.

Ini justru keunggulan strategis: tim lain akan menghabiskan minggu ini membuat UI chatbot yang tidak dinilai, sementara tim Anda membangun aset yang dinilai penuh di kriteria 3 (20 poin) *dan* langsung bisa dipakai lagi di final.

---

## 2. Produk dalam satu kalimat

> **Sebuah pipeline yang membaca 12.280 teks review dan mengubahnya menjadi satu tabel: "destinasi X punya masalah Y, sebanyak Z% pengunjung mengeluhkannya, dan itu menurunkan rating rata-rata sebesar N bintang."**

Itu inti seluruh solusi. Sisanya hanyalah cara menyajikan tabel tersebut.

**Mengapa tabel itu berharga:** hari ini pengelola destinasi hanya tahu rating mereka 4,5. Angka itu tidak memberi tahu apa pun tentang **apa yang harus diperbaiki lebih dulu**. Tabel ini memberitahunya, dengan bukti, terurut prioritas.

---

## 3. Konkret: input → output

### 3.1 Input — review asli dari dataset

Tiga review nyata di **Geosite Sipinsur** (827 review):

> ⭐3 — *"Harga tiket yg naik 10x lipat dari sblm ny, tdk ada perubahan ddlm lokasi wisata, dari pertama kali dtng sampe kemarin msh tetap sama dgn view hutan pinus tdk ada spot foto atau hal baru yg disuguhkan, perubahan cuma di harga tiket"*
>
> ⭐3 — *"Fasilitas nya kurang terjaga. Toilet Air nya mati / tidak hidup. Seharusnya dengan bayar Karcis 10 / orang sudah bisa di gunakan untuk fasilitas."*
>
> ⭐1 — *"Tidak recomended semua sea bayar , yang dluar nurul ya Parkir 10K"*

### 3.2 Output tahap 1 — per review

Model mengeluarkan JSON terstruktur:

```json
{
  "place": "Geosite Sipinsur",
  "review_id": 4471,
  "rating": 3,
  "date_est": "2025-04",
  "aspects": [
    {"aspect": "harga_pungli",     "sentiment": "negatif", "evidence": "harga tiket naik 10x lipat"},
    {"aspect": "fasilitas_value",  "sentiment": "negatif", "evidence": "tidak ada perubahan di lokasi"}
  ]
}
```

### 3.3 Output tahap 2 — agregasi per destinasi

Setelah 827 review Sipinsur diproses:

| Destinasi | Aspek | Disebut | Negatif | Rate (Wilson LB) | Dampak rating | Prioritas |
|---|---|---:|---:|---:|---:|---:|
| Geosite Sipinsur | harga_pungli | 88 | 61 | 59% | −1,8★ | **1** |
| Geosite Sipinsur | toilet_sanitasi | 47 | 31 | 51% | −1,4★ | 2 |
| Geosite Sipinsur | parkir | 39 | 18 | 34% | −0,7★ | 3 |
| Geosite Sipinsur | kebersihan | 55 | 12 | 14% | −0,3★ | 7 |

*(angka ilustratif — akan diisi hasil model sebenarnya)*

### 3.4 Bukti bahwa ini bukan template seragam

**Bukit Holbung Samosir** (1.363 review) menghasilkan profil yang sama sekali berbeda:

> ⭐1 — *"Tidak ada yang jual warung makanan nasi dan lauk, semua jualan cm kopi2 dan gorengan aja, warung muslim pun gk jualan makanan, untuk yg mau kesini bawa makanan dari homestay atau rumah"*
>
> ⭐3 — *"Banyak sampah plastik, tempat camping tidak diatur dengan baik. Mungkin pengelola perlu meniru Bukit Campuhan di Ubud Bali yang relatif bersih dari sampah"*
>
> ⭐3 — *"Indah bangett lah pokoknya bukit hollbung minus nya banyak kotora kerbau"*

**Pantai Pasir Putih Lumban Bul-bul** (232 review) berbeda lagi:

> ⭐1 — *"Gak rekom, karena main pasir d larang, melarang anaku"*
>
> ⭐3 — *"Pantainya si bagus ya tapi kamar mandinya, udah pake air danau toba minta bayar lagi"*
>
> ⭐1 — *"Tidak layak untuk di kunjungi. Klo muslim yg dtg mereka tidak suka."*

| Destinasi | Masalah dominan | Peluang UMKM yang muncul |
|---|---|---|
| Geosite Sipinsur | Pungli + toilet mati | Pengelolaan toilet berbayar yang layak |
| Bukit Holbung | Sampah + tiada warung makan (khususnya halal) | **Warung nasi/lauk halal** |
| Pantai Bul-bul | Sikap warga ke anak + pungutan kamar mandi | Pelatihan hospitality + kamar mandi terkelola |

Tiga destinasi, tiga daftar perbaikan berbeda, tiga peluang usaha berbeda. **Inilah yang tidak bisa dilihat siapa pun hari ini** — dan tidak bisa dihasilkan oleh chatbot.

---

## 4. Daftar Aspek Friksi

Sepuluh aspek final, dipilih karena volumenya sudah diverifikasi ada di korpus (lihat `IDEAS.md` §2):

| # | Aspek | Kata kunci awal (untuk seed labeling) | Volume terverifikasi |
|---|---|---|---:|
| 1 | `kebersihan` | sampah, kotor, jorok, bau, bersih | 1.244 |
| 2 | `parkir` | parkir, karcis parkir | 457 |
| 3 | `toilet_sanitasi` | toilet, wc, kamar mandi, sanitasi | 400 |
| 4 | `harga_pungli` | pungli, pungutan, mahal, dipalak, retribusi, karcis | 342 |
| 5 | `akses_jalan` | jalan rusak, akses, berlubang | 334 |
| 6 | `ramah_keluarga` | anak, balita, lansia, difabel, kursi roda | 303 |
| 7 | `halal_muslim` | halal, babi, muslim | 298 |
| 8 | `rumah_ibadah` | mushola, masjid, sholat, gereja | 82 |
| 9 | `jam_operasional` | tutup, buka jam, sudah tutup | 56 |
| 10 | `keamanan_sikap` | preman, tidak aman, hilang, dimarahi | 47 |

Tambahan opsional bila waktu cukup: `fasilitas_value` (bayar tapi tidak ada fasilitas), `kuliner_tersedia` (ada/tidak warung makan).

> ⚠️ Kata kunci ini **hanya untuk memilih review yang akan dilabeli manual (seed)**, agar pelabelan tidak membuang waktu pada review kosong. Model akhir dilatih pada teks, bukan pada kata kunci — kalau tidak, ini bukan AI, hanya `grep`. Juri akan menanyakan ini.

---

## 5. Rumus Friction Index

Untuk destinasi $p$ dan aspek $a$:

```
mention_rate(p,a) = jumlah review menyebut a  /  total review berteks di p

neg_rate(p,a)     = Wilson lower bound 95% dari (negatif_a / disebut_a)

severity(a)       = mean(rating | a negatif)  −  mean(rating global)
                    ← dipelajari dari data, bukan ditebak

FrictionIndex(p)  = Σ_a  mention_rate(p,a) × neg_rate(p,a) × |severity(a)|
```

### 5.1 Kenapa Wilson lower bound — dan kenapa ini menyelamatkan nilai Anda

Fakta dari data: **Bukit Holbung punya 1.363 review, tetapi hanya 13 review negatif berteks** (~2%). Kelas negatif sangat langka di seluruh korpus (rating 72% bintang 5).

Tanpa koreksi interval kepercayaan, destinasi dengan 5 review bisa tampak "lebih bermasalah" daripada destinasi dengan 800 review — murni karena kebetulan statistik. Wilson LB menghukum sampel kecil secara otomatis.

Efek sampingnya sangat menguntungkan: ini **menjawab kritik bias popularitas di guidebook §12.3 dengan matematika**, bukan dengan paragraf permintaan maaf. Tunjukkan tabel ranking sebelum vs sesudah Wilson LB di video — itu satu slide yang langsung membedakan tim Anda.

### 5.2 Konsekuensi desain penting

**Ekstraksi aspek dijalankan pada SEMUA review, bukan hanya yang bernada negatif.**

*"Toiletnya bersih dan terawat"* adalah sinyal fasilitas **positif** yang sama berharganya — ia menjadi penyebut dalam `neg_rate`. Tanpa review positif, tidak ada pembanding, dan `neg_rate` selalu 100%.

### 5.3 Penanganan kepercayaan rendah

Destinasi dengan < 20 review berteks ditandai `confidence: low` dan **tidak dimasukkan ke ranking publik**. Dari 139 destinasi, sekitar 37 punya nol review — mereka masuk kategori terpisah: *"data tidak cukup — prioritas survei lapangan"*, yang justru merupakan rekomendasi berguna bagi Dinas Pariwisata.

---

## 6. Yang benar-benar ditulis: 6 file Python

```
martahuta/
├── data/
│   └── raw/                      # 15 CSV dari panitia, tidak diubah
├── src/
│   ├── 1_parse_dates.py          # "a year ago" + "2 tahun lalu di" + scraped-at → tanggal absolut
│   ├── 2_entity_resolve.py       # 75 tempat tak-match → satu tabel tempat + lat-long
│   ├── 3_absa_label.py           # antarmuka pelabelan 500 review (aspek + sentimen)
│   ├── 4_absa_train.py           # TF-IDF baseline → IndoBERT → bandingkan macro-F1
│   ├── 5_friction_index.py       # rumus §5 → tabel akhir per destinasi
│   └── 6_geo_gap.py              # 323 titik + fasilitas → gap score → regresi validasi
├── notebooks/
│   └── demo.ipynb                # yang direkam untuk video 5–10 menit
├── outputs/
│   ├── places_unified.csv
│   ├── friction_index.csv        # ← DELIVERABLE UTAMA
│   ├── umkm_opportunities.csv
│   ├── eval_report.md
│   └── model_card.md
└── README.md
```

### Tugas tiap file

| File | Input | Output | Metrik yang dilaporkan |
|---|---|---|---|
| `1_parse_dates.py` | `published-at`, `scraped-at-date` | kolom `date_est` (YYYY-MM) | % berhasil di-parse, distribusi per tahun |
| `2_entity_resolve.py` | 5 file metadata + 2 file review | `places_unified.csv` (±330 baris) | **Precision / Recall / F1** pada 75 tempat tak-match |
| `3_absa_label.py` | review terpilih (stratified) | `labels.csv` (500–600 baris) | **Inter-annotator agreement (Cohen's κ)** |
| `4_absa_train.py` | `labels.csv` | model + prediksi 12.280 review | **macro-F1 per aspek**, confusion matrix, tabel 3 model |
| `5_friction_index.py` | prediksi ABSA | `friction_index.csv` | ranking sebelum/sesudah Wilson LB |
| `6_geo_gap.py` | `places_unified.csv` + fasilitas | gap score per destinasi | **R² / AUC** regresi gap → complaint rate |

### Catatan implementasi per file

**`1_parse_dates.py`** — perhatikan format campur: `"a year ago"` (Inggris), `"2 tahun lalu di"` (Indonesia, dengan `di` menggantung), `"Edited 3 months ago"`, dan 279 nilai kosong. Tanggal acuan = `scraped-at-date` (2025-07-28/29). Hasilnya perkiraan bulanan, bukan harian — nyatakan itu di laporan.

**`2_entity_resolve.py`** — strategi bertingkat: (1) exact match setelah normalisasi, (2) fuzzy match nama (rapidfuzz, ambang ~85), (3) blocking berdasarkan jarak lat-long < 200 m, (4) embedding nama untuk sisa kasus. Tangani duplikat literal `Pondok Siliwangi 27/28/29/30/31`. **Buat ground truth manual 75 pasangan** untuk mengukur P/R — tanpa ini tidak ada metrik.

**`3_absa_label.py`** — sampling **stratified**: jangan hanya melabeli review negatif. Ambil proporsional per aspek per rating, agar model melihat contoh positif juga. 3 anggota tim melabeli 60 review yang sama untuk mengukur κ, sisanya dibagi.

**`4_absa_train.py`** — wajib menampilkan **tiga** pendekatan berdampingan. Baseline sederhana yang dilaporkan jujur jauh lebih meyakinkan juri daripada satu model besar tanpa pembanding.

| Model | Perkiraan macro-F1 | Latency | Catatan |
|---|---|---|---|
| TF-IDF + LogReg | ~0,60 | ms | baseline wajib |
| IndoBERT fine-tune | ~0,78 | ~50 ms | kandidat produksi |
| LLM few-shot | ~0,80 | ~2 s | mahal, untuk pembanding |

**`5_friction_index.py`** — implementasi rumus §5, plus penandaan `confidence`.

**`6_geo_gap.py`** — hitung jarak haversine dari tiap destinasi ke fasilitas terdekat (toilet, rumah ibadah, faskes, ATM, SPBU, warung makan, penginapan) dari `waktu operasional destinasi.csv` + 323 titik berkoordinat. Lalu **regresi: apakah gap memprediksi complaint rate?** Ini validasi silang antar-sumber yang hampir pasti tidak dilakukan tim lain.

---

## 7. Skema Output

### `friction_index.csv` — deliverable utama

| Kolom | Tipe | Contoh |
|---|---|---|
| `place_id` | str | `WIS-042` |
| `place_name` | str | `Geosite Sipinsur` |
| `kabupaten` | str | `Humbang Hasundutan` |
| `lat`, `lon` | float | `2.2891`, `98.9412` |
| `n_reviews_text` | int | `412` |
| `aspect` | str | `harga_pungli` |
| `n_mention` | int | `88` |
| `n_negative` | int | `61` |
| `neg_rate_wilson` | float | `0.59` |
| `severity` | float | `-1.8` |
| `priority_rank` | int | `1` |
| `friction_contrib` | float | `0.42` |
| `confidence` | str | `high` / `low` |
| `top_evidence` | str | *"harga tiket naik 10x lipat..."* |
| `trend_3y` | str | `naik` / `turun` / `stabil` |

### `umkm_opportunities.csv`

| Kolom | Contoh |
|---|---|
| `place_name` | `Bukit Holbung Samosir` |
| `opportunity` | `Warung nasi & lauk halal` |
| `evidence_count` | `47` |
| `visitor_proxy` | `1363 review/tahun` |
| `nearest_existing_km` | `3.2` |
| `budget_band` | `Rp 400.000 – 800.000/hari` |
| `kabupaten` | `Samosir` |

Contoh baris yang dihasilkan, ditulis sebagai kalimat:

> *"Warung halal di sekitar Bukit Holbung: 1.363 review/tahun, 47 keluhan ketiadaan makanan halal, nol restoran halal dalam radius 3 km, budget harian wisnus Rp 400–800 ribu."*

---

## 8. Aplikasi (final round)

Tiga layar, **semuanya hanya membaca `friction_index.csv`** yang sudah jadi sejak preliminary.

### Layar 1 — Peta
139 destinasi sebagai titik di peta Toba, diwarnai merah→hijau menurut Friction Index. Filter: kabupaten, jenis wisata, aspek tertentu. Toggle "tampilkan destinasi tanpa data" (37 titik abu-abu = prioritas survei).

### Layar 2 — Rapor Destinasi
Klik satu titik. Judul: **"Geosite Sipinsur — Friction Index 2,4 (peringkat 12 dari 139)"**

- Tabel prioritas perbaikan (§3.3)
- Di bawah tiap baris: **kutipan verbatim review sebagai bukti** ← lapisan explainability; ini alasan pengelola akan percaya, dan jawaban atas §12.3 tentang "dasar rekomendasi"
- Grafik tren 3 tahun: keluhan pungli naik atau turun?
- Perbandingan dengan destinasi sejenis

### Layar 3 — Peluang UMKM
Daftar peluang usaha terurut potensi, dengan lokasi di peta dan bukti pendukungnya.

### Posisi AI generatif
Chat AI hanyalah **lapisan tipis di atas ketiga layar** untuk merangkum dalam bahasa alami — bukan produknya. Bila juri bertanya *"mana AI-nya?"*, jawabannya: **ABSA + gap model**, bukan chatbot. Ini pembedaan yang harus dilatih agar seluruh anggota tim menjawabnya sama.

---

## 9. Isi Video Demo Preliminary

Durasi 5–10 menit. **Tanpa wajah, tanpa nama institusi** (§17).

| Waktu | Isi |
|---|---|
| 0:00–1:00 | **Masalah.** 751.225 wisatawan, tinggal 1,31 hari. Simalungun 2,6 juta. Toba adalah koridor transit, bukan destinasi. |
| 1:00–2:30 | Jalankan `2_entity_resolve.py` live → tunjukkan `Pondok Siliwangi 27/28/29/30/31` menyatu jadi satu entitas. Tampilkan P/R/F1. |
| 2:30–5:00 | Jalankan ABSA pada tiga review Sipinsur → tampilkan JSON keluar. Lalu tabel: TF-IDF 0,61 → IndoBERT 0,79. Tunjukkan confusion matrix. |
| 5:00–7:00 | Bangun Friction Index → 10 destinasi bermasalah teratas. **Tunjukkan ranking sebelum vs sesudah Wilson LB** (slide bias audit). |
| 7:00–8:30 | Regresi gap infrastruktur → complaint rate. Laporkan R² + interval kepercayaan. Nyatakan eksplisit: asosiasi, bukan kausalitas. |
| 8:30–10:00 | Contoh output UMKM. Mockup peta. Rencana final round. Keterbatasan & etika. |

---

## 10. Pertanyaan Juri yang Harus Bisa Dijawab

Latih jawaban ini sebelum presentasi — kriteria 6 (10 poin) menilai *"kemampuan tim menjawab pertanyaan juri secara terstruktur"*.

**"Ini kan cuma keyword matching?"**
> Tidak. Kata kunci hanya dipakai untuk memilih review yang dilabeli manual. Model akhir adalah IndoBERT yang dilatih pada 500 review berlabel dan berjalan pada teks penuh — ia menangkap *"udah pake air danau toba minta bayar lagi"* sebagai pungli meski tidak ada kata "pungli" di dalamnya. Baseline keyword kami F1-nya 0,61; model akhir 0,79. Selisih itu justru buktinya.

**"Kenapa tidak pakai rating saja?"**
> Karena 72% review bintang 5 dan semua destinasi ada di rentang 4,2–4,8. Rating tidak membedakan apa pun, dan tidak memberi tahu *apa* yang salah.

**"Bagaimana dengan destinasi yang reviewnya sedikit?"**
> Wilson lower bound 95%, dan destinasi < 20 review berteks ditandai low-confidence serta dikeluarkan dari ranking publik. 37 destinasi tanpa review kami laporkan sebagai prioritas survei lapangan.

**"Apakah keluhan menyebabkan kunjungan singkat?"**
> Kami tidak mengklaim kausalitas. Yang kami tunjukkan adalah asosiasi statistik antara gap infrastruktur dan tingkat keluhan (R² = ...). Uji kausal memerlukan pilot A/B di satu kecamatan, yang kami usulkan sebagai tahap berikutnya.

**"Siapa yang akan memakai ini?"**
> Dinas Pariwisata Toba dan BPODT untuk prioritas anggaran; pengelola destinasi untuk perbaikan operasional; UMKM untuk keputusan buka usaha. Pilot yang kami usulkan: satu kecamatan (Balige), 3 bulan.

**"Bagaimana privasi reviewer?"**
> Kolom `name` berisi nama asli reviewer — kami hash pada tahap ingest dan tidak pernah menampilkannya. Kutipan verbatim ditampilkan tanpa atribusi identitas.

---

## 11. Deklarasi Pemakaian Dataset (15 file)

Wajib masuk laporan sebagai "Ringkasan Penggunaan Data" (§8A). Guidebook §6.3 **tidak mewajibkan memakai semua file** — yang dituntut adalah pemakaian *bermakna* dan *bisa dijelaskan*. Pemakaian dekoratif lebih berbahaya daripada pengecualian yang jujur.

### Tier 0 — Inti (7 file)

| File | Baris | Peran |
|---|---:|---|
| `wisata-v2` | 12.691 | Korpus utama ABSA |
| `resto-hotel-v2` | 9.611 | Korpus utama ABSA |
| `wisata-metadata` | 139 | Koordinat + entity resolution |
| `resto-metadata` | 148 | Koordinat + entity resolution |
| `hotel-metadata` | 36 | Koordinat + entity resolution |
| `waktu operasional destinasi` | 236 | Inventaris fasilitas → geo gap model |
| `Info Seputar TOP 3` | 30 | Volume kunjungan, budget, durasi 1,31 hari |

### Tier 1 — Tambahan bernilai tinggi, biaya rendah (2 file)

**`transportasi.csv` (16 moda)** — menyambung langsung ke tesis lama tinggal. Trayek + **jam operasional** tiap moda; 169 review menyebut transportasi. Hipotesis yang diuji: bila angkutan terakhir dari suatu kawasan berangkat sore, wisatawan **secara struktural tidak bisa menginap** — 1,31 hari sebagian adalah artefak jadwal transportasi, bukan preferensi. Masuk sebagai variabel `public_transport_access` di `6_geo_gap.py`.

**`kuliner.csv` (20 masakan)** — **jangan** dipakai sebagai penghitung permintaan: hanya 45 penyebutan nama masakan di 12.280 review (Saksang 25, Mie Gomak 18, Mie Sop 2) — terlalu lemah.
Pakai sebagai **ontologi/leksikon bahan**. File inilah yang menyatakan saksang, Babi Panggang Karo, dan B2 berbahan babi. Penyebutan di review: `babi` 129×, `babi panggang` 60×, `bpk` 39×, `b2` 21×.
→ Ini **menjelaskan secara struktural** asal 298 keluhan halal, bukan sekadar menghitungnya: kuliner unggulan kawasan ini memang berbasis babi. Menghasilkan rekomendasi UMKM yang spesifik dan berbasis sebab, bukan korelasi.

### Tier 2 — Kerjakan bila waktu cukup (2 file)

**`tempat-wisata-v1.csv` (177)** — kolom `addons` adalah inventaris aktivitas (*"Berenang, Sunset, Sunrise, Banana Boat, Kano, Spot Foto"*). **Jumlah aktivitas per destinasi adalah variabel penjelas lama tinggal yang paling langsung**: destinasi yang hanya bisa difoto tidak menahan orang. Tambahan: selisih `entry-fee` v1 vs v2 menjadi bukti kuantitatif ketidakkonsistenan data.

**`Artikel Danau Toba.csv` (48)** — analisis **"promise vs reality gap"**: bandingkan topik yang dijanjikan 48 artikel promosi dengan topik yang dialami di 12.280 review. Selisihnya adalah temuan tersendiri bagi Dinas Pariwisata.

### Tier 3 — Pendukung, akui keterbatasannya (4 file)

| File | Peran jujur |
|---|---|
| `Attractions Info` (57) | Deskripsi kaya + latar sejarah/budaya → lapisan konten aplikasi final. **Hanya 8 atraksi punya harga tiket**, jadi terlalu tipis untuk cross-check harga — jangan diklaim lebih |
| `hotel-resto-v1` (9) | Terlalu kecil untuk analisis. Dipakai murni sebagai cross-check entity resolution |
| `prompt.csv` (14) | **Eval set**, bukan produk. 10 prompt untuk menguji apakah knowledge base menjawab pertanyaan nyata |
| *(Attractions Info dihitung di atas)* | |

### Ringkasan untuk laporan

> **11 file dengan peran analitis nyata, 3 file pendukung, dan pemakaian `prompt.csv` sebagai eval set.**
> Kami tidak mengklaim memakai seluruh file secara setara; setiap keputusan pakai/tidak-pakai dijelaskan beserta alasannya.

Kalimat itu lebih kuat di hadapan juri daripada klaim "kami memakai semua 15 file" yang runtuh pada pertanyaan pertama.

---

## Lampiran — Kaitan ke Dokumen Lain

- Fakta dataset & profiling lengkap → [`IDEAS.md`](./IDEAS.md) §1–2
- Perbandingan dengan 3 ide alternatif → [`IDEAS.md`](./IDEAS.md) §5–7
- Pemetaan rubrik 100 poin → [`IDEAS.md`](./IDEAS.md) §8
- Rencana 7 hari & checklist artefak → [`IDEAS.md`](./IDEAS.md) §9
- Risiko, bias, dan etika → [`IDEAS.md`](./IDEAS.md) §10

---

> **MARTAHUTA** — *Marsipature Hutana Be*
> Del AI Hackathon 2026
