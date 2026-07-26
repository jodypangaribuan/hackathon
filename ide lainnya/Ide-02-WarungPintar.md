# WarungPintar — UMKM Growth Copilot

> **Tagline:** *"Setiap pemilik rumah makan di Toba kini punya analis bisnis pribadi — gratis, 24/7, bicara bahasa mereka."*

---

## 1. Ringkasan Eksekutif

**WarungPintar** adalah AI copilot untuk pelaku UMKM pariwisata Toba — pemilik rumah makan, kafe, homestay, dan toko oleh-oleh. Sistem membaca ulasan Google Maps tentang bisnis mereka, membandingkan dengan kompetitor sekitar, lalu memberikan **3 action items prioritas mingguan** untuk meningkatkan rating dan pendapatan.

Bukan dashboard yang ditonton — tapi **coach yang mengoreksi dan mendorong**.

### Posisi di Rubrik Penilaian

| Kriteria | Bobot | Target | Strategi |
|---|---|---|---|
| Kebaruan problem framing | 20 | 15-17 | UMKM copilot dari review data = validated by Reskilll 2026 |
| Dampak & relevansi | 20 | 18-20 | Beneficiary super konkret: 148 RM + 36 hotel |
| Kualitas teknis | 20 | 15-17 | ABSA + competitor clustering + LLM action generator |
| Kelayakan implementasi | 15 | 14-15 | UMKM bisa pakai besok, butuh WhatsApp saja |
| Pemanfaatan data | 15 | 14-15 | resto-metadata + 12K resto reviews = maksimal |
| Komunikasi & demo | 10 | 9-10 | Demo paling greget: reveal insight kompetitor |
| **TOTAL** | **100** | **85-94** | |

---

## 2. Problem Framing

### Masalah Utama
Pak Torang punya RM Sinar Minang di Balige. Setiap hari ada 5-10 ulasan Google Maps. Pak Torang:
- **Tidak punya waktu** baca semua ulasan
- **Tidak paham analitik** — angka rating tidak actionable
- **Tidak tahu posisi vs kompetitor** — RM sebelah lebih ramai, kenapa?
- **Tidak ada akses konsultan bisnis** — mahal, tidak tersedia di Toba

### Urgensi
148 restoran + 36 hotel di dataset adalah **nyawa ekonomi lokal**. Banyak yang bergantung pada rating Google Maps untuk dapat tamu. Penurunan rating 0.5 bintang = penurunan kunjungan 10-20%.

### Insight Kunci dari Data
- `resto-metadata.csv` punya `recommend-menu` untuk 60% resto → bisa compare menu populer
- `resto-hotel-v2.csv` punya `reviewer-type` (Keluarga/Pasangan/Bisnis) → segmentasi customer
- Banyak resto dengan **rating tinggi tapi review sedikit** → peluang promosi
- Banyak resto dengan **rating rendah tapi lokasi strategis** → masalah operasional

---

## 3. Fitur Detail

### Fitur 1: Review Mirror (Weekly Health Check)

**Cara kerja:**
Pemilik login pilih nama resto → sistem rangkum:

```
┌──────────────────────────────────────────────┐
│  RM SINAR MINANG — Mingguan Health Report    │
│  23-29 Juli 2026                              │
├──────────────────────────────────────────────┤
│  Rating: 4.2 ⬇ (-0.1 minggu ini)             │
│  Review baru: 8 (vs avg 5/minggu)            │
│                                              │
│  ✓ KELEBIHAN (disebut 6 dari 8 review):      │
│    "Mie Gomak enak", "porsi besar"           │
│                                              │
│  ⚠ KEKURANGAN (disebut 5 dari 8 review):     │
│    "lama", "parkir sempit", "pelayanan"      │
│                                              │
│  📊 SEGMENT PELANGGAN:                        │
│    Keluarga 50% | Pasangan 30% | Bisnis 20%  │
│    Pelanggan bisnis paling tidak puas (3.8)  │
└──────────────────────────────────────────────┘
```

**Tech:** IndoBERT ABSA + LLM summarization

### Fitur 2: Competitor Radar

**Cara kerja:**
- Geospatial clustering (DBSCAN) untuk find kompetitor dalam radius 2km
- Bandingkan: rating, harga, menu, fasilitas
- Highlight gap & opportunity

**Contoh output:**
```
KOMPETITOR ANDA (radius 2km dari RM Sinar Minang):

1. RM Fly Over Laguboti — Rating 4.5 ⬆ vs Anda 4.2
   Harga: Rp 35K (vs Anda Rp 25K)
   Keunggulan mereka: delivery, wifi, AC
   ⚡ ANDA BISA: tambah delivery via GoFood

2. Damar Toba — Rating 4.1 ⬇
   Harga: Rp 50K
   ⚡ MEREKA LEMAH DI: pelayanan
   ANDA BISA: highlight "pelayanan cepat" di marketing

3. Batikta Balige — Rating 4.3
   Menu unggulan: Babi Panggang Karo
   ⚡ ANDA TIDAK PUNYA: menu signature Batak
   Pertimbangkan: tambah Saksang atau Naniura
```

### Fitur 3: Action Coach (3 Prioritas Mingguan)

**Cara kerja:**
LLM analisis semua insight → generate 3 action spesifik, actionable, terukur:

```
🎯 3 ACTION PRIORITAS MINGGU INI:

1. [CEPAT - 1 hari] Balas 8 review terakhir.
   Template: "Makasih kak... Untuk keluhan parkir,
   kami sedang koordinasi dengan RT..."

2. [SEDANG - 1 minggu] Daftar GoFood/GrabFood.
   60% kompetitor punya delivery. Anda tertinggal.
   Estimasi naik: +15% transaksi.

3. [STRATEGIS - 1 bulan] Tambah menu signature Batak.
   Pelanggan keluarga cari pengalaman lokal.
   Rekomendasi: Saksang (cost Rp 15K, jual Rp 40K).
```

### Fitur 4: Menu & Pricing Optimizer

**Cara kerja:**
- Compare harga menu Anda vs kompetitor dengan kualitas serupa
- Identifikasi underpriced (perlu naik) / overpriced (perlu turun)
- Rekomendasi menu baru berdasarkan tren review

### Fitur 5: Customer Persona Insights

**Cara kerja:**
- Dari `reviewer-type` di resto-hotel-v2.csv
- Profil per segmen: Keluarga, Pasangan, Bisnis, Solo
- Insight: "Pelanggan Pasangan suka sunset view — pertimbangkan dekorasi romantis"

---

## 4. Arsitektur Teknis

```
┌──────────────────────────────────────────────┐
│           PEMILIK UMKM (WhatsApp / Web)       │
└────────────────────┬─────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────┐
│            GRADIO / STREAMLIT WEB APP         │
└────────────────────┬─────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Review   │  │Competitor│  │  Action  │
│ Mirror   │  │  Radar   │  │  Coach   │
│ (ABSA)   │  │(DBSCAN)  │  │  (LLM)   │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │
     └─────────────┴─────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│     DATA LAYER                                │
│  • reviews DB (12K resto reviews)            │
│  • resto metadata (148 places)               │
│  • geo clustering index                      │
│  • aspect sentiment scores                   │
└──────────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│  LLM (Llama 3.1 8B di B200 via vLLM)         │
│  Action generation + summarization           │
└──────────────────────────────────────────────┘
```

### Tech Stack Detail

| Komponen | Teknologi |
|---|---|
| Sentiment | IndoBERT fine-tuned untuk 6 aspek |
| Clustering | scikit-learn DBSCAN (lat/long) |
| LLM | Llama 3.1 8B via vLLM (B200) |
| Web | Gradio (simplest) atau Streamlit |
| Geospatial | Folium + haversine distance |
| Deploy | Docker di B200 |

---

## 5. Pemanfaatan Dataset

| File | Pemanfaatan |
|---|---|
| `resto-metadata.csv` (148) | Master DB: nama, harga, menu, fasilitas, lokasi |
| `resto-hotel-v2.csv` (12K) | Review analisis, reviewer-type segmentation |
| `hotel-metadata.csv` (36) | Untuk homestay/hotel copilot |
| `kuliner.csv` (10) | Knowledge base menu Batak + deskripsi |
| `Info TOP 3.csv` | Resto unggulan per kabupaten untuk benchmark |
| `waktu operasional.csv` | Fasilitas pendukung untuk rekomendasi |

### Data Pipeline
1. **Clean resto-metadata** — normalize price (`,.` inconsistency), extract menu items
2. **Parse reviews** — extract per-place review corpus
3. **Geocode** — lat/long untuk distance computation
4. **ABSA label** — manual 300 reviews, fine-tune IndoBERT
5. **Cluster** — DBSCAN per kabupaten untuk competitor group

---

## 6. Execution Plan

### Preliminary Round

**Minggu 1: Data + Sentiment**
- [ ] Cleaning resto-metadata (fix price format, menu extraction)
- [ ] EDA: rating distribution, price vs rating correlation
- [ ] IndoBERT fine-tune (Colab T4) — target F1 0.80+
- [ ] Aspect extraction dari 12K reviews

**Minggu 2: Core Features**
- [ ] DBSCAN competitor clustering
- [ ] Review Mirror logic (per-place summarization)
- [ ] Action Coach prompt engineering (Gemini API)
- [ ] Gradio prototype

**Minggu 3: Demo + Submission**
- [ ] Pilih 3 resto showcase (1 sukses, 1 sedang, 1 bermasalah)
- [ ] Video demo — focus storytelling UMKM
- [ ] LaporanAnalisis.pdf
- [ ] Code .ZIP

### Final Round (2 hari lockdown)

**Day 1:**
- Pagi: Deploy Llama 3.1 8B di B200
- Siang: Migrasi Action Coach dari API → local LLM
- Sore: Polish UI, add Competitor Radar interactive map
- Malam: Menu & Pricing Optimizer logic

**Day 2:**
- Pagi: Final test, demo rehearsal
- 12:00: Submit & present

---

## 7. Evaluasi Model

| Metrik | Target | Metode |
|---|---|---|
| ABSA F1 | ≥ 0.80 | 100 labeled reviews test |
| Competitor Detection Precision | ≥ 0.85 | Manual check 20 resto |
| Action Specificity (LLM eval) | ≥ 4/5 | Manual rating 30 actions |
| Price Recommendation Acc | ≥ 75% | Compare with market data |
| User Satisfaction (proxy) | N/A | Demo audience feedback |

---

## 8. Demo Script (10 Menit)

### Setup
- Pre-load 3 resto profiles ( RM Sinar Minang, Tabo Cottages, satu hideen gem)

### Script

**[0:00-1:30] Story Hook**
> "Pak Torang, pemilik RM Sinar Minang, bangun pagi, buka Google Maps. Ada 12 ulasan baru. Dia tidak baca — sibuk masak. Tapi di antara 12 ulasan itu, ada 5 keluhan tentang pelayanan lambat. Satu bulan kemudian, rating turun dari 4.3 ke 4.0. Tamu berkurang. Pak Torang tidak tahu kenapa."

**[1:30-3:30] Feature 1: Review Mirror**
- Login sebagai Pak Torang
- Tampilkan Weekly Health Report
- "Dalam 5 detik, Pak Torang tahu: rating turun, masalah utama pelayanan"

**[3:30-5:30] Feature 2: Competitor Radar**
- Klik "Lihat Kompetitor"
- Tampilkan peta dengan 5 RM sekitar
- Reveal: "RM Fly Over 500m dari sini, rating 4.5, punya delivery. Anda tidak."
- "Pak Torang baru sadar — selama ini dia tidak tahu posisinya"

**[5:30-7:30] Feature 3: Action Coach**
- Klik "Apa yang harus saya lakukan?"
- AI generate 3 action: balas review, daftar GoFood, training pelayanan
- "Bukan insight. Action. Spesifik. Terukur. Bisa dieksekusi hari ini."

**[7:30-9:00] Technical + Impact**
- Arsitektur slide
- "148 RM di Toba. Rata-rata pemilik tidak punya akses konsultan bisnis. WarungPintar adalah konsultan gratis, 24/7."

**[9:00-10:00] Scale & Vision**
- "Mulai dari 148 RM Toba. Skalakan ke seluruh Indonesia."
- "UMKM adalah 60% PDB pariwisata. Ini bukan fitur — ini empowerment."

---

## 9. Risiko & Mitigasi

| Risiko | Mitigasi |
|---|---|
| Reviewer-type kosong di banyak row | Fallback ke inference dari review text |
| Kompetitor cluster tidak akurat | Manual validate top 10, fallback to manual list |
| Action Coach generik | Few-shot prompting dengan example actionable |
| Bahasa Batak di review | IndoBERT multilingual handle, fallback lexicon |
| Demo internet mati | Pre-cache 3 resto profiles |

---

## 10. Differentiator

| Tim Lain | WarungPintar |
|---|---|
| Analitik untuk akademisi | Copilot untuk UMKM |
| Insight abstrak | Action items spesifik |
| Dashboard generik | Weekly report seperti konsultan bisnis |
| Fokus wisatawan | Fokus pelaku usaha lokal |

---

## 11. Rencana Keberlanjutan

### Pilot Plan
- Kolaborasi dengan Koperasi UMKM Toba
- Onboard 20 RM pilot selama 2 bulan
- Metric: rating naik 0.2 rata-rata dalam 3 bulan

### Skala
- WhatsApp bot (akses tanpa app baru)
- Partnership dengan GoFood/GrabFood untuk integrasi
- Expand ke 5 Prioritas Destinasi Pariwisata lain (Borobudur, Labuan Bajo, dll)

### Sustainability
- Freemium: laporan mingguan gratis, deep analysis berbayar
- B2B: Dispar subscribe untuk monitoring seluruh UMKM di wilayahnya
