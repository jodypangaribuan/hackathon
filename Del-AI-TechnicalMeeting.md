# Del AI Hackathon 2026 — Technical Meeting

**Tema:** AI Tourism  
**Tagline:** *Build Smart Solutions, Shape the Future of Tourism*  
**Tanggal:** Senin, 13 Juli 2026  
**Lokasi:** Institut Teknologi Del  

---

## Agenda

| No | Topik | Keterangan |
|----|-------|------------|
| 01 | Format & Alur Kompetisi | Preliminary Round vs Final Round |
| 02 | Linimasa & Jadwal Penting | Tanggal-tanggal yang wajib diingat |
| 03 | Challenge Statement | Tema, tujuan, dan ruang eksplorasi |
| 04 | Dataset Pariwisata Toba | Isi, karakter, dan ketentuan penggunaan |
| 05 | Pendekatan Teknis | Metode AI yang diperbolehkan |
| 06 | Luaran & Artefak Submission | Apa yang wajib dikumpulkan |
| 07 | Rubrik Penilaian | Bagaimana tim akan dinilai |
| 08 | Tata Tertib & Tanya Jawab | Aturan penting dan sesi diskusi |

---

## 1. Format & Alur Kompetisi

### Dua Tahap: Preliminary & Final Round

#### Tahap 1 — Preliminary Round
**Online • 13 Juli – 2 Agustus 2026**

- Seluruh tim menerima raw dataset pariwisata Toba
- Eksplorasi data untuk menghasilkan insight & solusi
- **Penilaian:** kualitas analisis, interpretasi, visualisasi, dan dampak rekomendasi
- **Submission:** laporan analisis, slide pitching, video demo, source code

#### Tahap 2 — Final Round
**Onsite di IT Del • 21–22 Agustus 2026**

- Tim yang lolos membangun produk nyata (mobile app / website / solusi AI lain)
- **Lockdown session:** pengembangan intensif & deployment di DGX B200 IT Del
- Presentasi 10 menit + tanya jawab 10 menit di depan dewan juri
- **Penilaian:** inovasi, implementasi AI, UX, scalability, dampak pariwisata

---

## 2. Linimasa & Jadwal Penting

| Tanggal | Kegiatan | Keterangan |
|---------|----------|------------|
| 5–12 Juli 2026 | Pendaftaran Peserta | Online |
| 13 Juli 2026 | Technical Meeting (Hari Ini) | Tanya jawab ketentuan |
| 13 Juli – 2 Agustus 2026 | Preliminary Submission | Deadline pukul **20:00 WIB** |
| 12–14 Agustus 2026 | Pengumuman Finalis | Via aicenter.del.ac.id |
| 18 Agustus 2026 | Technical Meeting Final | Teknis pelaksanaan final |
| 21 Agustus 2026 | Final Round – Day One | Onsite di IT Del |
| 22 Agustus 2026 | Final Round – Day Two | Onsite + Pengumuman Pemenang |

---

## 3. Challenge Statement

### Open Challenge Berbasis Data Pariwisata Danau Toba

> Bagaimana AI dapat membantu ekosistem pariwisata Toba menjadi lebih **informatif, inklusif, efisien, berkelanjutan, dan bernilai** bagi wisatawan, pelaku usaha lokal, pengelola destinasi, masyarakat, serta pemerintah daerah?

Peserta bebas memilih masalah, pengguna sasaran, pendekatan teknis, dan bentuk solusi.  
Dataset Toba yang mentah dan belum terintegrasi adalah **bagian dari tantangan itu sendiri**, bukan sekadar hambatan.

**Prinsip utama:**
- Solusi AI yang relevan dengan kebutuhan nyata ekosistem Toba
- Ruang bagi peserta menemukan masalah & peluang baru
- Mengubah data mentah menjadi insight, layanan, atau produk
- AI yang bertanggung jawab, transparan, dan kontekstual lokal

### Contoh Arah Masalah & Solusi *(Bukan Batasan)*

| Ruang Eksplorasi | Contoh Masalah | Contoh Solusi |
|------------------|----------------|---------------|
| **Pengalaman Wisatawan** | Sulit menemukan info sesuai kebutuhan, anggaran, bahasa, waktu | Asisten wisata, semantic search, itinerary assistant |
| **Data Intelligence** | Data tempat & ulasan belum bersih dan belum terhubung | Data quality copilot, entity matching, knowledge graph |
| **UMKM & Ekonomi Lokal** | Pelaku lokal butuh insight kebutuhan wisatawan | Insight engine, analisis sentimen, demand analytics |
| **Operasional Destinasi** | Pengelola perlu memahami gap layanan & fasilitas | Destination dashboard, geospatial intelligence |
| **Aksesibilitas & Inklusi** | Info belum ramah keluarga, lansia, disabilitas, multibahasa | Layanan multibahasa, accessibility finder |
| **Keberlanjutan** | Pariwisata perlu mendukung budaya & lingkungan lokal | Sustainability monitor, crowding indicator |

---

## 4. Dataset Pariwisata Toba

### Satu Ekosistem Data

Ekosistem data terintegrasi: profil tempat, fasilitas fisik, dan ulasan riil pengguna di kawasan Danau Toba (**Balige, Muara, Silaen**, dan sekitarnya).

**Kategori data:**
- Destinasi Wisata
- Akomodasi
- Kuliner & Kafe
- Transportasi
- Budaya & UMKM
- Fasilitas Umum
- Ulasan Pengguna

**Karakter dataset:**
- **Raw & realistis** — mungkin ada duplikasi, field kosong, format tidak konsisten
- **Tidak seluruhnya terstruktur** — sebagian berupa ulasan & deskripsi bebas
- **Belum terintegrasi penuh** — entitas sama bisa muncul di beberapa sumber

**Akses dataset:** [bit.ly/datasethackathon2026](https://bit.ly/datasethackathon2026)

### Ketentuan Penggunaan Dataset

#### Boleh Dilakukan
- Gunakan dataset panitia secara bermakna & dapat dijelaskan
- Membersihkan, normalisasi, deduplikasi, enrichment, embedding
- Memperkaya dengan data eksternal relevan (Toba)
- Data eksternal wajib mencantumkan sumber, lisensi & cara penggunaan

#### Tidak Diperbolehkan
- Menggunakan data personal sensitif
- Melakukan data collection yang melanggar ketentuan sumber
- Menghasilkan konten menyesatkan tanpa label jelas
- Data eksternal **tidak boleh menggantikan** dataset utama panitia

---

## 5. Pendekatan Teknis

**Tidak dibatasi pada satu teknologi** — solusi tidak harus menggunakan LLM.  
Pilih pendekatan yang paling sesuai dengan masalah yang diangkat.

| Metode | Contoh Teknik |
|--------|---------------|
| **LLM & RAG** | Prompt engineering, fine-tuning, agentic workflows |
| **Machine Learning Klasik** | Predictive modeling, ranking, clustering, classification |
| **NLP** | Sentimen, ringkasan, topic modeling, semantic search |
| **Knowledge Graph** | Entity resolution, relation extraction, data integration |
| **Geospatial AI** | Peta, rute, persebaran layanan, accessibility analysis |
| **Computer Vision** | Multimodal AI dengan data pendukung yang legal |
| **Dashboard & Decision Support** | Analytics, data copilot, API, aplikasi interaktif |

---

## 6. Luaran & Artefak Submission

### Deliverable Preliminary Round  
*(13 Juli – 2 Agustus 2026)*

Semua deliverable bersifat **Wajib** — kelengkapan artefak menjadi syarat submission valid.

| Deliverable | Isi |
|-------------|-----|
| **Deskripsi Proyek** | Problem statement, target pengguna, solusi, manfaat, diferensiasi |
| **Slide Pitching** | Problem, solution, data, AI approach, impact, demo, next steps |
| **Video Demo & Evaluasi** | 5–10 menit: eksekusi model, penjelasan performa, manfaat |
| **Repositori / Artefak Teknis** | Source code, notebook, dokumentasi, model card |
| **Ringkasan Penggunaan Data** | Dataset yang dipakai, proses transformasi, peran data |
| **Rencana Implementasi** | Rencana pengembangan, pilot test, mitigasi risiko |

### Struktur Laporan Analisis & Format Artefak

**LaporanAnalisis.pdf** wajib memuat:
1. Latar Belakang  
2. Analisis Permasalahan  
3. Desain & Indikator Keberhasilan  
4. Perencanaan Implementasi  
5. Modelling  
6. Evaluasi Model  
7. Hasil dan Pembahasan  
8. Deklarasi Penggunaan AI  

**Tiga artefak wajib diunggah:**

| File | Ketentuan |
|------|-----------|
| `[NamaTim] - LaporanAnalisis.pdf` | Maks. 25 MB |
| `[NamaTim] - Demo` (link publik) | Google Drive / YouTube, **tanpa wajah & identitas institusi** |
| `Product` (Source Code .ZIP) | Kode sumber lengkap solusi |

---

## 7. Rubrik Penilaian

**Total 100 Poin**

| Aspek Penilaian | Bobot |
|-----------------|-------|
| Kebaruan & ketajaman problem framing | 20 |
| Dampak & relevansi untuk ekosistem Toba | 20 |
| Kualitas teknis AI & rekayasa data | 20 |
| Kelayakan implementasi & keberlanjutan | 15 |
| Pemanfaatan data Toba | 15 |
| Komunikasi, demo, & dokumentasi | 10 |
| **Total** | **100** |

---

## 8. Tata Tertib

### Ketentuan Umum Peserta yang Wajib Dipatuhi

- Satu tim maksimal **3 orang**, boleh lintas sekolah/kampus
- Setiap peserta hanya boleh terdaftar di **1 (satu) tim**
- Tim wajib memiliki ketua yang dapat dihubungi aktif
- Nama Tim dan Anggota harus disebutkan (ketua + seluruh anggota)
- Judul Solusi: nama produk atau inovasi yang ringkas dan representatif
- **Tidak mencantumkan nama institusi** pada setiap file submission
- Data pendaftaran **tidak dapat diubah** setelah verifikasi
- Karya menjadi milik bersama panitia & peserta
- Panitia berhak mendiskualifikasi bila ada pelanggaran/plagiarisme
- Keputusan dewan juri & panitia bersifat **mutlak**

---

## Hadiah

| Juara | Hadiah |
|-------|--------|
| **Juara 1** | Rp 10.000.000 + Sertifikat + Merchandise |
| **Juara 2** | Rp 7.500.000 + Sertifikat + Merchandise |
| **Juara 3** | Rp 5.000.000 + Sertifikat + Merchandise |
| **Best Speaker** | Rp 1.500.000 *(Innovation and Implementation Award)* |

### Sekilas Final Round
- Lockdown session hingga **22 Agustus Pkl 12:00 WIB**
- Deploy wajib di infrastruktur **DGX B200 IT Del**
- Tanpa komunikasi dengan pihak luar
- Dress code formal (batik diperbolehkan)

---

## Kontak & Tanya Jawab

Silakan tanyakan hal-hal yang belum dijabarkan pada Guidebook & Challenge Statement.

| Channel | Kontak |
|---------|--------|
| **Email** | aicenter.itdel@gmail.com |
| **Instagram** | @puslit_ai_itdel |
| **WhatsApp** | Irwan Siagian, S.Kom — +62 813-7710-4464 |
| **WhatsApp** | Oppir Hutapea, S.Tr.Kom., M.Kom — +62 822-7242-6726 |

---

**Build Smart Solutions, Shape The Future of Tourism**  

*Del AI Hackathon 2026 | Technical Meeting*  
*Institut Teknologi Del — 25 Tahun*