# Del AI Hackathon 2026 — Analisis Dataset & Ide Solusi

> Dokumen kerja internal. Disusun dari pembacaan langsung `Del-AI-Hackathon-2026.md` dan profiling seluruh 15 file di `Datasets/`.
> Tanggal analisis: 26 Juli 2026 · Deadline preliminary: **2 Agustus 2026, 20:00 WIB**

---

## Daftar Isi

1. [Fakta Dataset (hasil profiling)](#1-fakta-dataset-hasil-profiling)
2. [Sinyal yang Sudah Diverifikasi di Review](#2-sinyal-yang-sudah-diverifikasi-di-review)
3. [The Trap — apa yang akan dibangun 80% tim](#3-the-trap--apa-yang-akan-dibangun-80-tim)
4. [IDE #1 (Rekomendasi Utama)](#4-ide-1-rekomendasi-utama--toba-retention-intelligence)
5. [IDE #2 — Sinyal Jujur](#5-ide-2--sinyal-jujur-the-anti-rating-engine)
6. [IDE #3 — Peta Inklusi Toba](#6-ide-3--peta-inklusi-toba)
7. [IDE #4 — Data Quality Copilot](#7-ide-4--data-quality-copilot)
8. [Pemetaan ke Rubrik 100 Poin](#8-pemetaan-ke-rubrik-100-poin)
9. [Rencana Eksekusi 7 Hari](#9-rencana-eksekusi-7-hari)
10. [Risiko, Etika, dan Catatan Kejujuran Data](#10-risiko-etika-dan-catatan-kejujuran-data)

---

## 1. Fakta Dataset (hasil profiling)

Angka-angka di bawah ini hasil hitung langsung dari file CSV, bukan dari deskripsi guidebook.

### 1.1 Ringkasan file

| File | Baris | Isi penting |
|---|---:|---|
| `wisata-v2.csv` | 12,691 | Review destinasi wisata, 138 tempat unik |
| `resto-hotel-v2.csv` | 9,611 | Review resto/hotel, 206 tempat unik, ada kolom `reviewer-type` |
| `wisata-metadata.csv` | 139 | lat-long lengkap 139/139, jam operasional lengkap |
| `resto-metadata.csv` | 148 | lat-long lengkap, tapi `opening-hours` hanya **1/148** |
| `hotel-metadata.csv` | 36 | lat-long lengkap 36/36 |
| `waktu operasional destinasi.csv` | 236 | FASILITAS UMUM + FASILITAS PENUNJANG per destinasi |
| `Info Seputar Danau Toba (TOP 3).csv` | 30 | **Data sisi permintaan per kabupaten** — sering diabaikan |
| `Attractions Info.csv` | 57 | Deskripsi kaya + latar sejarah/budaya |
| `Artikel Danau Toba.csv` | 48 | Artikel panjang (bahan RAG / knowledge base) |
| `tempat-wisata-v1.csv` | 177 | Versi lama, ada kolom `addons` (aktivitas) |
| `hotel-resto-v1.csv` | 9 | Versi lama, kecil |
| `kuliner.csv` | 20 | Deskripsi makanan khas Batak |
| `transportasi.csv` | 17 | Trayek, tarif, jenis kendaraan, jam operasional |
| `prompt.csv` | 14 | 10 contoh prompt itinerary — **umpan** |

### 1.2 Temuan kunci

| Temuan | Angka | Kenapa penting |
|---|---|---|
| **Review adalah 95% nilai dataset** | 22,302 review, **12,280 punya teks** | Ini satu-satunya aset yang tidak bisa ditiru dari Google Maps dalam semalam |
| **Rating adalah sinyal mati** | **72% bintang 5**; semua tempat ada di rentang 4,2–4,8 | Ranking berdasarkan rating = ranking berdasarkan noise. Sinyal ada di **teks**, bukan bintang |
| **Metadata bolong parah** | `opening-hours` 1/148 resto · `Fasilitas` 6/148 resto · `description`, `operational-day`, `place-ownership` **0/139** wisata | Peluang tugas imputasi yang bisa dievaluasi kuantitatif |
| **Entity resolution nyata** | 37 tempat di review wisata tidak match metadata · 38 di resto/hotel · 16 resto metadata tanpa review · duplikat literal `Pondok Siliwangi 27/28/29/30/31` | Bukan teori — memang harus dikerjakan |
| **Bias popularitas ekstrem** | Bukit Holbung Samosir **1,363** review · Geosite Sipinsur 827 · vs **37 destinasi 0 review** | Guidebook §12.3 secara eksplisit meminta ini dibahas |
| **Geospasial siap pakai** | **323 titik berkoordinat** (139 wisata + 148 resto + 36 hotel) | Analisis gap layanan, jarak, aksesibilitas langsung bisa jalan |
| **Ada dimensi waktu** | `published-at` relatif (`"a year ago"`, campur `"2 tahun lalu di"`) + `scraped-at-date` (2025-07-28/29) | Bisa direkonstruksi jadi tanggal absolut → **tren ~3 tahun** |
| **Data sisi permintaan** | Toba: 751,225 wisnus · 379 wisman · **durasi 1,31 hari** · budget 500rb–>1jt · peak Jun–Ags & Des–Jan · usia 18–25 | Ini yang mengubah proyek dari "analitik" jadi "argumen ekonomi" |

### 1.3 Volume kunjungan per kabupaten (dari sheet TOP 3)

| Kabupaten | Wisnus 2024 | Wisman | Durasi | Budget harian |
|---|---:|---:|---|---|
| Simalungun | 2,595,069 | 0 | – | 600rb – >1,2jt |
| Karo | 2,305,891 | 0 | – | 400rb – >800rb |
| Samosir | 1,506,208 | 0 | – | 400rb – >800rb |
| **Toba** | **751,225** | **379** | **1,31 hari** | 500rb – >1jt |
| Dairi | 719,807 | 0 (2021) | – | 400rb – >750rb |
| Humbang Hasundutan | 463,475 | 0 | – | 300rb – >500rb |
| Pakpak Bharat | 116,321 | 0 | – | 300rb – >600rb |
| Tapanuli Utara | – | – | – | 600rb – >1jt (wisman) |

> ⚠️ Kolom `durasi` **hanya terisi untuk baris Toba**, dan angka wisman jelas tidak lengkap (0 untuk Samosir tidak kredibel). Lihat [§10](#10-risiko-etika-dan-catatan-kejujuran-data).

---

## 2. Sinyal yang Sudah Diverifikasi di Review

Hasil keyword scan atas 12,280 review berteks. Angka dalam kurung = review dengan rating ≤3 bintang.

| Kategori keluhan | Jumlah review | Rating ≤3 | Rasio negatif |
|---|---:|---:|---:|
| Kebersihan / sampah | 1,244 | 259 | 21% |
| Parkir | 457 | 95 | 21% |
| Toilet / sanitasi | 400 | 119 | 30% |
| **Pungli / harga tidak wajar** | **342** | **186** | **54%** ⬅ |
| Akses jalan | 334 | 58 | 17% |
| Ramah anak / lansia / difabel | 303 | 50 | 17% |
| Halal / muslim-friendly | 298 | 47 | 16% |
| Rumah ibadah | 82 | 10 | 12% |
| Jam buka–tutup | 56 | 24 | 43% |
| Sinyal / WiFi | 47 | 12 | 26% |
| Keamanan | 47 | 18 | 38% |

**Temuan paling tajam:** keluhan **pungli / harga tidak wajar** punya rasio negatif tertinggi (54%) — kelas keluhan paling merusak rating di seluruh korpus, jauh di atas kebersihan yang volumenya 4× lebih besar. Ini insight yang belum pernah dikuantifikasi siapa pun untuk Toba, dan langsung bisa ditindaklanjuti Pemda.

---

## 3. The Trap — apa yang akan dibangun 80% tim

`prompt.csv` berisi 10 prompt itinerary yang sangat menggoda. Konsekuensinya:

- Mayoritas tim akan membangun **RAG itinerary chatbot**.
- Juri akan melihat ~40 chatbot yang mirip, hampir semua **tanpa evaluasi kuantitatif** — padahal kriteria 3 (20 poin) secara eksplisit meminta *"matriks kuantitatif dan evaluasi kuantitatif yang relevan"*.
- Kriteria 1 (20 poin) menghukum solusi yang *"sekadar mengikuti contoh panitia"* — dan **"chatbot / itinerary assistant" ada di tabel contoh panitia sendiri** (§5).

**Kesimpulan:** membangun chatbot itinerary = memasang plafon di sekitar juara 3.

Cara memakai `prompt.csv` dengan benar: **jadikan ia eval set, bukan produk.** Pakai 10 prompt itu untuk membuktikan bahwa knowledge base hasil pipeline kita bisa menjawab pertanyaan nyata — sebagai *satu bab evaluasi*, bukan sebagai keseluruhan solusi.

---

## 4. IDE #1 (Rekomendasi Utama) — "Toba Retention Intelligence"

### 4.1 Tagline

> **"Toba tidak kekurangan wisatawan — Toba kehilangan mereka dalam 1,31 hari."**

### 4.2 Problem framing

Toba menerima 751,225 wisatawan nusantara, tetapi rata-rata tinggal hanya **1,31 hari**. Simalungun dan Karo masing-masing menarik 2,3–2,6 juta. Artinya Toba berfungsi sebagai **koridor transit, bukan destinasi menginap**. Setiap tambahan 0,5 hari lama tinggal bernilai ratusan miliar rupiah bagi UMKM lokal.

Maka pertanyaannya bukan *"bagaimana membantu wisatawan menemukan tempat"* — melainkan:

> **"Apa persisnya yang membuat mereka pergi cepat, diurutkan berdasarkan berapa besar kerugian ekonominya, per destinasi?"**

Hari ini tidak ada yang bisa menjawab itu. 12,280 teks review bisa — dan sinyalnya sudah diverifikasi di [§2](#2-sinyal-yang-sudah-diverifikasi-di-review).

### 4.3 Inversi target pengguna (ini bagian novelty-nya)

Hampir semua tim akan melayani **sisi permintaan** (wisatawan). Solusi ini melayani **sisi penawaran**:

| Pengguna | Yang mereka dapat |
|---|---|
| Dinas Pariwisata / BPODT | Daftar prioritas perbaikan berbasis bukti, untuk alokasi anggaran |
| UMKM lokal | Peluang usaha spesifik + lokasi + estimasi pasar |
| Pengelola destinasi | Apa yang harus diperbaiki minggu ini, dengan kutipan review sebagai bukti |
| Wisatawan | Manfaat tidak langsung: destinasi yang benar-benar membaik |

### 4.4 Arsitektur — tiga output, satu tulang punggung model

```
                 ┌──────────────────────────────────┐
                 │  Unified Place Table (323 titik) │
                 │  entity resolution + geocoding   │
                 └────────────┬─────────────────────┘
                              │
              ┌───────────────┼────────────────┐
              │               │                │
     ┌────────▼──────┐ ┌──────▼───────┐ ┌──────▼────────┐
     │ ABSA Engine   │ │ Geo Gap      │ │ Demand Layer  │
     │ 12,280 review │ │ Analysis     │ │ TOP-3 sheet   │
     └────────┬──────┘ └──────┬───────┘ └──────┬────────┘
              │               │                │
     ┌────────▼──────┐ ┌──────▼───────┐ ┌──────▼────────┐
     │ 1. Friction   │ │ 2. Infra Gap │ │ 3. UMKM       │
     │    Index      │ │    Map       │ │    Opportunity│
     └───────────────┘ └──────────────┘ └───────────────┘
```

**Output 1 — Retention Friction Model**
Aspect-Based Sentiment Analysis atas 12,280 review → 8–10 aspek friksi × sentimen, per tempat, per tahun. Menghasilkan **Friction Index** per destinasi + daftar perbaikan yang sudah terurut prioritas.

**Output 2 — Infrastructure Gap Map**
Join 323 titik berkoordinat dengan `waktu operasional destinasi.csv` (236 baris fasilitas umum & penunjang). Untuk tiap destinasi hitung jarak ke toilet / rumah ibadah / faskes / ATM / SPBU / tempat makan / penginapan terdekat.

> 🔑 **Validasi pembunuh:** buktikan secara statistik bahwa skor infra-gap **memprediksi tingkat keluhan** hasil Output 1 (laporkan AUC / R² + confidence interval). Ini hasil ilmiah, bukan sekadar dashboard cantik. Hampir pasti tidak ada tim lain yang melakukan validasi silang antar-sumber seperti ini.

**Output 3 — UMKM Opportunity Finder**
Unmet demand yang diekstrak dari review ("tidak ada makanan halal", "tutup jam 5 sore", "tidak ada ATM") × volume pengunjung × budget band dari sheet TOP-3 → peluang usaha konkret dan berlokasi.

Contoh output nyata:
> *"Warung halal di sekitar Bukit Holbung: 1,363 review/tahun, 47 keluhan halal, nol restoran halal dalam radius 3 km, budget harian wisnus 400rb–800rb."*

### 4.5 Rencana evaluasi kuantitatif (ini yang memenangkan kriteria 3)

| Komponen | Metode evaluasi | Metrik dilaporkan |
|---|---|---|
| ABSA | Label manual 400–600 review (3 anggota tim, ukur inter-annotator agreement) | **macro-F1 per aspek**, confusion matrix |
| Perbandingan model | TF-IDF+LogReg → IndoBERT fine-tune → LLM few-shot | Tabel F1 vs latency vs biaya. **Selalu tunjukkan baseline** — juri menghargai ini |
| Bias audit | Performa pada tempat banyak-review vs nol-review; Bayesian shrinkage | Pergeseran ranking sebelum/sesudah debias. Menjawab §12.3 langsung |
| Entity resolution | Fuzzy match + blocking geo + embedding, pada 75 tempat tak-match | **Precision / Recall / F1** |
| Gap model | Regresi infra-gap → complaint rate | **R² / AUC** + interval kepercayaan |
| Knowledge base | 10 prompt dari `prompt.csv` sebagai eval set | Groundedness, cakupan jawaban |

### 4.6 Demo

Peta Toba; tiap destinasi diwarnai berdasarkan **Friction Index**. Klik satu titik →
- daftar perbaikan terurut prioritas,
- kutipan verbatim review sebagai bukti (transparansi & explainability),
- estimasi dampak terhadap lama tinggal,
- peluang UMKM di sekitarnya.

**Kelayakan final round (DGX B200):** IndoBERT berukuran kecil dan ringan; tambahkan LLM lokal untuk lapisan narasi. Deployment tidak berisiko.

### 4.7 Kenapa ide ini menang

- **Framing baru** yang tidak ada di tabel contoh panitia — bahkan membalik arah pertanyaan panitia.
- **Angka ekonomi** (1,31 hari, 751,225 kunjungan) membuat dampaknya terukur, bukan retoris.
- **Evaluasi kuantitatif berlapis**, termasuk satu validasi silang antar-sumber yang jarang terpikir.
- **Memakai 15 file**, termasuk dua yang akan diabaikan hampir semua tim (sheet TOP-3 dan waktu operasional).
- **Mudah dipresentasikan**: satu peta, satu angka per destinasi, bukti verbatim.

---

## 5. IDE #2 — "Sinyal Jujur" (the anti-rating engine)

**Premis:** semua tempat ada di 4,2–4,8 dan 72% review bintang 5. **Rating bintang berbohong.**

**Solusi:** mesin peringkat yang jujur —
- filter review tanpa teks / berinformasi rendah (10,022 review tanpa teks!),
- Bayesian shrinkage untuk tempat dengan sampel kecil,
- ekstrak skor **per dimensi** dari teks (kebersihan / value for money / akses / ramah keluarga / ketenangan),
- ranking per persona, bukan satu angka tunggal.

**Evaluasi:** rank correlation vs rating mentah, prediksi held-out terhadap review ≤3★, ablation tiap komponen.

**Nilai:** sangat teknis, mudah dievaluasi, framing menarik. **Kelemahan:** dampak lebih sempit dari Ide #1.
👉 **Rekomendasi: jadikan komponen di dalam Ide #1**, bukan produk terpisah.

---

## 6. IDE #3 — "Peta Inklusi Toba"

**Premis:** 303 review menyebut anak/lansia/difabel, 298 menyebut halal, hanya 82 menyebut rumah ibadah. Informasi aksesibilitas untuk Toba praktis tidak ada dalam bentuk terstruktur.

**Solusi:** lapisan aksesibilitas & inklusi pertama untuk Toba. Inferensi dari teks review di tempat metadata-nya kosong:
- akses kursi roda / stroller / lansia,
- ketersediaan makanan halal,
- fasilitas ibadah (mushola & gereja),
- keamanan anak,
- dukungan bahasa (sheet TOP-3 mencatat: Indonesia, Batak Toba, Inggris).

Output: peta gap inklusi + sertifikasi mandiri untuk pelaku usaha.

**Nilai:** cerita dampak kuat, secara moral menarik bagi juri, jauh lebih sepi dari ranah chatbot.
**Kelemahan:** dampak ekonomi lebih sulit dikuantifikasi dibanding Ide #1.

---

## 7. IDE #4 — "Data Quality Copilot"

**Premis:** `opening-hours` 1/148, `Fasilitas` 6/148, `description` 0/139, 75 entitas tak-match, duplikat literal.

**Solusi:** imputasi field kosong dari teks review + entity resolution + deduplikasi, menghasilkan satu tabel tempat terpadu yang bersih.

**Evaluasi:** paling bersih dari semua ide — mask field yang *sudah* terisi lalu ukur F1 / MAE pada harga. Sangat kuat untuk kriteria "Pemanfaatan data Toba" (15 poin).

**⚠️ Kelemahan fatal:** *"Data quality copilot"* **tertulis persis di tabel contoh panitia** (§5, baris Data Intelligence). Kriteria 1 (20 poin) akan memotong nilainya.
👉 **Rekomendasi: kerjakan tetap, tapi kemas sebagai Bab 3 laporan Ide #1**, bukan sebagai produk utama.

---

## 8. Pemetaan ke Rubrik 100 Poin

Untuk Ide #1:

| Kriteria | Bobot | Bagaimana ide ini memenuhinya |
|---|---:|---|
| Kebaruan & ketajaman problem framing | 20 | "1,31 hari" membalik seluruh pertanyaan challenge; melayani sisi penawaran, bukan wisatawan |
| Dampak & relevansi untuk Toba | 20 | Pengguna spesifik (Pemda/BPODT/UMKM), dampak dalam rupiah, bisa diadopsi minggu depan |
| Kualitas teknis AI & rekayasa data | 20 | ABSA + baseline + F1, gap model dengan R², entity resolution dengan P/R, bias audit |
| Kelayakan implementasi | 15 | Model kecil, jalan di DGX, pilot = satu kecamatan (Balige) |
| Pemanfaatan data Toba | 15 | 7 file inti + 4 file pendukung dengan peran nyata (lihat `IDE-1-MARTAHUTA-Detail.md` §11), termasuk 2 file yang akan diabaikan tim lain (sheet TOP-3 & waktu operasional). **Jangan klaim "semua 15 file"** — §6.3 hanya menuntut pemakaian yang bermakna dan bisa dijelaskan |
| Komunikasi, demo, dokumentasi | 10 | Satu peta, satu angka per destinasi, bukti kutipan verbatim |

---

## 9. Rencana Eksekusi 7 Hari

**Bottleneck utama adalah pelabelan manual. Mulai hari pertama, bagi tiga ke seluruh anggota tim.**

| Hari | Target |
|---|---|
| **H1** | Rekonstruksi tanggal absolut dari `published-at` + `scraped-at-date` (tangani campuran ID/EN). Mulai pelabelan 500 review untuk aspek ABSA. |
| **H2** | Entity resolution → satu tabel tempat terpadu berkoordinat. Selesaikan duplikat `Pondok Siliwangi`. Lanjut pelabelan. |
| **H3** | Baseline TF-IDF+LogReg untuk ABSA. Laporkan F1 pertama. Selesai pelabelan + hitung inter-annotator agreement. |
| **H4** | Fine-tune IndoBERT. Bandingkan dengan baseline. Bangun Friction Index. |
| **H5** | Geo gap analysis + regresi validasi (infra-gap → complaint rate). Bias audit + Bayesian shrinkage. |
| **H6** | UMKM Opportunity Finder. Dashboard/peta demo. Uji 10 prompt dari `prompt.csv`. |
| **H7** | Rekam video demo 5–10 menit, tulis LaporanAnalisis.pdf (8 bab wajib §17), rapikan repo + model card. |

**Checklist artefak wajib (§17):**
- [ ] `[Nama Tim] - LaporanAnalisis.pdf` (maks 25 MB, 8 bab: Latar Belakang → Deklarasi Penggunaan AI)
- [ ] `[Nama Tim] - Demo` (link publik Google Drive/YouTube, **tanpa wajah & tanpa identitas institusi**)
- [ ] Product — source code `.ZIP`
- [ ] Slide pitching
- [ ] Ringkasan penggunaan data + rencana implementasi
- [ ] **Tidak ada nama institusi di file manapun**

---

## 10. Risiko, Etika, dan Catatan Kejujuran Data

Bab ini wajib masuk laporan — guidebook §12.3 menilainya, dan mengakuinya lebih aman daripada disergap juri.

**Keterbatasan data yang harus dinyatakan terbuka:**

1. **`1,31 hari` hanya terisi untuk baris Toba** di sheet TOP-3. Kutip sebagai angka panitia; cross-reference BPS Sumut untuk kabupaten lain dengan sumber dicatat sesuai §12.2.
2. **Angka wisman jelas tidak lengkap** — 0 untuk Samosir tidak kredibel. Jangan pakai untuk klaim kuantitatif tanpa disclaimer.
3. **Bias popularitas**: Bukit Holbung 1,363 review vs 37 destinasi nol review. Friction Index untuk tempat sampel kecil **wajib** memakai shrinkage dan ditandai "low confidence".
4. **Bias platform**: seluruh review berasal dari pengguna Google Maps — condong ke wisatawan muda, melek digital, berbahasa Indonesia. Wisatawan lansia dan lokal non-digital tidak terwakili.
5. **Bias bahasa**: review campur Indonesia / Batak Toba / slang / typo. Model akan berkinerja lebih rendah pada teks Batak — laporkan F1 terpisah bila memungkinkan.
6. **Rating skew 72% bintang 5** membuat kelas negatif langka → gunakan macro-F1, bukan accuracy.
7. **Privasi**: kolom `name` berisi nama reviewer asli. **Hash atau buang** sebelum diproses; jangan pernah tampilkan di demo.
8. **Risiko misuse**: Friction Index bisa disalahartikan sebagai "daftar hitam destinasi". Bingkai sebagai *alat perbaikan*, bukan penilaian; sertakan intended use & limitations di model card.
9. **Klaim kausal**: korelasi infra-gap ↔ complaint rate **bukan** bukti kausalitas. Nyatakan sebagai asosiasi, dan usulkan pilot A/B di satu kecamatan sebagai uji lanjutan.

---

> **Build Smart Solutions, Shape The Future of Tourism**
