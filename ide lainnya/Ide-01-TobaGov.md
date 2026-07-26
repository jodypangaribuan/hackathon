# TobaGov.ai — Tourism Policy Intelligence Platform

> **Tagline:** *"Bayangkan Bupati Toba bisa bertanya ke AI tentang kondisi pariwisata — dan mendapat jawaban berbasis 27.000 ulasan warga."*

---

## 1. Ringkasan Eksekutif

**TobaGov.ai** adalah platform *decision-support intelligence* berbasis AI untuk pemerintah daerah, Dinas Pariwisata, dan pengelola destinasi di kawasan Danau Toba. Bukan dashboard statis, bukan chatbot wisatawan — melainkan **asisten analitik yang menjawab pertanyaan kebijakan dalam bahasa natural**, membaca 27K ulasan + 139 destinasi + 148 restoran, lalu memberikan rekomendasi berbasis bukti.

### Posisi di Rubrik Penilaian

| Kriteria | Bobot | Target Skor | Strategi |
|---|---|---|---|
| Kebaruan problem framing | 20 | 18-20 | Civic tech untuk pemerintah daerah = hampir tidak ada yang doing this |
| Dampak & relevansi | 20 | 18-20 | Beneficiary jelas: Dispar Toba, Bupati, pengelola destinasi |
| Kualitas teknis | 20 | 16-18 | RAG + LLM + forecasting + geospatial dalam satu arsitektur |
| Kelayakan implementasi | 15 | 13-15 | Pilot langsung di Dispar Toba — real stakeholder |
| Pemanfaatan data | 15 | 14-15 | 27K reviews + 139 wisata + 148 resto + transport + TOP 3 |
| Komunikasi & demo | 10 | 8-10 | Demo: "tanya AI soal anggaran 2027" |
| **TOTAL** | **100** | **87-98** | |

---

## 2. Problem Framing

### Masalah Utama
Pengambil keputusan di kawasan Danau Toba (Dinas Pariwisata, Bappeda, pengelola kawasan) saat ini membuat keputusan berbasis:
- **Intuisi** dan pengalaman pribadi
- **Laporan manual** yang lambat dan tidak real-time
- **Data terpisah-pisah** (rating di Google Maps, ulasan di travel apps, fasilitas di lapangan)

Padahal, ada **27.000+ ulasan warga** yang mengandung insight berharga tentang: fasilitas apa yang kurang, destinasi mana yang perlu investasi, tren kunjungan, keluhan utama, persebaran kualitas layanan.

### Urgensi
Kawasan Danau Toba adalah **5 Super Prioritas Destinasi Pariwisata** pemerintah. Miliaran rupiah diinvestasikan tanpa tools analitik modern untuk mengukur ROI dan deteksi masalah dini.

### Pertanyaan Kunci yang Ingin Dijawab Sistem
1. "Destinasi mana yang paling mendesak perlu perbaikan fasilitas?"
2. "Bagaimana tren kunjungan Balige vs Samosir 12 bulan terakhir?"
3. "Jika anggaran Rp 5 Miliar untuk 2027, prioritas alokasi apa?"
4. "Kabupaten mana yang underperforming dibanding potensinya?"
5. "Keluhan apa yang paling sering muncul di area Tuktuk?"

---

## 3. Fitur Detail

### Fitur 1: Ask-the-Data (Natural Language Policy Query)

**Cara kerja:**
- User (pejabat Dispar) ketik pertanyaan natural
- LLM memahami intent → pilih tool yang tepat (retrieval / analitik / forecasting)
- Sistem eksekusi query → LLM sintesis jawaban dengan sitasi data

**Contoh interaksi:**
```
User: "Destinasi mana yang paling banyak dikeluhkan fasilitasnya?"

AI: Berdasarkan analisis 27.348 ulasan dari 139 destinasi:

TOP 5 DESTINASI DENGAN KELUHAN FASILITAS TERBANYAK:
1. Bukit Holbung Samosir (1.363 review, 89 keluhan fasilitas)
   — Masalah utama: toilet kurang, area parkir terbatas
2. Pantai Pasir Putih Lumban Bulbul (232 review, 41 keluhan)
   — Masalah utama: sampah,缺乏 mushola
3. ...

REKOMENDASI: Prioritas investasi fasilitas 2027 — toilet & parkir
di 3 destinasi atas dapat berdampak pada ~6.000 wisatawan/bulan.

[Sumber: wisata-v2.csv, 27.348 ulasan, analisis ABSA IndoBERT]
```

### Fitur 2: Budget Allocation Recommender

**Cara kerja:**
- User input: anggaran + periode + prioritas (infrastruktur / marketing / training)
- AI analisis gap antar destinasi → optimasi alokasi
- Output: breakdown anggaran + justifikasi per item

**Logika:**
- Skor kebutuhan = (keluhan count) × (rating impact) × (visitor volume)
- Optimasi: max coverage dengan budget terbatas (knapsack problem)
- LLM narasikan menjadi proposal siap presentasi

### Fitur 3: Comparative Intelligence Dashboard

**Cara kerja:**
- Auto-benchmark antar 8 kabupaten (Toba, Samosir, Simalungun, Tapanuli Utara, Humbang Hasundutan, Dairi, Karo, Pakpak Bharat)
- Metrik: avg rating, review volume, sentiment trend, facility completeness
- Visualisasi: choropleth map, radar chart, trend line

**Insight auto-generated:**
- "Kabupaten Toba avg rating 4.3, tapi review volume turun 15% YoY"
- "Samosir leading di volume review tapi score fasilitas terendah"

### Fitur 4: Forecasting & Trend Analysis

**Cara kerja:**
- Parse timestamp dari 27K reviews (relative dates → absolute via `scraped-at-date`)
- Agregasi per bulan → time-series
- Forecast 3-6 bulan ke depan (Prophet / ARIMA)
- Deteksi anomali (Prophet changepoints / Isolation Forest)

**Output:**
- Trend line per destinasi
- Early warning: "Rating Bukit X diprediksi turun, investigate"

### Fitur 5: Executive Brief Generator

**Cara kerja:**
- Setiap minggu, AI generate 1-halaman executive brief otomatis
- Isi: top 3 insight, top 3 risk, top 3 rekomendasi
- Dikirim via email/WhatsApp ke pejabat terkait

---

## 4. Arsitektur Teknis

```
┌─────────────────────────────────────────────────┐
│              USER (Pejabat Dispar)              │
│         Streamlit Web Interface (Gradio)         │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│            ORCHESTRATOR (LangGraph)             │
│   Parse intent → pilih tool → sintesis jawaban  │
└──────┬──────────┬──────────┬──────────┬─────────┘
       │          │          │          │
       ▼          ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ RAG Tool │ │Analytics │ │Forecast  │ │ Geospatial│
│          │ │  Tool    │ │  Tool    │ │   Tool   │
│ChromaDB  │ │ Pandas   │ │ Prophet  │ │ Folium   │
│+ reviews │ │ Plotly   │ │ ARIMA    │ │ GeoJSON  │
│+ desc    │ │          │ │          │ │          │
└──────┬───┘ └──────┬───┘ └──────┬───┘ └──────┬───┘
       │            │            │            │
       └────────────┴────────────┴────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│           LLM REASONING (Llama 3.1 8B)          │
│      Self-hosted di DGX B200 (vLLM)             │
│      Sintesis jawaban + justifikasi             │
└─────────────────────────────────────────────────┘
```

### Komponen Teknis

| Komponen | Teknologi | GPU Need |
|---|---|---|
| LLM Inference | Llama 3.1 8B via vLLM | 1× B200 |
| Embedding | `paraphrase-multilingual-MiniLM` (CPU) | — |
| Vector DB | ChromaDB (in-memory) | — |
| Sentiment | IndoBERT fine-tuned (prelim) | Colab T4 |
| Forecasting | Prophet / statsmodels | CPU |
| Dashboard | Streamlit + Plotly + Folium | CPU |
| Orchestrator | LangGraph (Python) | CPU |

---

## 5. Pemanfaatan Dataset (Detail per File)

| File Dataset | Pemanfaatan | Fitur Terkait |
|---|---|---|
| `wisata-v2.csv` (14K reviews) | Sentiment analysis, trend forecasting, complaint extraction | Ask-the-Data, Forecasting |
| `resto-hotel-v2.csv` (12K reviews) | UMKM quality benchmarking | Comparative Intelligence |
| `wisata-metadata.csv` (139) | Master place DB, geo, ratings | All features |
| `resto-metadata.csv` (148) | Resto benchmarking | Comparative |
| `hotel-metadata.csv` (36) | Hotel gap analysis | Budget Recommender |
| `transportasi.csv` (16 routes) | Connectivity analysis between regions | Geospatial |
| `waktu operasional.csv` (60) | Facility completeness scoring | Budget Recommender |
| `Info Seputar TOP 3.csv` | Baseline benchmark per kabupaten | Comparative |
| `kuliner.csv` (10) | Cultural asset inventory | Brief Generator |
| `Artikel.csv` (6) | Context for LLM grounding | Ask-the-Data |

### Data Engineering Pipeline
1. **Cleaning** — fix CSV escaping bugs, normalize price format, dedupe
2. **Entity Resolution** — match place names across v1/v2/metadata
3. **Date Parsing** — "a year ago" + `scraped-at-date` → absolute timestamp
4. **Geocoding** — extract lat/long from metadata, fallback to address parsing
5. **Sentiment Scoring** — IndoBERT ABSA: 6 aspects (fasilitas, harga, kebersihan, akses, pelayanan, makanan)
6. **Indexing** — ChromaDB untuk RAG, separate collection per kategori

---

## 6. Execution Plan

### Preliminary Round (13 Juli – 2 Agustus 2026)

**Minggu 1 (13-19 Juli): Foundation**
- [ ] Notebook 1: Data cleaning & EDA (`01_data_pipeline.ipynb`)
  - Parse semua CSV, fix escaping, normalize
  - Visualisasi distribusi rating, review volume per kabupaten
- [ ] Notebook 2: Sentiment model (`02_absa_indobert.ipynb`)
  - Fine-tune IndoBERT untuk 6 aspect classes
  - Labeling: 500 review manual → train, 100 → test
  - Target: F1 > 0.80
- [ ] Notebook 3: Date parsing & forecasting prototype
  - Parse relative dates, aggregate monthly, plot trend

**Minggu 2 (20-26 Juli): Core AI**
- [ ] Notebook 4: RAG system (`04_rag_pipeline.ipynb`)
  - Index reviews + descriptions di ChromaDB
  - Retrieval evaluation: precision@5
- [ ] Notebook 5: LangGraph orchestrator (`05_orchestrator.py`)
  - Define tools: `query_reviews`, `compute_stats`, `forecast_trend`
  - Router: klasifikasi intent → pilih tool
- [ ] Integrasi LLM API (Gemini 2.5 Flash — free tier untuk preliminary)

**Minggu 3 (27 Juli – 2 Agustus): Demo + Submission**
- [ ] Streamlit prototype (`app.py`)
  - 3 tabs: Ask-the-Data, Dashboard, Forecast
- [ ] Video demo 7-9 menit
  - Screen record, no face, no institution name
- [ ] LaporanAnalisis.pdf (struktur 8 section wajib)
- [ ] Source code .ZIP dengan README

### Final Round (21-22 Agustus — Lockdown 2 hari)

**Day 1 (21 Agustus, 08:00-22:00):**
- Pagi: Setup B200, deploy Llama 3.1 8B via vLLM
- Siang: Migrasi orchestrator dari API Gemini → Llama lokal
- Sore: Polish dashboard, add Budget Recommender logic
- Malam: Integrasi forecasting, test end-to-end

**Day 2 (22 Agustus, 08:00-12:00):**
- Pagi: Final testing, bug fix, demo rehearsal
- Siang: Presentasi + demo (10 menit) + Q&A (10 menit)

---

## 7. Evaluasi Model (Angka Kuantitatif)

### Wajib untuk Rubrik Teknis (20 poin)

| Metrik | Target | Cara Ukur |
|---|---|---|
| ABSA F1 Score | ≥ 0.80 | Test set 100 labeled reviews |
| ABSA Accuracy | ≥ 0.85 | Per-aspect classification |
| RAG Retrieval Precision@5 | ≥ 0.75 | Manual eval 20 queries |
| RAG Answer Faithfulness | ≥ 0.80 | RAGAS framework |
| Forecasting MAPE | < 15% | Train/test split time-series |
| Intent Classification Acc | ≥ 0.90 | 50 query test |
| End-to-end Latency | < 5 detik | Stopwatch demo |
| Budget Allocation Coverage | ≥ 80% | Manual check vs expert |

---

## 8. Demo Script (10 Menit)

### Setup
- Laptop connected to projector
- Browser open: TobaGov.ai dashboard
- Prepare 3 saved scenarios

### Script

**[0:00-1:00] Hook & Problem**
> "Pak/Bbu juri, bayangkan Bupati Toba mau alokasi Rp 5 Miliar untuk pariwisata 2027. Saat ini, keputusan berbasis intuisi dan laporan manual yang lambat. Padahal ada 27.000 ulasan warga yang bisa jadi basis keputusan."

**[1:00-3:00] Feature 1: Ask-the-Data**
- Demo: ketik "Destinasi mana yang paling banyak dikeluhkan fasilitasnya?"
- Tampilkan: AI jawab dengan ranking + sumber data + rekomendasi
- "Ini terjawab dalam 3 detik, bukan 3 minggu riset manual."

**[3:00-5:00] Feature 2: Budget Recommender**
- Input: Rp 5 Miliar, prioritas fasilitas
- Output: breakdown alokasi 7 destinasi + justifikasi
- "AI tidak menggantikan keputusan, tapi memberikan basis bukti."

**[5:00-7:00] Feature 3: Dashboard + Forecasting**
- Tunjukkan choropleth map per kabupaten
- Trend line: "Perhatikan Samosir naik, Toba turun"
- Forecast 3 bulan ke depan dengan confidence interval

**[7:00-9:00] Technical Architecture**
- Slide arsitektur: RAG + LLM + Forecasting
- "Semua berjalan di DGX B200 IT Del — sovereign AI, data tidak keluar."
- Tunjukkan angka evaluasi: F1 0.85, RAGAS 0.82

**[9:00-10:00] Impact & Closing**
- "Sedang kami bicara dengan Dispar Toba untuk pilot Q4 2026."
- "Bukan masa depan pariwisata Toba — ini tools yang dibutuhkan hari ini."

---

## 9. Risiko & Mitigasi

| Risiko | Probabilitas | Dampak | Mitigasi |
|---|---|---|---|
| B200 gagal deploy | Rendah | Tinggi | Pre-test vLLM setup di Colab, siap fallback Gemini API |
| Demo internet mati | Sedang | Tinggi | Cache hasil query, demo offline mode |
| LLM halusinasi | Sedang | Sedang | RAG grounding wajib, tampilkan sitasi |
| Sentiment model underperform | Rendah | Sedang | Fallback ke VADER + lexicon Batak-aware |
| Juri tanya "ini cuma chatbot?" | Sedang | Rendah | Siap jawaban: "ini agent dgn tools, bukan chatbot" — show LangGraph |

---

## 10. Differentiator vs Tim Lain

| Aspek | Tim Lain (Generic) | TobaGov.ai |
|---|---|---|
| Target user | "Wisatawan" generik | Dinas Pariwisata, pejabat daerah |
| Bentuk solusi | Chatbot | Decision-support platform |
| Data usage | Metadata saja | 27K reviews + semua dataset |
| Demo angle | "Tanya rekomendasi wisata" | "Tanya kebijakan anggaran" |
| AI value | LLM wrapper | RAG + forecasting + optimization |
| B200 usage | API OpenAI saja | Self-hosted sovereign LLM |

---

## 11. Rencana Keberlanjutan

### Pilot Plan (Q4 2026)
- Kolaborasi dengan LPPM IT Del → Dispar Toba
- Deploy di server IT Del, akses untuk 5 pejabat kunci
- Metric sukses: 50 query/pekan, 3 keputusan terdokumentasi menggunakan sistem

### Roadmap 6 Bulan
- Bulan 1-2: Integrasi data real-time (Google Maps API)
- Bulan 3-4: Mobile-responsive dashboard
- Bulan 5-6: Multi-kabupaten rollout (Samosir, Simalungun)

### Sustainability Angle (untuk Rubrik Keberlanjutan 15 poin)
- Open-source core, customization per daerah
- Training lokal untuk staf Dispar (knowledge transfer)
- Skema revenue: subscription untuk pemda kabupaten lain di Indonesia
