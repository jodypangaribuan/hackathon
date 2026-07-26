# TobaRescue — Tourism Crisis & Quality Monitor

> **Tagline:** *"Deteksi krisis pariwisata sebelum rating jatuh. Early warning system untuk pengelola destinasi Danau Toba."*

---

## 1. Ringkasan Eksekutif

**TobaRescue** adalah sistem monitoring real-time dan early warning untuk kesehatan destinasi pariwisata Toba. Sistem menganalisis 27K+ ulasan dengan timestamp, mendeteksi **anomali** (rating drop, keluhan melonjak), lalu menghasilkan **crisis playbook** otomatis via LLM — action plan spesifik untuk merespon penurunan kualitas sebelum jadi krisis public.

### Posisi di Rubrik

| Kriteria | Bobot | Target | Strategi |
|---|---|---|---|
| Kebaruan | 20 | 15-17 | Operational monitoring angle — fresh |
| Dampak | 20 | 16-18 | Operational value untuk pengelola destinasi |
| Teknis | 20 | 16-18 | Time-series + anomaly detection + LLM playbook |
| Kelayakan | 15 | 14-15 | Pilot dengan pengelola destinasi |
| Data | 15 | 14-15 | Pakai timestamp reviews (jarang dieksplor!) |
| Komunikasi | 10 | 8-10 | Demo alert system dramatis |
| **TOTAL** | **100** | **83-93** | |

---

## 2. Problem Framing

### Masalah Utama
Pengelola destinasi Toba **reaktif**, bukan proaktif. Mereka baru tahu ada masalah ketika:
- Rating sudah turun signifikan
- Ulasan negatif sudah viral di media sosial
- Wisatawan sudah berhenti datang

Tidak ada sistem yang mengalert: *"Bukit Holbung mulai banyak keluhan sampah minggu ini — investigate sebelum parah"*.

### Urgensi
- 27K reviews punya timestamp → pola temporal bisa diekstrak
- Penurunan rating = penurunan kunjungan = kerugian ekonomi
- Early detection = intervensi cepat = hemat biaya

### Insight Kunci
- Reviews tersebar dalam beberapa tahun → pola musim terlihat
- `reviewer-type` memungkinkan segmentasi anomaly (e.g., keluhan bisnis traveler naik 200%)
- Fasilitas metadata → korelasi keluhan dengan gap fasilitas

---

## 3. Fitur Detail

### Fitur 1: Real-time Sentiment Monitor

**Dashboard per destinasi:**
```
DESTINASI: Bukit Holbung Samosir
===============================
Rating Trend: 4.6 → 4.4 (3 bulan) ⚠
Review Volume: 1.363 total, ~45/bulan

SENTIMENT TIMELINE (12 bulan):
[graph showing positive/negative trend]

ASPECT BREAKDOWN (30 hari):
✓ Pemandangan: 92% positive
✓ Akses: 65% positive
⚠ Kebersihan: 38% positive ← TURUN 40%!
⚠ Fasilitas: 45% positive
```

### Fitur 2: Anomaly Detector

**Algoritma:**
- Time-series per destinasi + per aspect
- Isolation Forest untuk detect outlier
- Prophet untuk forecast baseline + residual analysis
- Alert threshold: deviasi > 2σ dari baseline

**Alert types:**
- 🔴 **CRITICAL**: Rating drop > 0.5 dalam 30 hari
- 🟡 **WARNING**: Aspect sentiment drop > 30%
- 🔵 **INFO**: Volume review spike (potential viral issue)

**Contoh alert:**
```
🔴 ALERT: Bukit Holbung
Aspect: Kebersihan
Drop: 70% → 38% positive (60 hari)
Trigger: Isolation Forest anomaly score 0.92
Top complaints: "sampah", "kotor", "tempat sampah penuh"
Recommended action: koordinasi DLH, audit jadwal cleaning
Confidence: HIGH (40 data points)
```

### Fitur 3: Crisis Playbook Generator

**Cara kerja:**
LLM analisis alert + retrieve review relevan → generate action plan:

```
PLAYBOOK: Krisis Kebersihan Bukit Holbung
=========================================

SITUASI:
- 3 bulan terakhir, 58 keluhan "sampah" dari 142 review
- Rating turun dari 4.6 → 4.4
- Penurunan terkonsentrasi di weekend (high traffic)

ANALYSIS ROOT CAUSE:
- Kapasitas tempat sampah tidak match dengan visitor weekend
- Jadwal cleaning 1x/hari, butuh 3x/hari di weekend
- Tidak ada relawan/TKN yang assigned

ACTION PLAN (Prioritas):

🔴 IMMEDIATE (1 minggu):
1. Audit kapasitas tempat sampah existing
2. Tambah 10 tempat sampah di area集中
3. Jadwal cleaning: 3x/hari weekend

🟡 SHORT-TERM (1 bulan):
4. Koordinasi dengan DLH Toba for waste pickup
5. Rekrut 2 petugas kebersihan weekend
6. Pasang signage "Jaga Kebersihan" multibahasa

🟢 LONG-TERM (3 bulan):
7. Program "Adopsi Destinasi" dengan korporat
8. Sistem reward untuk visitor yang bawa sampah balik
9. Edukasi via TikTok/IG dengan influencer lokal

KPI SUCCESS:
- Sentiment kebersihan > 70% dalam 60 hari
- Rating > 4.5 dalam 90 hari
```

### Fitur 4: Predictive Forecasting

**Cara kerja:**
- Prophet model per destinasi
- Forecast 3-6 bulan dengan confidence interval
- Identify seasonality (lebaran, semester break, year-end)
- Early warning: "Rating diprediksi turun di Q4 — intervene now"

### Fitur 5: Cross-Destination Benchmarking

**Cara kerja:**
- Compare anomaly patterns across destinations
- Identify systemic issues (e.g., semua destinasi punya keluhan toilet)
- Highlight outlier (destinasi dengan rating stabil → best practice)

---

## 4. Arsitektur Teknis

```
┌──────────────────────────────────────────────┐
│         DASHBOARD (Streamlit + Plotly)        │
└────────────────────┬─────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│  Alert   │  │ Forecast │  │ Playbook │
│  Engine  │  │  Engine  │  │ Generator│
│(Isolation│  │(Prophet) │  │  (LLM)   │
│ Forest)  │  │          │  │          │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │
     └─────────────┴─────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│       TIME-SERIES DATA LAYER                  │
│  • Review timestamps (parsed from relative)  │
│  • Aspect sentiment scores (IndoBERT ABSA)   │
│  • Monthly aggregations per destinasi        │
└──────────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│  LLM (Llama 3.1 8B di B200)                  │
│  Playbook generation + insight narration     │
└──────────────────────────────────────────────┘
```

### Tech Stack

| Komponen | Teknologi |
|---|---|
| Anomaly Detection | scikit-learn Isolation Forest |
| Forecasting | Prophet / NeuralProphet |
| Sentiment | IndoBERT fine-tuned |
| LLM | Llama 3.1 8B via vLLM |
| Dashboard | Streamlit + Plotly |
| Alerting | Custom threshold + scheduling |

---

## 5. Pemanfaatan Dataset

| File | Pemanfaatan |
|---|---|
| `wisata-v2.csv` (14K) | **Core**: timestamp + sentiment per destinasi |
| `resto-hotel-v2.csv` (12K) | Resto/hotel monitoring |
| `wisata-metadata.csv` | Destinasi profile |
| `waktu operasional.csv` | Facility context untuk playbook |
| `Info TOP 3.csv` | Benchmark per kabupaten |
| `transportasi.csv` | Ferry disruption impact analysis |

### Critical Data Engineering
**Date Parsing Pipeline:**
1. `published-at`: "a year ago", "5 months ago", "3 weeks ago"
2. `scraped-at-date`: ~28-29 Juli 2025
3. Compute: absolute date = scraped - relative
4. Aggregate: monthly buckets per destinasi
5. Quality check: jika data < 12 bulan, label sebagai short series

---

## 6. Execution Plan

### Preliminary Round

**Minggu 1: Data + Time-Series**
- [ ] Parse relative dates ke absolute
- [ ] Build monthly time-series per destinasi
- [ ] EDA: seasonality patterns, trend analysis
- [ ] Notebook 1: data pipeline + EDA

**Minggu 2: Anomaly + Forecasting**
- [ ] IndoBERT ABSA fine-tune (6 aspects)
- [ ] Isolation Forest training per destinasi
- [ ] Prophet forecasting baseline
- [ ] Notebook 2: anomaly detection + forecasting

**Minggu 3: Playbook + Demo**
- [ ] LLM playbook generation (Gemini API)
- [ ] Streamlit dashboard
- [ ] Video demo: alert scenario dramatis
- [ ] Submission

### Final Round (2 hari)

**Day 1:**
- Deploy Llama 3.1 8B di B200
- Polish dashboard dengan alert UI
- Add cross-destination benchmarking

**Day 2:**
- Final test, presentasi

---

## 7. Evaluasi Model

| Metrik | Target | Metode |
|---|---|---|
| ABSA F1 | ≥ 0.80 | Test set |
| Anomaly Detection Precision | ≥ 0.70 | Synthetic injected anomalies |
| Anomaly Detection Recall | ≥ 0.80 | Same |
| Forecast MAPE | < 15% | Train/test split |
| Playbook Actionability | ≥ 4/5 | Manual rating oleh operator destinasi |
| Alert Latency | < 1 detik | Real-time test |

---

## 8. Demo Script

### Setup
- Pre-load 3 scenario: 1 krisis aktif, 1 early warning, 1 success story

### Script

**[0:00-1:30] Hook**
> "Pak Joko, pengelola Bukit Holbung, bangun pagi. Rating 4.4. Turun dari 4.6 bulan lalu. Dia tidak tahu kenapa. Tiga bulan kemudian, tamu berkurang 30%. Kalau saja ada peringatan dini..."

**[1:30-3:30] Dashboard Tour**
- Buka dashboard TobaRescue
- Tampilkan heatmap 139 destinasi
- Highlight 3 dengan alert aktif (merah)

**[3:30-5:30] Deep Dive Anomaly**
- Klik Bukit Holbung
- Tampilkan sentiment timeline
- Reveal anomaly: "Kebersihan drop 70% dalam 60 hari"
- Top complaints word cloud: "sampah", "kotor"

**[5:30-7:30] Crisis Playbook**
- Klik "Generate Action Plan"
- LLM produce playbook (immediate, short, long-term)
- "Dalam 3 detik, pengelola dapat roadmap konkret"

**[7:30-9:00] Forecasting**
- Tampilkan Prophet forecast
- "Jika tidak intervene, rating akan 4.1 dalam 3 bulan"
- What-if: setelah playbook → rating recover ke 4.5

**[9:00-10:00] Scale + Tech**
- "27K reviews punya timestamp — ini aset yang jarang dieksplor tim lain"
- "Anomaly detection + Prophet + LLM — all in B200"

---

## 9. Risiko & Mitigasi

| Risiko | Mitigasi |
|---|---|
| Date parsing tidak akurat | Manual validate 100 samples |
| Time series terlalu pendek | Fokus destinasi dengan > 500 review |
| False positive alert | Tuning threshold, manual review |
| Playbook generik | Few-shot dengan playbook example spesifik |
| Demo tidak dramatis | Pre-script alert scenario |

---

## 10. Differentiator

| Generic | TobaRescue |
|---|---|
| Dashboard reaktif | Predictive + early warning |
| Insight statis | Alert otomatis |
| Manual analysis | Anomaly detection ML |
| Report bulanan | Playbook real-time |

---

## 11. Rencana Keberlanjutan

### Pilot Plan
- 5 destinasi prioritas (Bukit Holbung, Pantai Lumban Bulbul, Taman Eden, dll)
- Daily monitoring, weekly report ke pengelola
- Metric: detection lead time (berapa hari sebelum rating drop)

### Scale
- Integrasi Google Maps API untuk real-time review scraping
- Expand ke seluruh 5to Destinasi Prioritas
- SaaS untuk asosiasi pengelola destinasi
