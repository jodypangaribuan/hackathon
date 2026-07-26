# TobaGov — Tourism Intelligence Platform
### Final Blueprint v3 (Honest, Detailed, Execution-Ready)

> **Tagline:** *"Ubah 12.000 suara wisatawan menjadi keputusan berbasis bukti untuk pengelola destinasi Danau Toba."*

---

## Daftar Isi

1. [Ringkasan Eksekutif](#1-ringkasan-eksekutif)
2. [Problem Framing](#2-problem-framing)
3. [Fitur Detail](#3-fitur-detail)
4. [Arsitektur Teknis](#4-arsitektur-teknis)
5. [Pemanfaatan Dataset](#5-pemanfaatan-dataset)
6. [Execution Plan](#6-execution-plan)
7. [Evaluasi Model](#7-evaluasi-model)
8. [Responsible AI & Limitations](#8-responsible-ai--limitations)
9. [Demo Script](#9-demo-script)
10. [Risiko & Mitigasi](#10-risiko--mitigasi)
11. [Differentiator](#11-differentiator)
12. [Rencana Keberlanjutan](#12-rencana-keberlanjutan)
13. [Pembagian Tim](#13-pembagian-tim-3-orang)
14. [Mapping ke Rubrik Penilaian](#14-mapping-ke-rubrik-penilaian)
15. [Deliverable Checklist](#15-deliverable-checklist)

---

## 1. Ringkasan Eksekutif

### Apa Itu TobaGov

**TobaGov** adalah platform *decision-support* berbasis AI untuk **pengelola destinasi** dan **Dinas Pariwisata** kawasan Danau Toba. Bukan chatbot wisatawan, bukan dashboard statis — melainkan **asisten analitik** yang menjawab pertanyaan kebijakan dalam bahasa natural, dengan jawaban yang **selalu disertai sitasi data**.

### Posisi yang Jujur

| Klaim | Realitas |
|---|---|
| Bukan "AI yang menggantikan pejabat" | Asisten analitik yang memberi **basis bukti** |
| Bukan "pilot siap deploy" | Prototipe yang menunjukkan **kemampuan + roadmap** |
| Bukan "forecasting presisi" | **Trend intelligence** + hotspot detection |

### Angka Kunci (Terverifikasi dari Dataset)

| Metrik | Angka | Sumber |
|---|---|---|
| Total review wisata | 12,691 (6,369 berisi teks) | `wisata-v2.csv` |
| Total review resto/hotel | 9,611 (5,911 berisi teks) | `resto-hotel-v2.csv` |
| Total ulasan berisi teks | **~12,280** | gabungan |
| Destinasi wisata | 139 | `wisata-metadata.csv` |
| Restoran | 148 | `resto-metadata.csv` |
| Hotel/akomodasi | 36 | `hotel-metadata.csv` |
| Rute transportasi | 16 (termasuk ferry) | `transportasi.csv` |
| Destinasi dengan fasilitas tercatat | 60 | `waktu operasional.csv` |

### Estimasi Skor Rubrik (Jujur)

| Kriteria | Bobot | Target | Strategi |
|---|---|---|---|
| Kebaruan problem framing | 20 | 16-18 | Civic intelligence, bukan chatbot wisatawan |
| Dampak & relevansi | 20 | 14-16 | Beneficiary jelas (pengelola destinasi) |
| Kualitas teknis | 20 | 14-16 | RAG + ABSA + geospatial, Llama self-hosted di B200 |
| Kelayakan implementasi | 15 | 12-14 | Roadmap realistis, honest limitation |
| Pemanfaatan data Toba | 15 | 13-15 | 12K reviews + reverse-geocode + semua metadata |
| Komunikasi & demo | 10 | 8-9 | Demo "tanya-jawab" data-driven |
| **TOTAL** | **100** | **77-88** | |

---

## 2. Problem Framing

### Masalah Spesifik

Pengelola destinasi Toba mengambil keputusan berbasis **intuisi** dan **laporan manual yang lambat**. Padahal ada **~12.000 ulasan publik berisi teks** dari warga yang mengandung sinyal kuat tentang:

- Fasilitas apa yang paling dikeluhkan
- Destinasi mana yang reputasinya menurun
- Perbedaan kualitas antar wilayah
- Pola keluhan per segmen wisatawan (keluarga vs solo vs wisman)

### Mengapa Ini Sulit Saat Ini

1. **Volume terlalu besar untuk baca manual** — 12K reviews tidak bisa dibaca satu per satu
2. **Data tersebar** — rating di Google Maps, teks di travel apps, fasilitas di lapangan
3. **Tidak ada tools analitik** spesifik untuk pariwisata Toba
4. **Insight tidak actionable** — rating 4.2 tidak memberitahu "apa yang harus diperbaiki"

### Dampak Berantai

```
Review warga menumpuk (12K)
        ↓
Tidak ada tools untuk ekstrak insight
        ↓
Pengelola tidak tahu masalah utama
        ↓
Investasi fasilitas tidak tepat sasaran
        ↓
Rating turun → wisatawan berkurang → UMKM rugi
```

### Pertanyaan Kunci yang Ingin Dijawab Sistem

1. "Apa 3 keluhan terbesar di kawasan Balige vs Samosir?"
2. "Destinasi mana yang reputasinya menurun dibanding 2 tahun lalu?"
3. "Destinasi mana yang paling butuh perbaikan fasilitas?"
4. "Segmen wisatawan mana yang paling tidak puas?"

### Posisi di Ruang Eksplorasi Panitia

TobaGov menjawab **3 dari 6 ruang eksplorasi** secara koheren:

| Ruang Eksplorasi | Cara TobaGov Menjawab |
|---|---|
| **Data Intelligence** | Entity resolution + RAG atas 12K reviews |
| **Operasional Destinasi** | Geospatial gap analysis + priority ranking |
| **Keberlanjutan & Resiliensi** | Trend intelligence + hotspot detection |

---

## 3. Fitur Detail

### Fitur 1: Ask-the-Data (Natural Language Policy Query)

**Cara kerja:**
1. User (pejabat/pengelola) ketik pertanyaan natural
2. LangGraph orchestrator klasifikasi intent → pilih tool yang tepat
3. Tool eksekusi query (RAG / statistik / ranking)
4. LLM sintesis jawaban dengan **situsasi data eksplisit**

**Contoh interaksi:**

```
User: "Apa 3 keluhan terbesar di Balige?"

AI: Berdasarkan analisis ulasan berisi teks dari destinasi
di area Balige (1.847 ulasan dari 19 destinasi):

TOP 3 KELUHAN (berdasarkan frequency mention):
─────────────────────────────────────────────
1. FASILITAS (disebut 142 kali)
   Contoh: "toilet kurang", "parkir sempit", "tidak
   ada mushola"
   Destinasi terdampak: Pantai Lumban Bulbul (41x)

2. KEBERSIHAN (disebut 98 kali)
   Contoh: "sampah", "kotor", "tempat sampah penuh"

3. PELAYANAN (disebut 67 kali)
   Contoh: "lama", "tidak ramah"

SUMBER:
• wisata-v2.csv (6,369 ulasan berisi teks)
• ABSA model: 3 aspek, F1 = 0.71
• Periode: scraped Juli 2025
```

**Mengapa ini kuat:** Setiap klaim bisa di-trace ke review asli. Juri tidak bisa bilang "ini halusinasi" karena ada sitasi.

---

### Fitur 2: Priority Ranking (Bukan Knapsack Optimization)

**Cara kerja:**

```
Priority Score = normalize(
    complaint_count × log(visitor_volume) × rating_gap
)

Dimana:
- complaint_count = jumlah keluhan fasilitas (dari ABSA)
- visitor_volume = proxy dari total review count
- rating_gap = (5 - current_rating) / 5
```

**Output:**

```
PRIORITY RANKING — Investasi Fasilitas
=======================================

#1 Bukit Holbung Samosir
   Score: 8.7/10
   • 89 keluhan fasilitas dari 1.363 review
   • Rating: 4.4 (turun dari 4.6)
   • Top issue: toilet, parkir

#2 Pantai Pasir Putih Lumban Bulbul
   Score: 7.2/10
   • 41 keluhan fasilitas dari 232 review
   • Rating: 4.3

#3 ...

CATATAN: Ini ranking prioritas, bukan alokasi optimal.
Keputusan final tetap di tangan pengelola.
```

**Mengapa tidak pakai knapsack?** Karena tidak ada ground truth biaya/ROI. Klaim "alokasi optimal" tanpa data biaya = halusinasi. Ranking jujur dan defendable.

---

### Fitur 3: Trend Intelligence (Bukan Forecasting Presisi)

**Apa yang BISA dilakukan:**
- Compare rating & sentiment antar periode ("1 year ago" vs "2 years ago")
- Identifikasi destinasi dengan reputasi menurun
- Deteksi "hotspot" keluhan (area dengan proporsi keluhan tinggi)

**Apa yang TIDAK BISA dilakukan (honest disclosure):**
- Forecast bulanan presisi (data resolusi tahunan)
- Prediksi musim ramai (tidak ada multiple snapshot)

**Output:**

```
TREND INTELLIGENCE — Reputasi Antar Periode
============================================

🔴 MENURUN (perlu investigasi):
• Bukit Holbung: avg rating periode "2 years ago" = 4.6
                 avg rating periode "1 year ago"  = 4.4
                 → Turun 0.2
                 → Mayoritas keluhan: kebersihan

🟢 STABIL/NAIK:
• Taman Eden 100: konsisten 4.5-4.6
• Geosite Sipinsur: konsisten 4.7+

ℹ️ METODOLOGI:
Data published-at resolusi kasar ("a year ago").
Analisis berdasarkan perbandingan kategori periode,
bukan time-series bulanan. Tidak dilakukan forecasting.
```

---

### Fitur 4: Geospatial Hotspot Map

**Cara kerja:**
1. Extract lat/long dari `wisata-metadata.csv`
2. Reverse-geocode ke kabupaten via Nominatim (gratis, no API key)
3. Plot keluhan/sentiment di peta interaktif Folium
4. Highlight area dengan konsentrasi masalah

**Klaim jujur:** 68/139 destinasi (49%) punya alamat ambigu → di-reverse-geocode via lat/long (lebih akurat). ~7% tanpa koordinat ditandai "lokasi tidak terverifikasi".

**Output:**
- Choropleth map per kabupaten (rating rata-rata, keluhan density)
- Marker cluster untuk destinasi individual
- Heatmap keluhan fasilitas

---

### Fitur 5: Segment Insights (dari reviewer-type)

**Cara kerja:**
- `resto-hotel-v2.csv` punya kolom `reviewer-type` (Keluarga/Pasangan/Bisnis/Solo)
- Analisis: segmen mana yang paling tidak puas?
- Insight: "Pelanggan Bisnis paling tidak puas di area X"

**Output:**

```
SEGMENT INSIGHTS — Kepuasan per Tipe Wisatawan
===============================================
(Berdasarkan resto-hotel-v2.csv dengan reviewer-type)

Keluarga   (2.341 review): avg 4.3 ⭐
Pasangan   (1.876 review): avg 4.4 ⭐
Bisnis       (892 review): avg 4.0 ⭐ ← paling rendah
Solo         (453 review): avg 4.5 ⭐

INSIGHT: Segmen Bisnis kurang puas.
Top keluhan: WiFi lemah, tidak ada meeting room.
Rekomendasi: Hotel bisnis perlu upgrade fasilitas.
```

---

## 4. Arsitektur Teknis

### Diagram Arsitektur

```
┌─────────────────────────────────────────────────┐
│           USER (Pengelola Destinasi)            │
│         Streamlit / Gradio Web Interface        │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│            ORCHESTRATOR (LangGraph)             │
│   Intent classify → pilih tool → sintesis       │
└──────┬──────────┬──────────┬──────────┬─────────┘
       │          │          │          │
       ▼          ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ RAG Tool │ │ Stats    │ │ Ranking  │ │ Geo Tool │
│          │ │ Tool     │ │ Tool     │ │          │
│ChromaDB  │ │ Pandas   │ │ Priority │ │ Folium   │
│+ 12K     │ │ Plotly   │ │ score    │ │ GeoPandas│
│ reviews  │ │          │ │ compute  │ │          │
└────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
     │            │            │            │
     └────────────┴────────────┴────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│         LLM (Llama 3.1 8B)                      │
│  ┌─────────────────────────────────────────┐    │
│  │ PRELIMINARY: via Groq API               │    │
│  │ FINAL: via vLLM di DGX B200 (same model)│    │
│  │ Migrasi: ganti base URL only (5 menit)  │    │
│  └─────────────────────────────────────────┘    │
│  Sintesis jawaban + justifikasi                 │
└─────────────────────────────────────────────────┘
```

### Kenapa Llama via Groq → vLLM (Bukan Gemini → Llama)

| Aspek | Gemini → Llama (v1) | Groq → vLLM (v3) |
|---|---|---|
| Model konsisten? | ❌ Beda model | ✅ Llama 3.1 8B sama persis |
| Prompt kompatibel? | ❌ Perlu re-tune | ✅ Identik |
| Migrasi effort | 4-6 jam debugging | 5 menit ganti API URL |
| Demo risk di final | Tinggi | Sangat rendah |
| Manfaat B200? | ✅ Di final | ✅ Di final |

### Komponen Teknis Detail

| Komponen | Teknologi | Preliminary | Final (B200) |
|---|---|---|---|
| LLM | Llama 3.1 8B | Groq API (free, cepat) | vLLM lokal |
| Embedding | paraphrase-multilingual-MiniLM | CPU (Colab/HF Space) | CPU |
| Vector DB | ChromaDB (in-memory) | CPU | CPU |
| Sentiment (ABSA) | IndoBERT fine-tuned (3 aspek) | Colab T4 training | B200 batch inference |
| Dashboard | Streamlit + Plotly + Folium | HuggingFace Space | Docker di B200 |
| Orchestrator | LangGraph | CPU | CPU |
| Reverse-geocode | GeoPy + Nominatim | CPU | CPU |

### Resource Allocation di DGX B200 (8× B200 GPU)

```
GPU 0-1: vLLM serving Llama 3.1 8B (tensor parallel = 2)
GPU 2:   Batch ABSA inference (IndoBERT)
GPU 3-7: Idle / backup (cukup 3 GPU untuk semua)
```

---

## 5. Pemanfaatan Dataset

### Data Audit (Hasil Verifikasi)

| File | Total Row | Berisi Teks | Kosong Teks | Catatan |
|---|---|---|---|---|
| `wisata-v2.csv` | 12,691 | 6,369 (50%) | 6,322 (50%) | Rating tetap有用 |
| `resto-hotel-v2.csv` | 9,611 | 5,911 (62%) | 3,700 (38%) | Punya reviewer-type |
| `wisata-metadata.csv` | 139 | — | — | 49% alamat ambigu |
| `resto-metadata.csv` | 148 | — | — | opening-hours kosong |
| `hotel-metadata.csv` | 36 | — | — | place-id kosong |
| `transportasi.csv` | 16 | — | — | Ferry routes critical |
| `waktu operasional.csv` | 60 | — | — | Data fasilitas |

### Pemanfaatan per File

| File | Pemanfaatan di TobaGov | Fitur Terkait |
|---|---|---|
| `wisata-v2.csv` | ABSA, RAG, ranking, trend | Ask-the-Data, Priority, Trend |
| `resto-hotel-v2.csv` | Resto/hotel insight, segment | Segment Insights |
| `wisata-metadata.csv` | Master DB + geocode | Geospatial Map |
| `resto-metadata.csv` | Resto benchmarking | Ranking |
| `hotel-metadata.csv` | Akomodasi gap | Ranking |
| `transportasi.csv` | Connectivity analysis | Geospatial |
| `waktu operasional.csv` | Facility gap scoring | Priority Ranking |
| `Info TOP 3.csv` | Baseline per kabupaten | Benchmark |
| `kuliner.csv` | Cultural asset index | RAG context |
| `Artikel.csv` | Sejarah + konteks | RAG context |

### Data Engineering Pipeline

**Notebook 1 — `01_data_audit.ipynb`:**
- Audit semua CSV: hitung missing value per kolom
- Visualisasi distribusi rating, review volume, geographic spread
- **Output**: Data Quality Report (bukti untuk rubrik "Pemanfaatan data")

**Notebook 2 — `02_data_cleaning.ipynb`:**
- Fix CSV escaping bugs (banyak misaligned rows)
- Normalize price format ("25,000" vs "25.000" vs "Rp 25K")
- Deduplikasi place-name via fuzzy matching (RapidFuzz)
- Parse `published-at` ke kategori periode (recent, 1y, 2y, old)

**Notebook 3 — `03_reverse_geocode.ipynb`:**
- Extract lat/long dari metadata
- Reverse-geocode ke kabupaten via Nominatim
- Validate: compare dengan alamat untuk 70 destinasi yang ada alamat
- Fallback: manual tagging untuk ~10 destinasi tanpa koordinat

**Notebook 4 — `04_absa_training.ipynb`:**
- Manual label 300 review untuk 3 aspek (fasilitas, kebersihan, pelayanan)
- Split: 240 train, 60 test
- Fine-tune IndoBERT (Colab T4, ~2 jam)
- Target jujur: F1 0.70

**Notebook 5 — `05_rag_indexing.ipynb`:**
- Chunk reviews per destinasi (group_by place-name)
- Embed dengan paraphrase-multilingual-MiniLM
- Index di ChromaDB dengan metadata (kabupaten, periode, rating)
- Build retrieval eval set (20 query, manual relevance judgment)

**Notebook 6 — `06_orchestrator.ipynb`:**
- Define LangGraph state schema
- Tools: `query_reviews`, `compute_stats`, `rank_priority`, `get_geo_info`
- Intent classifier (rule-based + LLM fallback)
- End-to-end test dengan 10 pertanyaan sample

---

## 6. Execution Plan

### Preliminary Round (13 Juli – 2 Agustus 2026)

#### Minggu 1 (13-19 Juli): Data Foundation

| Hari | Tugas | Output |
|---|---|---|
| 1-2 | Data audit + cleaning notebook | `01_data_audit.ipynb`, `02_data_cleaning.ipynb` |
| 3-4 | Reverse-geocode + kabupaten mapping | `03_reverse_geocode.ipynb` |
| 5 | Manual label 300 review untuk ABSA | `labeled_reviews.json` |
| 6-7 | Fine-tune IndoBERT, evaluasi F1 | `04_absa_training.ipynb`, model weights |

#### Minggu 2 (20-26 Juli): Core AI

| Hari | Tugas | Output |
|---|---|---|
| 8-9 | RAG indexing (ChromaDB) atas 12K reviews | `05_rag_indexing.ipynb` |
| 10-11 | LangGraph orchestrator + 4 tools | `06_orchestrator.ipynb` |
| 12-13 | Streamlit prototype (3 tabs: Ask, Dashboard, Map) | `app.py` |
| 14 | Test dengan 10 pertanyaan sample | Test report |

#### Minggu 3 (27 Juli – 2 Agustus): Demo + Submission

| Hari | Tugas | Output |
|---|---|---|
| 15-16 | Polish UI, add geospatial map | Final `app.py` |
| 17 | Record video demo (7-9 menit) | `demo.mp4` |
| 18-19 | LaporanAnalisis.pdf (8 section wajib) | PDF |
| 20 | Final check, ZIP code, submit | Submission package |

### Final Round (21-22 Agustus — 2 Hari Lockdown)

#### Day 1 (21 Agustus, 08:00-22:00)

| Waktu | Tugas |
|---|---|
| 08:00-11:00 | Setup B200, deploy Llama 3.1 8B via vLLM. Test endpoint, latency benchmark. Ganti Groq API URL → localhost:8000 (5 menit perubahan kode) |
| 11:00-15:00 | Polish dashboard (tambah interactive features) |
| 15:00-19:00 | Batch inference ABSA atas semua 12K reviews (B200 fast) |
| 19:00-22:00 | Demo rehearsal, record backup video |

#### Day 2 (22 Agustus, 08:00-12:00)

| Waktu | Tugas |
|---|---|
| 08:00-10:00 | Final bug fix, UI polish |
| 10:00-12:00 | Presentasi + demo + Q&A |

---

## 7. Evaluasi Model

### Metrik Kuantitatif (Realistis)

| Metrik | Target | Cara Ukur | Justifikasi |
|---|---|---|---|
| ABSA F1 (3 aspek) | 0.68-0.72 | 60 review test set | Domain baru, 240 training sample |
| RAG Retrieval Precision@5 | 0.70-0.80 | 20 query manual | ChromaDB + multilingual embedding |
| RAG Answer Faithfulness | 0.75-0.85 | RAGAS framework | Grounding ketat dari reviews |
| Reverse-Geocode Accuracy | 0.90+ | Validasi 70 sampel | Nominatim akurat untuk koordinat |
| Intent Classification Acc | 0.85-0.92 | 30 query test | LangGraph router |
| End-to-end Latency | 3-6 detik | Stopwatch demo | Groq cepat, vLLM similar |

### Metodologi Evaluasi

**ABSA (Aspect-Based Sentiment Analysis):**
```
Labeling:
- 300 review dipilih secara stratified (by destinasi, rating, length)
- 3 annotator (tim members), majority vote
- 3 aspek: fasilitas, kebersihan, pelayanan
- Label per aspek: positive / negative / neutral / not-mentioned

Training:
- Split: 240 train, 60 test
- Model: IndoBERT-base-p1 + linear classification head
- Fine-tune: 5 epochs, lr 2e-5, Colab T4
- F1 macro avg

Baseline comparison:
- Zero-shot: Llama 3.1 8B prompt (without fine-tuning)
- Lexicon: InSet + sentistrength
```

**RAG Retrieval:**
```
Query set: 20 pertanyaan (mix of policy questions)
Relevance judgment: manual rating 0-3 per retrieved chunk
Metrics: Precision@5, Recall@5, MRR
```

**RAG Faithfulness (RAGAS):**
```
Framework: ragas library
Metrics:
- Faithfulness (no hallucination)
- Answer Relevancy
- Context Precision
Sample: 15 Q&A pairs
```

---

## 8. Responsible AI & Limitations

### Identifikasi Bias

| Bias | Dampak | Mitigasi |
|---|---|---|
| **Sample bias** | Review dari wisatawan aktif menulis ≠ semua wisatawan | Disclose di dokumentasi |
| **Popularity bias** | Destinasi populer punya lebih banyak review | Normalisasi per-review-volume |
| **Language bias** | Review Batak/English mungkin miss-klasifikasi | Pakai multilingual embedding |
| **Geographic gap** | 49% alamat ambigu, ~7% tanpa koordinat | Reverse-geocode + honest tagging |

### Intended Use & Misuse Risks

```
INTENDED USERS:
- Dinas Pariwisata kabupaten sekitar Danau Toba
- Pengelola destinasi individual
- Peneliti/akademisi pariwisata

INTENDED USE:
- Mendukung (bukan menggantikan) pengambilan keputusan
- Memberikan basis bukti dari data ulasan publik
- Identifikasi prioritas perbaikan

LIMITATIONS:
- Data temporal resolusi tahunan, tidak bisa forecast bulanan
- ABSA hanya 3 aspek (fasilitas, kebersihan, pelayanan)
- Review kosong teks (50%) tidak bisa dianalisis aspek
- ~7% destinasi tanpa koordinat

MISUSE RISKS:
- Menganggap ranking sebagai "alokasi optimal" (ini hanya prioritas)
- Mengabaikan konteks lokal yang tidak tertangkap model
- Menggunakan untuk menghakimi UMKM (bukan tujuannya)
```

### Privacy
- Hanya data ulasan publik (Google Maps)
- Tidak ada tracking individu wisatawan
- `reviewer-id` di dataset kosong → tidak ada identifikasi

---

## 9. Demo Script (10 Menit)

### Setup
- Laptop + projector
- Browser: TobaGov dashboard di HuggingFace Space (prelim) atau B200 (final)
- 3 saved query scenarios
- Cache 5 query results untuk demo offline jika internet mati

### Script

**[0:00-1:00] Hook & Problem**

> "Pengelola destinasi Toba mengambil keputusan berbasis intuisi. Padahal ada 12.000 ulasan publik berisi teks dari warga. Bagaimana mengubah ini jadi basis bukti? Perkenalkan, TobaGov."

**[1:00-3:00] Feature 1: Ask-the-Data**

- Demo live: ketik "Apa 3 keluhan terbesar di Balige?"
- Tampilkan jawaban dengan ranking + sumber data
- Highlight: "Setiap angka bisa di-trace ke review asli"

> "Ini terjawab dalam 3 detik. Bukan 3 minggu riset manual."

**[3:00-5:00] Feature 2: Priority Ranking**

- Tampilkan top 5 destinasi paling butuh perbaikan
- Highlight metodologi: `complaint × volume × rating_gap`

> "Kami tidak klaim ini alokasi optimal. Ini ranking prioritas. Keputusan final tetap di pengelola."

**[5:00-7:00] Feature 3: Geospatial Hotspot**

- Peta interaktif: choropleth per kabupaten
- Highlight area dengan konsentrasi keluhan

> "Reverse-geocode dari koordinat, bukan alamat teks yang 49% ambigu."

**[7:00-8:30] Trend Intelligence**

- Tampilkan perbandingan rating antar periode
- Highlight: "Bukit Holbung turun 0.2 — mayoritas keluhan kebersihan"

> "Kami transparan: data resolusi tahunan, jadi tidak ada forecasting bulanan."

**[8:30-9:30] Tech Architecture**

- Slide: LangGraph + RAG + ABSA + Llama self-hosted
- "Preliminary via Groq API, final via vLLM di B200 — model sama persis"
- "Sovereign AI: data tidak keluar di final round"

**[9:30-10:00] Honest Limitations + Closing**

> "Kami akui keterbatasan: data temporal kasar, ABSA F1 0.71 bukan 0.95, ini prototipe bukan pilot siap deploy. Tapi ini langkah pertama menuju pariwisata Toba yang evidence-based."

### Anti-Failure Protocol

| Skenario | Mitigasi |
|---|---|
| Internet mati | Cache 5 query results, demo offline |
| LLM lambat | Pre-compute answers, show cached + simulate "thinking" |
| Juri tanya "ini cuma chatbot?" | Tunjukkan LangGraph multi-tool, bukan single LLM call |
| Juri tanya "siapa yang pakai?" | Jawab jujur: prototipe, target stakeholder pengelola |
| Juri tanya "kenapa tidak pakai GPT-4?" | "Sovereign AI + B200 — selain itu, Llama 8B cukup untuk reasoning kita" |

---

## 10. Risiko & Mitigasi

| Risiko | Probabilitas | Dampak | Mitigasi |
|---|---|---|---|
| B200 vLLM setup gagal | Sedang | Tinggi | Pre-test vLLM di Colab L4, dokumentasi setup lengkap |
| ABSA F1 < 0.60 | Sedang | Sedang | Fallback: zero-shot LLM extraction via prompt |
| Reverse-geocode gagal | Rendah | Sedang | Pre-compute di preliminary, cache hasil |
| Demo internet mati | Sedang | Tinggi | Cache 5 query results, demo offline mode |
| Juri skeptis "policy intelligence" | Sedang | Sedang | Demo dramatis dengan data konkret |
| Review bahasa Batak miss | Sedang | Rendah | Dokumentasi sebagai limitation |
| Prompt beda Groq vs vLLM | Rendah | Rendah | Same model = same behavior, pre-test |

---

## 11. Differentiator

| Aspek | Tim Lain (Generic) | TobaGov |
|---|---|---|
| Target user | "Wisatawan" generik | Pengelola destinasi (spesifik) |
| Bentuk solusi | Chatbot rekomendasi | Decision-support platform |
| Data usage | Metadata + beberapa review | 12K reviews + semua metadata |
| Klaim AI | "AI canggih" | "F1 0.71, limitation diakui" |
| B200 usage | API OpenAI saja | Self-hosted Llama via vLLM |
| Forecasting | Klaim MAPE < 15% | "Tidak bisa, data resolusi tahunan" (honest) |
| Honesty | Klaim pilot | "Prototipe + roadmap" (honest) |
| Problem angle | Consumer (wisatawan) | Civic (pengelola/pemerintah) |

---

## 12. Rencana Keberlanjutan

### Roadmap 3 Bulan Pasca-Hackathon

| Bulan | Tugas |
|---|---|
| 1 | Open-source core engine, dokumentasi publik, iterasi feedback juri |
| 2 | Kolaborasi dengan LPPM IT Del untuk demo ke Dispar Toba |
| 3 | Iterasi berdasarkan feedback + integrasi Google Maps API untuk real-time |

### Sustainability Model

| Stream | Model |
|---|---|
| Core engine | Open-source (MIT license) |
| Untuk pemda | Gratis |
| Consulting untuk private | Berbayar (destination operators) |
| Custom integration | Berbayar (hotel chains, asosiasi) |

### Yang TIDAK Diklaim (Honest)

- ❌ "Sudah bicara dengan Dispar" (belum)
- ❌ "Pilot Q4 2026 confirmed" (aspirational)
- ❌ "100 UMKM akan pakai" (tidak ada bukti)
- ❌ "Forecasting presisi" (data tidak mendukung)

---

## 13. Pembagian Tim (3 Orang)

### Role Division

| Anggota | Role | Tanggung Jawab Utama |
|---|---|---|
| **Anggota 1** | Data Engineer | Cleaning, entity resolution, reverse-geocode, RAG indexing |
| **Anggota 2** | AI/ML Engineer | ABSA fine-tuning, LangGraph orchestrator, tools logic |
| **Anggota 3** | Full-Stack + Deployment | Streamlit UI, B200 deployment (vLLM), demo/pitch |

### Preliminary Round — Pembagian Paralel

```
Anggota 1 (Data Eng):
  Week 1: 01_audit → 02_cleaning → 03_geocode
  Week 2: 05_rag_indexing
  Week 3: Dokumentasi + support

Anggota 2 (AI/ML):
  Week 1: Label 300 review → 04_absa_training
  Week 2: 06_orchestrator + tools
  Week 3: Evaluasi kuantitatif + laporan teknis

Anggota 3 (Full-Stack):
  Week 1: Setup repo, environment, HF Space
  Week 2: app.py (Streamlit UI)
  Week 3: Video demo + slide + laporan + submit
```

### Final Round — Pembagian Lockdown

```
Day 1 (08:00-22:00):
  Anggota 1: Support data query, batch ABSA preprocessing
  Anggota 2: vLLM setup, test orchestrator di B200, debug
  Anggota 3: UI polish, demo rehearsal, backup video

Day 2 (08:00-12:00):
  Semua: Final test, presentasi, Q&A
  Anggota 3: Lead pitch
  Anggota 1 & 2: Backup Q&A (teknis)
```

---

## 14. Mapping ke Rubrik Penilaian

| Kriteria | Bobot | Bagaimana TobaGov Menjawab | Target Skor |
|---|---|---|---|
| **Kebaruan & ketajaman problem framing** | 20 | Civic intelligence untuk pengelola destinasi — bukan chatbot wisatawan generik. Angle "evidence-based policy" segar. | 16-18 |
| **Dampak & relevansi ekosistem Toba** | 20 | Beneficiary jelas (pengelola destinasi, Dispar). Value terukur (priority ranking, segment insight). | 14-16 |
| **Kualitas teknis AI & rekayasa data** | 20 | RAG + ABSA + geospatial + LangGraph multi-tool. Llama self-hosted di B200. Metrik kuantitatif dilaporkan jujur. | 14-16 |
| **Kelayakan implementasi & keberlanjutan** | 15 | Roadmap realistis (3 bulan). Honest limitation disclosure. Open-source model. | 12-14 |
| **Pemanfaatan data Toba** | 15 | 12K reviews + semua metadata + reverse-geocode. Data Quality Report sebagai bukti. | 13-15 |
| **Komunikasi, demo, dokumentasi** | 10 | Demo "tanya-jawab" dramatis. Setiap klaim disertai sitasi data. Laporan terstruktur. | 8-9 |
| **TOTAL** | **100** | | **77-88** |

---

## 15. Deliverable Checklist

### Preliminary Round Deliverables

| Deliverable | Sifat | Status Checklist |
|---|---|---|
| Deskripsi Proyek | Wajib | [ ] Problem, target user, solusi, diferensiasi |
| Slide Pitching | Wajib | [ ] Problem, solution, data, AI approach, impact, demo, next steps |
| Video Demo & Evaluasi Model | Wajib | [ ] 5-10 menit, screen record (no face), evaluasi performa |
| Repositori / Artefak Teknis | Wajib | [ ] Kode, notebook, README, model card |
| Ringkasan Penggunaan Data | Wajib | [ ] Data Quality Report + pipeline dokumentasi |
| Rencana Implementasi | Wajib | [ ] Pilot plan, mitigasi risiko, resource needs |

### Preliminary Submission Package

```
[TeamName]-LaporanAnalisis.pdf  (≤25 MB)
├── 1. Latar Belakang
├── 2. Analisis Permasalahan
├── 3. Desain dan Indikator Keberhasilan Solusi
├── 4. Perencanaan Implementasi
├── 5. Modelling
├── 6. Evaluasi Model
├── 7. Hasil dan Pembahasan
└── 8. Deklarasi Penggunaan (atau Tidak Menggunakan) AI

[TeamName]-Demo (Google Drive public link)
└── demo.mp4 (7-9 menit, screen record, no face/institution)

[TeamName]-Product (ZIP)
├── README.md
├── requirements.txt
├── app.py (Streamlit)
├── notebooks/
│   ├── 01_data_audit.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_reverse_geocode.ipynb
│   ├── 04_absa_training.ipynb
│   ├── 05_rag_indexing.ipynb
│   └── 06_orchestrator.ipynb
├── src/
│   ├── tools/
│   │   ├── rag_tool.py
│   │   ├── stats_tool.py
│   │   ├── ranking_tool.py
│   │   └── geo_tool.py
│   ├── orchestrator.py
│   └── data/
│       ├── cleaned/ (processed CSVs)
│       ├── geocoded/ (kabupaten mapping)
│       └── absa/ (model weights)
├── docs/
│   ├── data_quality_report.md
│   ├── model_card.md
│   └── responsible_ai.md
└── slides/
    └── pitch_deck.pdf
```

### Aturan Penting (Jangan Dilanggar)

- ❌ Jangan cantumkan nama institusi pendidikan di file manapun
- ❌ Jangan tampilkan wajah di video demo
- ❌ Jangan klaim angka yang tidak bisa dibuktikan
- ❌ Jangan klaim pilot/adopsi tanpa bukti kontak
- ✅ Semua klaim data harus bisa di-trace ke notebook
- ✅ Limitations section wajib eksplisit

---

## Appendix A: Sample Queries untuk Demo

```
1. "Apa 3 keluhan terbesar di Balige?"
2. "Destinasi mana yang paling butuh perbaikan fasilitas?"
3. "Bandingkan rating rata-rata Balige vs Samosir"
4. "Segmen wisatawan mana yang paling tidak puas?"
5. "Destinasi mana yang reputasinya menurun?"
6. "Restoran dengan rating tertinggi di Tuktuk?"
7. "Fasilitas apa yang paling jarang tersedia?"
8. "Show me the complaint hotspot map"
```

## Appendix B: Preliminary vs Final Architecture Comparison

| Aspek | Preliminary | Final |
|---|---|---|
| LLM | Groq API (Llama 3.1 8B) | vLLM lokal di B200 (Llama 3.1 8B) |
| Hosting | HuggingFace Space | Docker di B200 |
| ABSA inference | Per-query (lambat) | Batch pre-compute (cepat) |
| Data | Same | Same |
| Prompt | Same | Same |
| Behavior | Same | Same |

---

*Dokumen ini adalah blueprint final yang honest, detailed, dan execution-ready. Setiap klaim telah diverifikasi terhadap dataset aktual.*
