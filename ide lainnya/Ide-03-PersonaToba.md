# PersonaToba — Synthetic Traveler Simulation Engine

> **Tagline:** *"Sebelum membangun destinasi, simulasi dulu dengan 1.000 wisatawan digital. Temukan masalah sebelum wisatawan sungguhan kecewa."*

---

## 1. Ringkasan Eksekutif

**PersonaToba** adalah mesin simulasi multi-persona yang menghidupkan **5 tipe wisatawan digital** (Backpacker, Keluarga, Lansia, Wisman, Content Creator) untuk "menjalani" itinerary di Danau Toba. Setiap persona adalah LLM agent dengan preferensi, budget, dan tolerance berbeda — mereka membaca ulasan destinasi, mengunjungi tempat secara virtual, lalu memberikan feedback.

Output: **gap analysis** — fasilitas apa yang kurang untuk segmen tertentu, destinasi mana yang inaccessible untuk lansia, di mana backpacker struggle dengan transportasi.

### Mengapa Ini 2026
- **Synthetic data generation** + **multi-agent simulation** = tren AI paling hot 2026
- USAII Hackathon 2026 Graduate winner: agent-based policy engine
- Reskilll: "Multi-agent debate system for decision-making"
- **Tidak ada tim lain** yang akan memikirkan pendekatan ini

### Posisi di Rubrik

| Kriteria | Bobot | Target | Strategi |
|---|---|---|---|
| Kebaruan | 20 | 19-20 | Paling novel — agent simulation untuk pariwisata |
| Dampak | 20 | 15-17 | Pre-emptive design, mencegah masalah sebelum terjadi |
| Teknis | 20 | 17-19 | Multi-agent LLM + persona consistency + RAG grounding |
| Kelayakan | 15 | 12-14 | Butuh stakeholder pengelola destinasi untuk value |
| Data | 15 | 13-15 | Reviews + metadata + Info TOP 3 untuk persona grounding |
| Komunikasi | 10 | 8-10 | Demo simulasi live = greget tinggi |
| **TOTAL** | **100** | **84-95** | |

---

## 2. Problem Framing

### Masalah Utama
Pengembang destinasi pariwisata membuat keputusan **tanpa pernah bertanya**: bagaimana rasanya jadi lansia di Bukit Holbung? Bagaimana rasanya jadi wisman yang tidak bahasa Indonesia di pasar Balige?

Setiap destinasi dinilai dari **satu sudut pandang** (pengelola / wisatawan umum). Tidak ada tools untuk **simulasi multi-perspektif** sebelum investasi.

### Urgensi
- Investasi infrastruktur pariwisata Toba miliaran rupiah
- Banyak fasilitas dibangun **untuk wisatawan rata-rata**, padahal segmen wisatawan beragam
- Risiko: destinasi tidak inklusif,口碑 negatif dari segmen tertentu

### Pertanyaan Kunci
1. "Jika 100 wisatawan lansia visit Toba bulan depan, di mana mereka akan struggle?"
2. "Backpacker budget Rp 150K/hari — itinerary apa yang feasible?"
3. "Wisatawan mancanegara (non-Indonesian speaker) — di mana info gap terbesar?"
4. "Keluarga dengan anak balita — destinasi mana yang paling ramah?"

---

## 3. Fitur Detail

### Fitur 1: Persona Generator

**5 persona default** (berbasis `Info TOP 3.csv` data profil turis nyata):

```yaml
PERSONA 1: "Sarah the Backpacker"
- Demografis: 24 thn, perempuan, Solo
- Budget: Rp 200K/hari
- Bahasa: EN + sedikit ID
- Tolerance: jalan kaki 5km OK, hostel OK, tidak masalah transport umum
- Preferensi: hidden gems, lokal authentic, foto Instagram
- Pain points: tidak suka turis massal, takut scam

PERSONA 2: "Keluarga Tamba"
- Demografis: 35 thn, suami-istri + 2 anak (4 & 7 thn)
- Budget: Rp 800K/hari
- Bahasa: ID
- Tolerance: perlu mobil, anak perlu toilet, tidak tahan jalan kaki > 2km
- Preferensi: family-friendly, edukatif, aman
- Pain points: anak rewel, butuh istirahat

PERSONA 3: "Opa Müller" (Wisman Lansia)
- Demografis: 68 thn, laki-laki, Jerman
- Budget: Rp 1.5M/hari
- Bahasa: EN/DE, no ID
- Tolerance: tidak tahan tangga, perlu hotel bintang 4+, makanan halal/kosher
- Preferensi: cultural depth, comfort, slow travel
- Pain points: akses kesehatan, bahasa, mobility

PERSONA 4: "Dimas Creator"
- Demografis: 28 thn, content creator TikTok
- Budget: Rp 500K/hari
- Bahasa: ID
- Tolerance: flexible, cari visual spektakuler
- Preferensi: sunset/sunrise spot, aesthetic cafe, unique experience
- Pain points: butuh WiFi upload, charging station

PERSONA 5: "Pasangan Honeymoon Andini"
- Demografis: 30 thn, honeymoon
- Budget: Rp 1.2M/hari
- Bahasa: ID
- Tolerance: romantic ambiance, privacy
- Preferensi: sunset dinner, couple activities, aesthetic stay
- Pain points: crowd, noise
```

### Fitur 2: Simulation Engine

**Cara kerja:**
1. User pilih persona + itinerary (atau generate auto dari prompt)
2. Persona agent "menjalani" itinerary step-by-step
3. Di setiap destinasi, agent retrieve 50 review relevan (RAG)
4. Agent "bereaksi" sesuai preferensi/tolerance persona
5. Output: diary pengalaman + friction points + satisfaction score

**Contoh output:**
```
===== SIMULASI: "Sarah the Backpacker" =====
===== ITINERARY: Balige → Samosir → Balige, 1 hari =====

07:00 - Berangkat dari Balige naik angkot (Rp 15K)
  → "OK, sesuai budget. Tapi info jadwal tidak jelas."

09:00 - Ferry Ajibata → Tomok (Rp 7K)
  → "Ferry jam 9 kepenuhan, tunggu 30 menit. Frustrating."

10:30 - Tomok: Museum Batak Center
  → "Fascinating! Tapi penjelasan cuma Batak/ID. Saya tidak paham."

13:00 - Makan siang di Jenny's Restaurant
  → "Naniura menarik tapi Rp 80K. Over budget untuk saya."

...

FRICTION POINTS:
⚠ Info multibahasa minim di 4/5 destinasi
⚠ Ferry capacity tidak predictable
⚠ Menu Batak mahal untuk backpacker budget

SATISFACTION: 6.5/10
```

### Fitur 3: Gap Detector (Multi-Persona)

Jalankan simulasi untuk semua 5 persona di destinasi yang sama → bandingkan:

```
DESTINASI: Bukit Holbung Samosir
=================================
Backpacker  : 8.5/10 (loves the view, OK with hike)
Keluarga    : 4.0/10 (anak tidak bisa naik, tidak ada toilet)
Lansia      : 2.0/10 (tangga curam, tidak accessible)
Creator     : 9.0/10 (golden hour spektakuler)
Honeymoon   : 7.0/10 (romantis tapi crowd)

GAP INSIGHT: Lansia & Keluarga tidak bisa menikmati Bukit Holbung.
Rekomendasi: tangga lebih landai, toilet di tengah jalur.
```

### Fitur 4: What-If Policy Simulator

**Cara kerja:**
- User: "Bagaimana jika kita tambahkan toilet gratis di 5 destinasi?"
- Sistem re-run simulasi dengan modifikasi fasilitas
- Compare satisfaction score before/after

### Fitur 5: Synthetic Review Generator (Bonus)

Generate ulasan sintetis dari persona untuk destinasi baru yang belum punya review → bantu cold-start problem.

---

## 4. Arsitektur Teknis

```
┌──────────────────────────────────────────────┐
│           USER (Perencana Destinasi)          │
│            Streamlit / Gradio UI              │
└────────────────────┬─────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────┐
│          SIMULATION ORCHESTRATOR              │
│   (LangGraph multi-agent coordinator)        │
└──────┬───────────────────────────────────────┘
       │
       ├──→ Persona 1 (Sarah Backpacker) ──┐
       ├──→ Persona 2 (Keluarga Tamba)  ──┤
       ├──→ Persona 3 (Opa Müller)      ──┤──→ Aggregate
       ├──→ Persona 4 (Dimas Creator)   ──┤    & Gap Analysis
       └──→ Persona 5 (Honeymoon)       ──┘
                                          │
                                          ▼
                          ┌────────────────────────┐
                          │   SHARED RAG LAYER     │
                          │  • 27K reviews         │
                          │  • 139 destinations    │
                          │  • Ferry schedules     │
                          │  • Facility metadata   │
                          └────────────────────────┘
                                          │
                                          ▼
                          ┌────────────────────────┐
                          │  LLM (Llama 3.1 8B)    │
                          │  5 parallel instances  │
                          │  di B200 (vLLM)        │
                          └────────────────────────┘
```

### Komponen Teknis

| Komponen | Teknologi | GPU Need |
|---|---|---|
| Persona Agent | Llama 3.1 8B dengan persona system prompt | 1× B200 per persona (5 total, sequential OK) |
| RAG | ChromaDB + multilingual embeddings | CPU |
| Orchestrator | LangGraph | CPU |
| UI | Streamlit | CPU |
| Output viz | Plotly (radar chart per persona) | CPU |

### B200 Sweet Spot
- 5 persona agents bisa jalan **parallel** di 5 GPU B200 (DGX B200 punya 8 GPU)
- Atau sequential di 1 GPU (lebih aman untuk demo)
- vLLM untuk efficient batching

---

## 5. Pemanfaatan Dataset

| File | Pemanfaatan |
|---|---|
| `wisata-v2.csv` (14K) | Persona reads real reviews untuk "bereaksi" |
| `resto-hotel-v2.csv` (12K) | Resto/hotel reaction grounding |
| `wisata-metadata.csv` | Destinasi profile untuk itinerary |
| `resto-metadata.csv` | Menu + harga untuk budget simulation |
| `hotel-metadata.csv` | Accommodation options |
| `transportasi.csv` | **Critical** — ferry schedule constraint |
| `Info TOP 3.csv` | **Source persona** dari real tourist profile data |
| `waktu operasional.csv` | Facility info untuk accessibility simulation |
| `kuliner.csv` | Cultural depth untuk wisman persona |

---

## 6. Execution Plan

### Preliminary Round

**Minggu 1: Persona + Data**
- [ ] Ekstrak real tourist profile dari `Info TOP 3.csv`
- [ ] Define 5 persona dengan YAML schema (lengkap)
- [ ] Data cleaning untuk RAG indexing
- [ ] Notebook 1: persona design + data pipeline

**Minggu 2: Simulation Engine**
- [ ] RAG setup (ChromaDB)
- [ ] Single-persona simulation (test dengan Sarah Backpacker)
- [ ] LangGraph multi-persona orchestrator
- [ ] Notebook 2: simulation engine

**Minggu 3: Demo + Submission**
- [ ] Gap Detector logic
- [ ] Streamlit UI (visual radar chart)
- [ ] Video demo — show 1 destinasi, 5 persona reactions
- [ ] Evaluasi: persona consistency score, friction detection rate

### Final Round (2 hari)

**Day 1:**
- Deploy 5 Llama 3.1 8B instances di B200 (1 per persona, parallel)
- Atau 1 instance dengan vLLM batching (5x throughput)
- Polish UI: timeline viz, persona diary
- Add What-If Simulator

**Day 2:**
- Demo rehearsal
- Present

---

## 7. Evaluasi Model

| Metrik | Target | Metode |
|---|---|---|
| Persona Consistency | ≥ 80% | LLM-as-judge: apakah reaction sesuai persona profile |
| Friction Detection | ≥ 70% overlap dgn manual | Compare dengan known issues (e.g., toilet minim) |
| Simulation Realism | ≥ 4/5 | Manual rating oleh 3 volunteer |
| Latency (5 persona) | < 60 detik | Stopwatch |
| Insight Novelty | ≥ 3 non-obvious insight | Manual review |

---

## 8. Demo Script

### Setup
- Pre-load simulation results untuk Bukit Holbung (5 persona)
- Pre-load What-If scenario: "Tambah toilet di Bukit Holbung"

### Script

**[0:00-1:30] Hook**
> "Pak/Bbu juri, jika 5 jenis wisatawan berbeda visit Bukit Holbung besok — backpacker Jerman, keluarga Tamba dari Jakarta, opa Müller 68 tahun — siapa yang akan kecewa? Saat ini, tidak ada cara untuk tahu sebelum mereka datang."

**[1:30-3:30] Persona Showcase**
- Tampilkan 5 persona card dengan avatar
- "Setiap persona punya personality, budget, tolerance berbeda"

**[3:30-6:00] Live Simulation**
- Pilih destinasi: Bukit Holbung
- Run simulation (atau show cached result)
- Tampilkan diary 3 persona:
  - Sarah: "loved it"
  - Keluarga: "anak tidak bisa naik"
  - Opa Müller: "tangga curam, saya tidak bisa"
- Radar chart satisfaction per persona

**[6:00-8:00] Gap Detector**
- Highlight: "Lansia & Keluarga tidak bisa nikmati"
- AI rekomendasi: "Tangga landai + toilet di tengah = +3 points Lansia"

**[8:00-9:30] What-If Simulator**
- User input: "Tambah toilet + perbaiki jalur"
- Re-run simulation
- Show: Lansia naik dari 2.0 → 6.5

**[9:30-10:00] Tech + Vision**
- "5 LLM agents parallel di B200, grounded dengan 27K real reviews"
- "Ini bukan chatbot. Ini digital twin pariwisata Toba."

---

## 9. Risiko & Mitigasi

| Risiko | Mitigasi |
|---|---|
| Persona terlalu generik | Few-shot dengan specific Batak context |
| Simulasi lambat (5 agent) | Pre-compute untuk demo, vLLM batching |
| Reaksi tidak realistis | Grounding wajib dengan RAG real reviews |
| Terlalu akademik untuk juri praktisi | Demo fokus insight actionable, bukan paper |
| Hallucination faktual | Hard rules: budget selalu computed, bukan hallucinated |

---

## 10. Differentiator

| Generic | PersonaToba |
|---|---|
| Chatbot rekomendasi | Multi-agent simulation |
| Satu sudut pandang | 5 perspektif paralel |
| Reaktif (jawab pertanyaan) | Proaktif (find gaps sebelum terjadi) |
| Insight abstrak | Diary pengalaman + friction timeline |
| Analitik post-hoc | Pre-emptive design tool |

---

## 11. Rencana Keberlanjutan

### Use Case Real
- **Bappeda Toba**: simulasi sebelum bangun infrastruktur baru
- **Dispar**: test paket tour baru untuk segmen target
- **Asosiasi Hotel**: simulasi experience tamu different segment
- **Pengembang destinasi baru**: demand forecasting per persona

### Roadmap
- Bulan 1-3: Tambah 10 persona (semua segmen dari data TOP 3)
- Bulan 4-6: Integrasi data review real-time
- Bulan 7-12: Expand ke 4 Destinasi Prioritas lain

### Sustainability
- SaaS untuk pengembang destinasi (B2B)
- License ke kementerian Pariwisata
- Open-source persona framework, paid simulation engine
