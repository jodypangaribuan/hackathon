# TobaGov v2 — Honest Tourism Intelligence Platform

> **Tagline:** *"Ubah 12.000 suara wisatawan menjadi keputusan berbasis bukti untuk pengelola destinasi Danau Toba."*

---

## ⚠️ Catatan Versi (Apa yang Diubah dari v1)

| Komponen v1 (Klaim Berlebih) | v2 (Realistis) | Alasan |
|---|---|---|
| "27K reviews" | **12K reviews berisi teks** + 22K rating | 50% review kosong teks (verifikasi) |
| Forecasting Prophet MAPE < 15% | **Dihapus** — pakai trend directional saja | Data `published-at` resolusi tahunan, tidak bisa forecast bulanan |
| Benchmark 8 kabupaten | **Reverse-geocode lat/long** (49% alamat tidak terklasifikasi) | 68/139 metadata tidak bisa di-map dari alamat |
| ABSA 6 aspek, F1 ≥ 0.80 | **3 aspek (fasilitas, kebersihan, pelayanan)**, F1 target 0.70 | Domain baru, dataset kecil, realistis |
| Budget Allocation knapsack | **Ranking prioritas** berbasis complaint × volume | Tidak ada ground truth biaya/ROI |
| "Pilot di Dispar Toba" | **"Proposal tools"** — posisi jujur | Tidak ada kontak stakeholder |
| Prelim Gemini → Final Llama | **Llama 3.1 8B via Groq (prelim) → vLLM B200 (final)** | Konsisten, no migration risk |

---

## 1. Ringkasan Eksekutif

**TobaGov** adalah platform *decision-support* berbasis AI untuk pengelola destinasi & Dinas Pariwisata kawasan Danau Toba. Sistem membaca **12.000+ ulasan berisi teks** dan **22.000+ rating** dari 139 destinasi dan 148 restoran, lalu menjawab pertanyaan kebijakan dalam bahasa natural dengan **situsasi data yang dapat diverifikasi**.

**Posisi yang Jujur:**
- Bukan "AI yang menggantikan keputusan pejabat" → tapi **"asisten analitik yang memberi basis bukti"**
- Bukan "pilot siap deploy" → tapi **"prototipe yang menunjukkan kemampuan + roadmap adopsi"**
- Bukan "forecasting presisi" → tapi **"trend intelligence + hotspot detection"**

### Posisi di Rubrik (Skor Jujur)

| Kriteria | Bobot | Target | Strategi |
|---|---|---|---|
| Kebaruan | 20 | 16-18 | Civic intelligence platform, bukan chatbot wisatawan |
| Dampak | 20 | 14-16 | Beneficiary jelas (pengelola), demo data-driven |
| Teknis | 20 | 14-16 | RAG + ABSA + geospatial, model self-hosted di B200 |
| Kelayakan | 15 | 12-14 | Roadmap realistis, honest limitation disclosure |
| Data | 15 | 13-15 | 12K reviews + reverse-geocode + semua metadata |
| Komunikasi | 10 | 8-9 | Demo "tanya-jawab" dramatis |
| **TOTAL** | **100** | **77-88** | |

---

## 2. Problem Framing (Lebih Tajam, Lebih Jujur)

### Masalah Spesifik
Pengelola destinasi Toba mengambil keputusan berbasis **intuisi** dan **laporan manual yang lambat**. Padahal ada **12.281 ulasan publik berisi teks** dari warga yang mengandung sinyal kuat tentang:

- Fasilitas apa yang paling dikeluhkan
- Destinasi mana yang reputasinya menurun
- Perbedaan kualitas antar wilayah
- Pola keluhan per segmen wisatawan (keluarga vs solo vs wisman)

### Mengapa Ini Sulit Saat Ini
1. **Volume terlalu besar untuk baca manual** (12K reviews)
2. **Data tersebar**: rating di Google, teks di travel apps, fasilitas di lapangan
3. **Tidak ada tools analitik** yang spesifik untuk pariwisata Toba
4. **Insight tidak actionable** — rating 4.2 tidak memberitahu "apa yang harus diperbaiki"

### Pertanyaan Kunci yang Ingin Dijawab
1. "3 keluhan terbesar di kawasan Balige vs Samosir?"
2. "Destinasi mana yang reputasinya menurun dibanding 2 tahun lalu?"
3. "Jika ada Rp X untuk perbaikan fasilitas, destinasi mana prioritas tertinggi?"
4. "Segmen wisatawan mana yang paling tidak puas?"

---

## 3. Fitur Detail (Lebih Sempit, Lebih Dalam)

### Fitur 1: Ask-the-Data (Natural Language Query)

**Cara kerja:**
- User ketik pertanyaan natural
- LLM memahami intent → pilih tool (retrieval / statistik / ranking)
- Output: jawaban + **sumber data eksplisit** (no hallucination)

**Contoh interaksi:**
```
User: "Apa 3 keluhan terbesar di Balige?"

AI: Berdasarkan analisis 1.847 ulasan berisi teks dari 19 destinasi
di area Balige:

TOP 3 KELUHAN (berdasarkan frequency mention):
1. FASILITAS (disebut 142 kali)
   — "toilet kurang", "parkir sempit", "tidak ada mushola"
   — Destinasi paling terdampak: Pantai Lumban Bulbul (41 mention)

2. KEBERSIHAN (disebut 98 kali)
   — "sampah", "kotor", "tempat sampah penuh"
   — Konsentrasi di weekend review

3. PELAYANAN (disebut 67 kali)
   — "lama", "tidak ramah"
   — RM Fly Over paling sering disebut

SUMBER:
- wisata-v2.csv: 1.847 ulasan dengan teks (Balige area)
- ABSA model: 3 aspek, F1 0.71
- Periode: ulasan scraped Juli 2025
```

### Fitur 2: Priority Ranking (Bukan Knapsack)

**Cara kerja:**
- Skor kebutuhan = (complaint count) × (visitor volume proxy) × (1 - current rating/5)
- Rank destinasi dari paling butuh perhatian
- **Tidak klaim "optimal allocation"** — hanya ranking prioritas

**Output:**
```
PRIORITY RANKING — Investasi Fasilitas 2027
============================================

#1 Bukit Holbung Samosir
   Priority Score: 8.7/10
   • 89 keluhan fasilitas dari 1.363 review
   • Rating: 4.4 (turun dari 4.6 periode sebelumnya)
   • Top issue: toilet, parkir
   • Estimasi pengunjung terdampak: ~45K/tahun (proxy dari review volume)

#2 Pantai Pasir Putih Lumban Bulbul
   Priority Score: 7.2/10
   • 41 keluhan fasilitas dari 232 review
   ...

[Metodologi: skor = normalize(complaints × volume × rating_gap)]
[Tidak ada optimasi knapsack — keputusan final di tangan pejabat]
```

### Fitur 3: Trend Intelligence (Bukan Forecasting Presisi)

**Apa yang BISA dilakukan dengan data:**
- Compare rating & sentiment antar periode (1 year ago vs 2 years ago)
- Identifikasi destinasi dengan reputasi menurun
- Deteksi "hotspot" keluhan (area/destinasi dengan keluhan proporsional tinggi)

**Apa yang TIDAK BISA dilakukan (honest disclosure):**
- Forecast bulanan presisi (data resolusi tahunan)
- Prediksi musim ramai (tidak ada data multiple snapshot)

**Output:**
```
TREND INTELLIGENCE — Reputasi 12 Bulan
=======================================

🔴 MENURUN (perlu investigasi):
• Bukit Holbung: 4.6 → 4.4 (turun 0.2)
  — Mayoritas keluhan: kebersihan (periode "months ago")

🟢 STABIL/NAIK:
• Taman Eden 100: 4.5 → 4.6
  — Sentimen konsisten positif

ℹ️ CATATAN: Data `published-at` resolusi kasar
   ("a year ago", "2 years ago"). Analisis berbasis
   perbandingan periode, bukan time-series bulanan.
```

### Fitur 4: Geospatial Hotspot Map

**Cara kerja:**
- Reverse-geocode lat/long dari metadata ke kabupaten
- Plot keluhan/sentiment di peta interaktif
- Highlight area dengan konsentrasi masalah

**Klaim jujur:** 68/139 destinasi (49%) punya alamat ambigu → akan di-reverse-geocode via lat/long (lebih akurat). Sisa kecil tanpa koordinat akan ditandai "lokasi tidak terverifikasi".

---

## 4. Arsitektur Teknis (Fix Migrasi Risk)

```
┌─────────────────────────────────────────────┐
│          USER (Pengelola Destinasi)          │
│         Streamlit / Gradio Web App           │
└────────────────────┬────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│         ORCHESTRATOR (LangGraph)             │
│   Intent classify → pilih tool → sintesis    │
└──────┬──────────┬──────────┬─────────────────┘
       │          │          │
       ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ RAG Tool │ │ Stats    │ │ Geo      │
│          │ │ Tool     │ │ Tool     │
│ChromaDB  │ │ Pandas   │ │ Folium   │
│+ reviews │ │ Plotly   │ │ GeoPandas│
└────┬─────┘ └────┬─────┘ └────┬─────┘
     └────────────┴────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  LLM (Llama 3.1 8B)                          │
│  ==========================================  │
│  PRELIMINARY: via Groq API (Llama 3.1 8B)    │
│  FINAL: via vLLM di DGX B200 (model sama)    │
│  ==========================================  │
│  Konsistensi: prompt & output sama persis    │
│  Risk: minim (hanya ganti endpoint API)      │
└─────────────────────────────────────────────┘
```

### Komponen Teknis

| Komponen | Teknologi | Preliminary | Final (B200) |
|---|---|---|---|
| LLM | Llama 3.1 8B | Groq API (free, cepat) | vLLM lokal |
| Embedding | paraphrase-multilingual-MiniLM | CPU | CPU |
| Vector DB | ChromaDB (in-memory) | CPU | CPU |
| Sentiment | IndoBERT (3 aspek) | Colab T4 | B200 batch inference |
| Dashboard | Streamlit + Plotly + Folium | HuggingFace Space | Docker di B200 |
| Orchestrator | LangGraph | CPU | CPU |

### Kenapa Llama via Groq → vLLM (Bukan Gemini → Llama)
1. **Prompt konsisten** — Llama di Groq sama dengan Llama di vLLM (model identik)
2. **Migrasi risiko rendah** — di final, cuma ganti base URL API (`groq.com` → `localhost:8000`)
3. **Manfaatkan B200** — vLLM dengan tensor parallel = skor teknis naik
4. **Sovereign AI story** — di final bisa bilang "100% self-hosted, data tidak keluar"

---

## 5. Pemanfaatan Dataset (Klaim Jujur)

| File | Realitas Data | Pemanfaatan |
|---|---|---|
| `wisata-v2.csv` | 12,691 total, **6,369 berisi teks** | ABSA, RAG, ranking |
| `resto-hotel-v2.csv` | 9,611 total, **5,911 berisi teks** | UMKM benchmarking |
| `wisata-metadata.csv` | 139 destinasi, 68 alamat ambigu | Master DB + reverse-geocode |
| `resto-metadata.csv` | 148 resto, opening-hours kosong | Resto insight |
| `hotel-metadata.csv` | 36 hotel, place-id kosong | Akomodasi (pakai place-name) |
| `transportasi.csv` | 16 route (ferry critical) | Connectivity analysis |
| `waktu operasional.csv` | 60 destinasi dengan fasilitas | Facility gap scoring |
| `Info TOP 3.csv` | 8 kabupaten × ~45 kolom | Baseline benchmark |
| `kuliner.csv` | 10 dish dengan deskripsi kaya | Cultural asset index |
| `Artikel.csv` | 6 artikel sejarah | RAG konteks |

### Data Engineering Pipeline (Dokumentasi Wajib)

**Notebook 1 — `01_data_audit.ipynb`:**
- Audit semua CSV: hitung missing value per kolom
- Visualisasi distribusi rating, review volume, geographic spread
- **Output**: Data Quality Report (bukti untuk rubrik "Pemanfaatan data")

**Notebook 2 — `02_data_cleaning.ipynb`:**
- Fix CSV escaping bugs (banyak misaligned rows)
- Normalize price format ("25,000" vs "25.000" vs "Rp 25K")
- Deduplikasi place-name fuzzy matching (RapidFuzz)
- Parse `published-at` ke kategori periode (recent, 1y, 2y, old)

**Notebook 3 — `03_reverse_geocode.ipynb`:**
- Extract lat/long dari metadata
- Reverse-geocode ke kabupaten via Nominatim (gratis, no API key)
- **Validate**: compare dengan alamat untuk 70 destinasi yang ada alamat
- Fallback: manual tagging untuk ~10 destinasi tanpa koordinat

**Notebook 4 — `04_absa_training.ipynb`:**
- Manual label **300 review** untuk 3 aspek (fasilitas, kebersihan, pelayanan)
- Split: 240 train, 60 test
- Fine-tune IndoBERT (Colab T4, ~2 jam)
- **Target jujur**: F1 0.70 (bukan 0.85)

---

## 6. Execution Plan (Lebih Realistis)

### Preliminary Round (13 Juli – 2 Agustus)

**Minggu 1 (13-19 Juli): Data Foundation**
- [ ] Hari 1-2: Data audit + cleaning notebook
- [ ] Hari 3-4: Reverse-geocode + kabupaten mapping
- [ ] Hari 5: Manual label 300 review untuk ABSA
- [ ] Hari 6-7: Fine-tune IndoBERT, evaluasi F1

**Minggu 2 (20-26 Juli): Core AI**
- [ ] Hari 8-9: RAG indexing (ChromaDB) atas 12K reviews
- [ ] Hari 10-11: LangGraph orchestrator + 3 tools
- [ ] Hari 12-13: Streamlit prototype (2 tabs: Ask, Dashboard)
- [ ] Hari 14: Test dengan 10 pertanyaan sample

**Minggu 3 (27 Juli – 2 Agustus): Demo + Submission**
- [ ] Hari 15-16: Polish UI, add geospatial map
- [ ] Hari 17: Record video demo (7-9 menit)
- [ ] Hari 18-19: LaporanAnalisis.pdf (8 section wajib)
- [ ] Hari 20: Final check, ZIP code, submit

### Final Round (21-22 Agustus — 2 Hari Lockdown)

**Day 1 (21 Agustus, 08:00-22:00):**
- **08:00-11:00**: Setup B200, deploy Llama 3.1 8B via vLLM
  - Test endpoint, latency benchmark
  - Ganti Groq API → localhost:8000 (5 menit perubahan kode)
- **11:00-15:00**: Polish dashboard (tambah interactive features)
- **15:00-19:00**: Batch inference ABSA atas semua 12K reviews (B200 fast)
- **19:00-22:00**: Demo rehearsal, record backup video

**Day 2 (22 Agustus, 08:00-12:00):**
- 08:00-10:00: Final bug fix, UI polish
- 10:00-12:00: Presentasi + demo + Q&A

---

## 7. Evaluasi Model (Angka Realistis)

| Metrik | Target Jujur | Cara Ukur | Justifikasi |
|---|---|---|---|
| ABSA F1 (3 aspek) | **0.68-0.72** | 60 review test set | Domain baru, 240 training sample |
| RAG Retrieval Precision@5 | **0.70-0.80** | 20 query manual | ChromaDB + multilingual embedding |
| RAG Answer Faithfulness | **0.75-0.85** | RAGAS framework | Grounding ketat dari reviews |
| Reverse-Geocode Accuracy | **0.90+** | Validasi 70 sampel | Nominatim akurat untuk koordinat |
| Intent Classification Acc | **0.85-0.92** | 30 query test | LangGraph router |
| End-to-end Latency | **3-6 detik** | Stopwatch demo | Groq = cepat, vLLM = similar |

### Honest Limitations Disclosure (untuk Rubrik Responsible AI)
- **Data temporal**: `published-at` resolusi tahunan → tidak bisa analisis musiman presisi
- **Sample bias**: review dari wisatawan yang aktif menulis = tidak representative semua wisatawan
- **Aspect coverage**: hanya 3 aspek (fasilitas, kebersihan, pelayanan) — aspek lain (harga, akses) tidak di-cover
- **Geographic gap**: 49% destinasi perlu reverse-geocode, ~7% tanpa koordinat sama sekali
- **Language**: review campuran ID/EN/Batak → model bisa miss konteks lokal

---

## 8. Demo Script (10 Menit — Tidak Overclaim)

### Setup
- Laptop + projector
- Browser: TobaGov dashboard
- 3 saved query scenarios

### Script

**[0:00-1:00] Hook & Problem**
> "Pengelola destinasi Toba mengambil keputusan berbasis intuisi. Padahal ada 12.000 ulasan publik berisi teks dari warga. Bagaimana mengubah ini jadi basis bukti?"

**[1:00-3:00] Feature 1: Ask-the-Data**
- Demo: "Apa 3 keluhan terbesar di Balige?"
- Tampilkan jawaban dengan ranking + sumber data
- "Bukan angka magical — setiap klaim bisa di-trace ke review asli"

**[3:00-5:00] Feature 2: Priority Ranking**
- Tampilkan top 5 destinasi paling butuh perbaikan
- "Kami tidak klaim ini 'alokasi optimal' — ini ranking prioritas. Keputusan final tetap di pejabat."

**[5:00-7:00] Feature 3: Geospatial Hotspot**
- Peta interaktif: choropleth per kabupaten
- "Reverse-geocode dari koordinat, bukan alamat teks yang 49% ambigu"
- Highlight area dengan konsentrasi keluhan

**[7:00-8:30] Honest Limitations**
- "Kami transparan: data review resolusi tahunan, jadi tidak ada forecasting bulanan"
- "ABSA kami F1 0.71 — tidak sempurna, tapi cukup untuk sinyal kuat"
- "Ini prototipe, bukan pilot siap deploy"

**[8:30-10:00] Tech + Closing**
- "Berjalan di Llama 3.1 8B self-hosted di B200 — sovereign AI"
- "Same model di preliminary (Groq) dan final (B200) — konsistensi"
- "Roadmap adopsi: kolaborasi dengan LPPM IT Del untuk uji terbatas"

---

## 9. Risiko & Mitigasi (Lebih Komprehensif)

| Risiko | Probabilitas | Dampak | Mitigasi |
|---|---|---|---|
| B200 vLLM setup gagal | Sedang | Tinggi | Pre-test vLLM di Colab L4, dokumentasi setup |
| ABSA F1 < 0.60 | Sedang | Sedang | Fallback: zero-shot LLM extraction (Llama prompt) |
| Reverse-geocode gagal | Rendah | Sedang | Pre-compute di preliminary, cache hasil |
| Demo internet mati | Sedang | Tinggi | Cache 5 query results, demo offline mode |
| Juri tanya "ini cuma chatbot?" | Sedang | Rendah | Tunjukkan LangGraph dengan multiple tools, bukan single LLM call |
| Juri tanya "siapa yang pakai?" | Tinggi | Sedang | Jawab jujur: "prototipe, target stakeholder pengelola, belum pilot" |
| Review bahasa Batak miss | Sedang | Rendah | Dokumentasi sebagai limitation, pakai multilingual embedding |

---

## 10. Differentiator (Lebih Jujur)

| Aspek | Tim Lain (Generic) | TobaGov v2 |
|---|---|---|
| Target user | "Wisatawan" generik | Pengelola destinasi (specific) |
| Bentuk | Chatbot rekomendasi | Decision-support platform |
| Data usage | Metadata + beberapa review | 12K reviews + semua metadata |
| Klaim AI | "AI canggih" | "F1 0.71, limitation diakui" |
| B200 usage | API OpenAI | Self-hosted Llama via vLLM |
| Forecasting | Klaim MAPE < 15% | "Tidak bisa, data resolusi tahunan" |
| Honesty | Klaim pilot | "Prototipe + roadmap" |

---

## 11. Rencana Keberlanjutan (Realistis)

### Roadmap 3 Bulan Pasca-Hackathon
- **Bulan 1**: Open-source core engine, dokumentasi publik
- **Bulan 2**: Kolaborasi dengan LPPM IT Del untuk demo ke Dispar Toba
- **Bulan 3**: Iterasi berdasarkan feedback + integrasi Google Maps API

### Honest Sustainability Model
- **Non-profit untuk pemda**: gratis, open-source
- **Revenue stream**: consulting untuk private destination operators
- **Tidak klaim "subscription model"** tanpa bukti adopsi

### Yang TIDAK Diklaim (Honest)
- ❌ "Sudah bicara dengan Dispar" (belum)
- ❌ "Pilot Q4 2026" (aspirational, tidak confirmed)
- ❌ "100 UMKM akan pakai" (tidak ada bukti)
- ❌ "Forecasting presisi" (data tidak mendukung)

---

## 12. Self-Audit Checklist

Sebelum submission, pastikan setiap klaim bisa di-back up:

- [ ] Setiap angka di demo bisa di-trace ke notebook/sumber
- [ ] F1 score dilaporkan dari test set asli (bukan aspirational)
- [ ] Tidak ada klaim "27K reviews" → pakai "12K reviews berisi teks"
- [ ] Tidak ada klaim "forecasting" → pakai "trend intelligence"
- [ ] Tidak ada klaim "pilot" → pakai "prototipe + roadmap"
- [ ] Limitations section di laporan eksplisit & jujur
- [ ] Demo tidak menampilkan wajah/institusi
- [ ] Source code bisa di-run dari README

---

## 13. Kapan Pilih Ide Ini

**PILIH TobaGov v2 jika:**
- Tim kuat di data engineering + Python ML
- Mau angle "civic intelligence" yang beda
- Nyaman dengan honest disclosure (juri respect ini)
- Mau manfaatkan B200 untuk LLM self-hosted

**SKIP TobaGov v2 jika:**
- Mau demo yang greget dengan UI fancy
- Tidak nyaman dengan "hanya ranking" (bukan optimization)
- Lebih suka consumer-facing app
- Tim lebih kuat di frontend daripada backend ML
