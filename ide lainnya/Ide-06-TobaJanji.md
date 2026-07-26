# TobaJanji — Responsible Tourism Scorecard

> **Tagline:** *"Sebelum berkembang, ukur dulu: apakah pariwisata Toba berkelanjutan, inklusif, dan adil? AI yang mengaudit pariwisata dengan kacamata etika."*

---

## 1. Ringkasan Eksekutif

**TobaJanji** adalah platform ** Responsible AI governance** untuk pariwisata Toba — mengaudit dan menilai destinasi dari aspek keberlanjutan, inklusi, pemerataan ekonomi, dan potensi bias. Bukan analytics dashboard biasa, tapi **scorecard etis** yang membantu pengambil keputusan membangun pariwisata yang bertanggung jawab.

### Mengapa Ini 2026
- **USAII Hackathon 2026** punya kategori khusus **"Responsible AI Award"**
- Challenge statement IT Del eksplisit menyebut: *"aspek etika, privasi, dan keberlanjutan"*
- ESG/sustainability reporting = tren global 2026
- **Tidak ada tim lain** yang akan fokus governance

### Posisi di Rubrik

| Kriteria | Bobot | Target | Strategi |
|---|---|---|---|
| Kebaruan | 20 | 18-20 | Paling novel — governance angle |
| Dampak | 20 | 15-17 | Long-term value, susah diukur quick win |
| Teknis | 20 | 13-15 | Scoring + LLM reasoning — moderate complexity |
| Kelayakan | 15 | 12-14 | Butuh stakeholder buy-in untuk adoption |
| Data | 15 | 13-15 | Mix semua dataset untuk multi-dimensional score |
| Komunikasi | 10 | 8-10 | Demo: "audit report" format |
| **TOTAL** | **100** | **79-91** | |

---

## 2. Problem Framing

### Masalah Utama
Pengembangan pariwisata Toba fokus pada **pertumbuhan** (jumlah wisatawan, investasi) tanpa mengukur:
- **Keberlanjutan**: apakah budaya lokal terjaga? Lingkungan tidak rusak?
- **Inklusi**: apakah lansia, disabilitas, wisman terlayani?
- **Pemerataan**: apakah ekonomi merata, atau cuma Tuktuk/Balige yang untung?
- **Bias**: apakah UMKM kecil tenggelam karena algoritma rekomendasi bias ke yang populer?

### Urgensi
- Challenge statement eksplisit: *"aspek etika, privasi, dan keberlanjutan"*
- Tren global: ESG reporting, sustainable tourism
- Risiko greenwashing tanpa measurement

### Pertanyaan Kunci
1. "Seberapa inklusif pariwisata Toba untuk lansia & disabilitas?"
2. "Apakah investasi pariwisata merata, atau terkonsentrasi di 3 area?"
3. "UMKM mana yang invisible karena algoritma bias?"
4. "Destinasi mana yang over-tourism vs under-developed?"

---

## 3. Fitur Detail

### Fitur 1: Tourism Sustainability Index (TSI)

**4 pilar scoring per destinasi & per kabupaten:**

```
TOURISM SUSTAINABILITY INDEX
Kabupaten Toba — Q3 2026
==========================

🌐 ECONOMIC SPREAD     : 6.2/10  ⚠
  - 80% review terkonsentrasi di 5 destinasi
  - UMKM pinggiran invisible (review < 10)
  - Rekomendasi: promosi 20 UMKM underexposed

🌍 ENVIRONMENTAL       : 5.5/10  🔴
  - 35% keluhan: sampah, kebersihan
  - Tidak ada data emisi/carbon
  - Rekomendasi: waste management investment

🎭 CULTURAL            : 7.8/10  ✅
  - 23 destinasi budaya well-reviewed
  - 10 kuliner Batak documented
  - Rekomendasi: preserve traditional practice

♿ INCLUSIVITY         : 4.0/10  🔴
  - 15% destinasi punya info fasilitas disabilitas
  - Multibahasa info minim
  - Rekomendasi: audit accessibility 20 destinasi prioritas

OVERALL TSI: 5.9/10 (Moderate)
```

### Fitur 2: Bias Auditor

**Cara kerja:**
- Analisis distribusi review, rating, visibility per destinasi
- Detect: destinasi dengan rating tinggi tapi invisible
- Detect: area geografis underrepresented
- Detect: UMKM yang tertinggal karena tidak punya digital presence

**Output:**
```
BIAS AUDIT REPORT
=================

⚠ VISIBILITY GAP:
20 destinasi dengan rating > 4.5 tapi review < 20.
Likely cause: tidak populer di algoritma Google Maps.
Recommendation: campaign untuk 5 destinasi tertinggi.

⚠ GEOGRAPHIC BIAS:
Kabupaten Pakpak Bharat: hanya 3 destinasi di dataset
(vs 35 di Toba). Underrepresentation data.

⚠ UMKK DIGITAL DIVIDE:
45% resto tidak punya info di GoFood/Grab.
Cause: pemilik tidak tech-savvy.
Recommendation: training program digital literacy.
```

### Fitur 3: Inclusivity Report Card

**Per kabupaten, score:**
- Akses disabilitas (data dari `waktu operasional.csv`)
- Fasilitas keluarga (toilet, parkir, area menyusui)
- Layanan multibahasa (proxy: review dari wisman)
- Akses transportasi (ferry, angkot availability)

### Fitur 4: Cultural Preservation Monitor

**Cara kerja:**
- Track mention tradisi Batak di reviews (ulos, marga, kuliner, upacara)
- Trend: apakah cultural mention naik (good) atau turun (commercialization)
- Identify: tradisi yang hilang dari discourse

### Fitur 5: Fair Tourism Dashboard

**Visualisasi:**
- Choropleth map: pemerataan review/investasi per kabupaten
- Heatmap: destinasi over-tourism vs under-developed
- Network graph: UMKM connectivity

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
│  Scoring │  │   Bias   │  │   LLM    │
│  Engine  │  │  Auditor │  │ Narrator │
│          │  │          │  │          │
│(weighted │  │(statistic│  │ Explain  │
│ formula) │  │ analysis)│  │ scores + │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │
     └─────────────┴─────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│              DATA LAYER                       │
│  • 27K reviews (sentiment + aspect)          │
│  • 139 wisata + 148 resto metadata          │
│  • Fasilitas metadata                        │
│  • Geo distribution                          │
└──────────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│  LLM (Llama 3.1 8B di B200)                  │
│  Narrate scores, generate recommendations    │
└──────────────────────────────────────────────┘
```

### Tech Stack

| Komponen | Teknologi |
|---|---|
| Scoring | Custom weighted formula (Python) |
| Bias Detection | Statistical analysis (scipy, statsmodels) |
| Sentiment | IndoBERT ABSA |
| LLM | Llama 3.1 8B via vLLM |
| Viz | Plotly + Folium + Streamlit |

---

## 5. Pemanfaatan Dataset

| File | Pemanfaatan |
|---|---|
| `wisata-v2.csv` (14K) | Sentiment, visibility analysis |
| `resto-hotel-v2.csv` (12K) | UMKM visibility, bias |
| `wisata-metadata.csv` (139) | Geographic distribution |
| `resto-metadata.csv` (148) | UMKM inventory |
| `hotel-metadata.csv` (36) | Accommodation spread |
| `transportasi.csv` (16) | Accessibility scoring |
| `waktu operasional.csv` (60) | **Critical**: inclusivity data |
| `Info TOP 3.csv` | Benchmark per kabupaten |
| `kuliner.csv` (10) | Cultural preservation metric |

### Scoring Methodology
```
ECONOMIC SPREAD = 1 - Gini(review_volume per destinasi)
ENVIRONMENTAL = 1 - (keluhan_kebersihan_count / total_review)
CULTURAL = (cultural_mention_count / total_review) × preservation_factor
INCLUSIVITY = (destinasi_dengan_fasilitas_disabilitas / total_destinasi) × multibahasa_factor

TSI = w1×ECON + w2×ENV + w3×CULT + w4×INCL
(weights dari expert judgment atau AHP)
```

---

## 6. Execution Plan

### Preliminary Round

**Minggu 1: Data + Scoring**
- [ ] Define scoring formula (4 pilar, sub-metrics)
- [ ] Data pipeline untuk compute scores
- [ ] Compute TSI untuk 8 kabupaten
- [ ] Notebook 1: methodology + scoring

**Minggu 2: Bias + LLM**
- [ ] Statistical bias analysis
- [ ] LLM narrative generation (Gemini API)
- [ ] Build Streamlit dashboard
- [ ] Notebook 2: bias audit + LLM

**Minggu 3: Demo + Submission**
- [ ] Polish dashboard dengan report card format
- [ ] Video demo — show audit report
- [ ] Submission

### Final Round (2 hari)

**Day 1:**
- Deploy Llama 3.1 8B di B200
- Enhance LLM narrative quality
- Add Cultural Preservation Monitor

**Day 2:**
- Demo rehearsal, present

---

## 7. Evaluasi Model

| Metrik | Target | Metode |
|---|---|---|
| Scoring Consistency | 100% | Deterministic formula, reproducible |
| Bias Detection Recall | ≥ 0.75 | Manual identify 20 bias cases |
| LLM Narrative Quality | ≥ 4/5 | Manual rating |
| Report Card Clarity | ≥ 4/5 | User testing 5 orang |
| Stakeholder Acceptance | N/A | Qualitative demo feedback |

---

## 8. Demo Script

### Setup
- Pre-load TSI untuk 8 kabupaten
- Pre-load 1 deep-dive: Kabupaten Toba

### Script

**[0:00-1:30] Hook**
> "Pak/Bbu juri, challenge statement eksplisit menyebut: 'aspek etika, privasi, dan keberlanjutan'. Tapi bagaimana kita mengukurnya? Selama ini, pariwisata Toba dinilai dari jumlah wisatawan. Kami ingin menambah dimensi: apakah berkelanjutan, inklusif, dan adil?"

**[1:30-3:30] TSI Overview**
- Tampilkan map dengan TSI per kabupaten
- "Toba 5.9, Samosir 6.5, Pakpak Bharat 3.2"
- "Pakpak Bharat underperforming — underrepresentation data"

**[3:30-5:30] Deep Dive: Inclusivity**
- Klik pilar Inclusivity
- Reveal: "Hanya 15% destinasi punya info fasilitas disabilitas"
- "Artinya, 85% destinasi Toba potentially inaccessible untuk lansia/kursi roda"

**[5:30-7:00] Bias Auditor**
- Tampilkan 20 destinasi rating tinggi tapi invisible
- "Ini hidden gems, tapi algoritma Google Maps tidak promote"
- "20 UMKM yang harusnya dapat perhatian, tapi tidak"

**[7:00-8:30] Cultural Monitor**
- Trend mention "ulos" di reviews: naik/turun
- "Jika turun, tanda commercialization. Jika naik, tanda preservasi."

**[8:30-10:00] Governance Vision**
- "Responsible AI bukan fitur, tapi principle"
- "TobaJanji bantu pemda mengukur apa yang selama ini tidak terukur"
- "Roadmap: quarterly TSI report untuk Bupati seluruh 5 Prioritas Destinasi"

---

## 9. Risiko & Mitigasi

| Risiko | Mitigasi |
|---|---|
| Skor terlihat subjektif | Transparent methodology, cite formula |
| Data fasilitas minim | Honest: "data ini incomplete, perlu audit" |
| Demo kurang dramatis | Fokus "revelation" moment — "Anda tahu hanya 15% accessible?" |
| Juri tanya "ini cuma statistik?" | Tunjukkan LLM narrative + recommendation |
| Tidak ada quick win | Position sebagai long-term governance tool |

---

## 10. Differentiator

| Generic | TobaJanji |
|---|---|
| Analytics dashboard | Governance & ethics scorecard |
| Maximize growth | Balance growth + sustainability |
| Single metric (rating) | Multi-dimensional (4 pilar) |
| Visibility bias-aware | Explicit bias auditor |
| Pilot para wisatawan | Pilot untuk regulator/policy maker |

---

## 11. Rencana Keberlanjutan

### Pilot Plan
- Quarterly TSI report ke Bupati 8 kabupaten Toba
- Kolaborasi dengan Bappeda untuk integrasi ke RPJMD
- Metric sukses: 3 keputusan kebijakan terdokumentasi menggunakan TSI

### Scale
- Expand framework ke 5 Prioritas Destinasi Pariwisata
- Standardisasi metrik sustainability untuk pariwisata Indonesia
- Open-source scoring methodology

### Sustainability Angle (Meta!)
- TobaJanji sendiri adalah tools sustainability
- Open methodology untuk transparansi
- Tidak komersial untuk pemda, freemium untuk private developer

### Alignment dengan Challenge Statement
- ✅ Eksplisit address "aspek etika, privasi, keberlanjutan"
- ✅ Sejalan dengan "inklusif" dan "berkelanjutan"
- ✅ Menumbuhkan "budaya pengembangan AI yang bertanggung jawab"
- ✅ Connect dengan manfaat untuk "masyarakat lokal dan pemerintah daerah"

---

## 12. Kapan Pilih Ide Ini

**PILIH TobaJanji jika:**
- Ingin beda total dari tim lain (governance vs consumer)
- Mau bidik "Responsible AI Award" (kategori khusus di hackathon 2026)
- Tim kuat di data science & policy analysis
- Ingin impact jangka panjang, bukan demo greget

**SKIP TobaJanji jika:**
- Mau demo yang dramatis dan interaktif
- Tim lebih kuat di engineering daripada analysis
- Lebih suka solusi consumer-facing
