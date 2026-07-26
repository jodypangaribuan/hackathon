# TobaScribe — Multimodal Knowledge Scribe

> **Tagline:** *"Foto ulos, dengar ceritanya. Foto makanan, tahu sejarahnya. Multimodal AI yang menjadikan setiap objek Toba sebuah cerita."*

---

## 1. Ringkasan Eksekutif

**TobaScribe** adalah asisten multimodal (vision + voice + text) yang menjadi **jembatan pengetahuan** antara wisatawan, UMKM, dan warisan budaya Toba. Tiga mode utama: **Snap-to-Knowledge** (foto → cerita), **Voice Storyteller** (audio guide otomatis), dan **Auto-Documenter** (foto UMKM → deskripsi marketing siap pakai).

### Mengapa Ini 2026
- **Multimodal AI** adalah tren dominan 2026 (GPT-4o, Gemini 2.5, Qwen-VL)
- Reskilll #2: "Accessibility Describer" = multimodal untuk inklusi
- **Vision + Voice** = demo paling greget dan visible

### Posisi di Rubrik

| Kriteria | Bobot | Target | Strategi |
|---|---|---|---|
| Kebaruan | 20 | 16-18 | Multimodal + cultural preservation angle |
| Dampak | 20 | 15-17 | UMKM + wisatawan + preservasi budaya |
| Teknis | 20 | 17-19 | Vision model + Whisper + TTS + RAG |
| Kelayakan | 15 | 13-15 | Use case jelas untuk UMKM & wisatawan |
| Data | 15 | 12-14 | Kuliner + artikel + deskripsi untuk RAG |
| Komunikasi | 10 | 9-10 | Demo paling greget: langsung tunjuk foto |
| **TOTAL** | **100** | **82-93** | |

---

## 2. Problem Framing

### Masalah Utama
1. **Wisatawan asing** tidak paham konteks budaya: lihat ulos, tidak tahu ini tenun tradisional. Lihat makanan, tidak tahu namanya. Info plank di museum hanya Bahasa Indonesia/Batak.
2. **Lansia & disabilitas penglihatan**: tidak bisa baca info text di destinasi
3. **UMKM**: tidak bisa buat deskripsi marketing produk mereka (tidak paham copywriting, tidak ada waktu)

### Urgensi
- 5 Prioritas Destinasi → target wisman. Tapi info multibahasa minim.
- UMKM Toba ketinggalan digital marketing karena tidak bisa deskripsikan produk.
- Budaya Batak (ulos, kuliner, marga) kaya tapi **tidak terdokumentasi accessible**.

### Insight dari Dataset
- `kuliner.csv` punya deskripsi mendalam 10 hidangan Batak → knowledge base
- `Artikel Danau Toba.csv` punya 6 artikel sejarah kaya
- `wisata-metadata.csv` description field → konteks per destinasi
- Bisa di-RAG untuk grounding vision model

---

## 3. Fitur Detail

### Fitur 1: Snap-to-Knowledge (Vision + RAG)

**Cara kerja:**
1. User foto objek (ulos, makanan, arsitektur, patung)
2. VLM (Qwen2.5-VL) identify objek
3. RAG retrieve konteks budaya dari kuliner.csv + artikel
4. Output: penjelasan dalam bahasa user (ID/EN)

**Contoh interaksi:**
```
[User upload foto: mie gomak]

TOBASCRIBE:
📷 Object identified: Mie Gomak (Batak cuisine)

📖 CERITA:
Mie Gomak adalah hidangan khas Batak Toba yang
berasal dari kata "gomak" (tangan) — disajikan
dengan kuah kental rempah, ikan mas, dan dao-dao.

Sejarahnya berasal dari tradisi pesta adat...

🏖 DI MANA BISA COBA:
1. RM Sinar Minang (Balige) — Rp 25K
2. Jenny's Restaurant (Tuktuk) — Rp 35K
3. Damar Toba — Rp 40K

💬 Did you know? Mie Gomak sering disajikan saat
upacara adat seperti pernikahan Batak.

[Sumber: kuliner.csv, resto-metadata.csv]
```

### Fitur 2: Voice Storyteller (Audio Guide Otomatis)

**Cara kerja:**
1. User di destinasi, GPS-based atau pilih dari list
2. Sistem generate cerita audio lokasi (history, cultural context, tips)
3. TTS ke Bahasa Indonesia / English
4. Bonus: voice karakter Batak untuk authenticity

**Use case:**
- Lansia yang tidak bisa baca text panjang
- Wisman yang tidak bahasa Indonesia
- Audio guide gratis tanpa sewa guide manusia

**Tech:** RAG atas Artikel + description + Whisper (input voice) + MeloTTS (output)

### Fitur 3: Auto-Documenter (UMKM Marketing Copilot)

**Cara kerja:**
1. UMKM foto produk (makanan, ulos, kerajinan)
2. VLM identify + describe visual
3. LLM generate 3 varian copy: Instagram caption, GoFood description, Google Maps description
4. Output siap pakai

**Contoh:**
```
[UMKM upload foto: ulos Batak]

COPY 1 - INSTAGRAM CAPTION:
"Ulos Batak yang autentik dari Toba 🔥
Setiap helai benang membawa cerita leluhur.
Dapatkan di [Toko Saya] Balige.
#UlosBatak #DanauToba #KaryaAnakNegeri"

COPY 2 - GOFOOD DESCRIPTION:
"Ulos tenun tradisional Batak Toba.
Dibuat oleh pengrajin lokal Desa Jangga.
Ukuran 200x80cm. Cocok untuk hadiah
atau koleksi cultural."

COPY 3 - GOOGLE MAPS:
"Toko Ulos Sianok Mula — pengrainan ulos
autentik sejak 1985. Lokasi: Jl. Balige...
Rating: 4.7. Buka 08:00-17:00."
```

### Fitur 4: Snap-and-Translate (Bonus)

**Cara kerja:**
Foto menu / signage Bahasa Batak → VLM + OCR → translate ke ID/EN

### Fitur 5: Heritage Walk Generator (Bonus)

**Cara kerja:**
- User pilih area (Balige, Tuktuk, Tomok)
- AI generate audio walking tour dengan 5-7 stop
- Setiap stop: photo reference + audio story

---

## 4. Arsitektur Teknis

```
┌──────────────────────────────────────────────┐
│         USER (Wisatawan / UMKM)               │
│      Web App (Gradio) / Mobile-web            │
└──────┬───────────────────────────┬───────────┘
       │ photo/voice/text          │
       ▼                           ▼
┌──────────────┐           ┌──────────────┐
│  VISION LANE │           │  VOICE LANE  │
│              │           │              │
│ Qwen2.5-VL   │           │ Whisper-     │
│ (B200)       │           │ large-v3     │
│              │           │ (B200)       │
└──────┬───────┘           └──────┬───────┘
       │                          │
       └────────────┬─────────────┘
                    │
                    ▼
       ┌────────────────────────┐
       │     RAG LAYER          │
       │  ChromaDB:             │
       │  • kuliner (10)        │
       │  • artikel (6)         │
       │  • wisata description  │
       │  • resto metadata      │
       └────────────┬───────────┘
                    │
                    ▼
       ┌────────────────────────┐
       │ LLM (Llama 3.1 8B B200)│
       │ Story generation,      │
       │ Copy generation,       │
       │ Translation            │
       └────────────┬───────────┘
                    │
                    ▼
       ┌────────────────────────┐
       │  OUTPUT LANE           │
       │  • MeloTTS (B200)      │
       │  • Rendered text + img │
       └────────────────────────┘
```

### Tech Stack

| Komponen | Teknologi | GPU Need |
|---|---|---|
| Vision | Qwen2.5-VL 7B via vLLM | 2× B200 |
| Speech-to-Text | Whisper-large-v3 | 1× B200 |
| Text-to-Speech | MeloTTS / XTTS-v2 | 1× B200 |
| LLM | Llama 3.1 8B | 1× B200 |
| Embedding | multilingual-MiniLM | CPU |
| RAG | ChromaDB | CPU |
| UI | Gradio | CPU |

### B200 Sweet Spot
- 4 model parallel: VLM, Whisper, TTS, LLM = 5 GPU
- DGX B200 punya 8 GPU → muat dengan margin
- **This is the best B200 utilization scenario**

---

## 5. Pemanfaatan Dataset

| File | Pemanfaatan |
|---|---|
| `kuliner.csv` (10) | Knowledge base makanan Batak untuk Snap-to-Knowledge |
| `Artikel.csv` (6) | Sejarah & cultural context untuk Voice Storyteller |
| `wisata-metadata.csv` (139) | Description per destinasi untuk audio guide |
| `resto-metadata.csv` (148) | "Where to try" recommendations |
| `Attractions Info.csv` (14) | Cultural background aktivitas |
| `Info TOP 3.csv` | Top spots per kabupaten untuk Heritage Walk |

### Knowledge Engineering
1. **Index kuliner** — setiap dish: nama, deskripsi, asal, tradisi, di-mana-coba
2. **Index artikel** — chunk per paragraf, metadata topik
3. **Index destinasi** — description + cultural context
4. **Image dataset** — perlu scrapping / synthetic generation untuk training VLM
   - **Challenge**: data foto Toba terbatas
   - **Solusi**:gunakan VLM zero-shot dengan RAG grounding (no fine-tuning)

---

## 6. Execution Plan

### Preliminary Round

**Minggu 1: RAG + Knowledge Base**
- [ ] Clean & enrich kuliner.csv (tambah konteks)
- [ ] Chunk Artikel untuk RAG
- [ ] Build ChromaDB index
- [ ] Notebook 1: knowledge base + RAG eval

**Minggu 2: Multimodal Pipeline**
- [ ] Test Gemini Vision API untuk Snap-to-Knowledge (prelim)
- [ ] Test Whisper API untuk voice input
- [ ] Prompt engineering untuk story generation
- [ ] Notebook 2: multimodal pipeline

**Minggu 3: Demo + Submission**
- [ ] Gradio web app (3 tabs: Snap, Voice, UMKM)
- [ ] Prepare 10 foto test case (ulos, makanan, arsitektur)
- [ ] Video demo — show live photo upload
- [ ] Evaluasi: VLM accuracy, RAG faithfulness, TTS quality

### Final Round (2 hari)

**Day 1:**
- Deploy Qwen2.5-VL 7B + Whisper + MeloTTS + Llama di B200
- Migrasi dari API → local models
- Polish UI, add Voice Storyteller

**Day 2:**
- Final test, demo rehearsal
- Present

---

## 7. Evaluasi Model

| Metrik | Target | Metode |
|---|---|---|
| VLM Object Identification | ≥ 70% | 30 foto test case |
| RAG Faithfulness | ≥ 0.80 | RAGAS framework |
| Story Quality (LLM-judge) | ≥ 4/5 | Manual eval 20 stories |
| TTS Naturalness (MOS) | ≥ 3.5/5 | 10 listener survey |
| UMKM Copy Quality | ≥ 4/5 | Manual eval 10 produk |
| End-to-end Latency | < 8 detik | Stopwatch |

---

## 8. Demo Script

### Setup
- Prepare 5 test photos: ulos, mie gomak, rumah Bolon, patung Sigale-gale, signage Batak
- Prepare 2 UMKM produk photos
- Mic untuk voice demo

### Script

**[0:00-1:30] Hook**
> "Pak juri, saya wisman dari Jerman. Saya lihat ini [tunjuk foto ulos]. Apa ini? Saya tidak tahu. Tidak ada info Bahasa Inggris. Saya pergi tanpa memahami."

**[1:30-3:30] Snap-to-Knowledge Demo**
- Upload foto ulos
- Tampilkan: VLM identify "Ulos Batak"
- RAG add cultural context
- Output: cerita ulos + di mana beli + tradisi

**[3:30-5:00] Voice Storyteller**
- Pilih destinasi: Museum Batak Center
- Generate audio story (Indonesia + English)
- Play sample — "Dengar, ini cerita sejarah Batak dalam 30 detik"
- "Untuk lansia, untuk wisman, gratis"

**[5:00-7:00] UMKM Auto-Documenter**
- Upload foto makanan UMKM
- Generate 3 copy variants: Instagram, GoFood, Google Maps
- "UMKM Toba tidak perlu jago copywriting. Foto, dapat copy siap pakai."

**[7:00-8:30] Multimodal Architecture**
- Slide: 4 model parallel di B200 (VLM + Whisper + TTS + LLM)
- "Ini kenapa B200 penting — multimodal butuh banyak model jalan bareng"

**[8:30-10:00] Vision & Impact**
- "Preservasi budaya + aksesibilitas + UMKM empowerment — satu tools"
- "Bisa dikembangkan ke seluruh destinasi budaya Indonesia"

---

## 9. Risiko & Mitigasi

| Risiko | Mitigasi |
|---|---|
| VLM tidak recognize objek Batak | RAG grounding + fallback "I see X, here's context..." |
| TTS kualitas rendah | Use XTTS-v2 atau fine-tune dengan sample voice Batak |
| Foto test case di demo gagal | Pre-test 10 foto, siap fallback cached result |
| Multimodal butuh banyak GPU | B200 punya 8 — cukup; pre-test resource allocation |
| Bahasa Batak untuk TTS | Fokus ID + EN dulu, Batak sebagai bonus |

---

## 10. Differentiator

| Generic | TobaScribe |
|---|---|
| Text chatbot | Multimodal (vision + voice + text) |
| Output text | Photo + audio + text output |
| Untuk wisatawan umum | Wisatawan + lansia + wisman + UMKM |
| API OpenAI only | Self-hosted 4 model di B200 |
| Rekomendasi abstrak | Photo → cerita konkret |

---

## 11. Rencana Keberlanjutan

### Pilot Plan
- Deploy di Museum Batak Center + 5 destinasi prioritas
- Sticker QR code di setiap objek → user scan → audio guide
- UMKM onboarding: 20 pilot, free copy generation

### Scale
- Mobile app (React Native) untuk pengalaman lebih baik
- Partnership dengan Google Arts & Culture untuk cultural preservation
- Expand ke 4 destinasi budaya lain (Bali, Yogyakarta, Toraja, Papua)

### Sustainability
- Freemium: 3 foto/bulan gratis, unlimited berbayar
- B2B: Museum, tourism board subscribe untuk custom knowledge base
- Open-source multimodal framework, paid content
