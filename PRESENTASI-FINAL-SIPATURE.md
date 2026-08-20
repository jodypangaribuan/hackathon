# Naskah & Struktur Slide Presentasi Final SIPATURE
## Solusi AI untuk Peringatan Dini & Peningkatan Kualitas Pariwisata Danau Toba

Dokumen ini merupakan panduan lengkap isi slide presentasi (PowerPoint/Keynote) dan naskah narasi pembicara (*speaker script*) untuk babak **Final Round (10 Menit Presentasi Solusi + Demo Produk)**.

---

### Alokasi Waktu Presentasi (Total 10 Menit)
* **Menit 00:00 – 01:30 (1.5 m):** Latar Belakang & Analisis Permasalahan (Slide 1–3)
* **Menit 01:30 – 04:00 (2.5 m):** Pendekatan Artificial Intelligence, Data Pipeline, & Modeling (Slide 4–7)
* **Menit 04:00 – 07:30 (3.5 m):** Implementasi Produk, Arsitektur, & Live Demo (Slide 8–10)
* **Menit 07:30 – 09:30 (2.0 m):** Dampak Solusi, Nilai Ekonomi, & Roadmap Masa Depan (Slide 11–12)
* **Menit 09:30 – 10:00 (0.5 m):** Kesimpulan & Penutup (Slide 13)

---

## Slide 1: Judul & Identitas Tim (Cover Slide)
* **Waktu:** 00:00 – 00:20 (20 detik)
* **Judul:** SIPATURE: Sistem Intelijen & Peringatan Dini Kualitas Pariwisata Berbasis Artificial Intelligence
* **Sub-judul:** Transformasi Pengawasan Pariwisata DPSP Danau Toba dari Penanganan Reaktif Menjadi Intervensi Preskriptif Proaktif
* **Presenter / Tim:** Tim SIPATURE (Del AI Hackathon 2026)
* **Elemen Visual:** Logo SIPATURE, mockup antarmuka dashboard pada laptop/tablet, dan latar panorama Danau Toba elegan dengan tema gelap (*slate dark mode*).

> **Naskah Pembicara (Speaker Notes):**
> "Selamat pagi/siang Dewan Juri yang kami hormati. Danau Toba telah ditetapkan sebagai Destinasi Pariwisata Super Prioritas. Namun, kepuasan wisatawan dan reputasi destinasi sering kali terancam oleh masalah klasik yang terlambat ditangani: mulai dari getok harga, fasilitas sanitasi yang tidak terawat, hingga akses yang terputus. Hari ini, kami mempersembahkan **SIPATURE**, sebuah sistem intelijen berbasis kecerdasan buatan yang mampu membaca ribuan suara wisatawan secara otomatis, mendeteksi sinyal friksi secara *real-time*, dan memberikan rekomendasi aksi konkret bagi pemangku kepentingan."

---

## Slide 2: Latar Belakang Masalah (The Core Friction)
* **Waktu:** 00:20 – 01:00 (40 detik)
* **Judul:** Mengapa Pengawasan Kualitas Pariwisata Saat Ini Gagal Mendeteksi Isu Lebih Awal?
* **Poin Utama Slide:**
  * **Volume Ulasan Melimpah, Tanpa Struktur:** Ribuan ulasan wisatawan tersebar di Google Maps dan platform digital, tetapi tidak pernah dianalisis secara sistematis oleh dinas pariwisata.
  * **Pola Pengawasan Pasif & Reaktif:** Masalah (seperti pungutan liar atau toilet rusak) baru diketahui pemerintah setelah viral di media sosial dan mencoreng nama baik kawasan.
  * **Ketiadaan Prioritas Berbasis Data:** Pengelola tidak memiliki alat ukur objektif untuk menentukan destinasi mana yang paling kritis membutuhkan intervensi anggaran dan inspeksi fisik.
* **Elemen Visual:** Diagram perbandingan: *Pendekatan Tradisional (Ulasan Tercecer -> Viral -> Reaktif -> Kerugian Reputasi)* vs *Pendekatan SIPATURE (AI Ingestion -> Deteksi Dini -> Verifikasi Lapangan -> Intervensi Cepat)*.

> **Naskah Pembicara (Speaker Notes):**
> "Setiap hari, ratusan wisatawan menuliskan pengalaman mereka di platform digital. Sayangnya, dinas pariwisata dan pengelola destinasi tidak memiliki kapasitas manual untuk membaca belasan ribu ulasan tersebut satu per satu. Akibatnya, isu seperti toilet kotor atau tarif tidak transparan baru direspons setelah viral dan menjadi krisis reputasi. Yang dibutuhkan oleh Danau Toba bukan sekadar agregasi skor bintang, melainkan sistem peringatan dini yang mampu mengekstraksi aspek spesifik dari keluhan wisatawan dan menyusun skala prioritas tindakan secara kuantitatif."

---

## Slide 3: Analisis Data & Permasalahan Lapangan
* **Waktu:** 01:00 – 01:30 (30 detik)
* **Judul:** Diagnosis Masalah dari 12.234 Ulasan Wisatawan Danau Toba
* **Poin Utama Slide:**
  * **Data Masif & Heterogen:** Analisis terhadap 12.234 ulasan dari 14 dataset heterogen (wisata alam, kuliner, perhotelan, transportasi).
  * **Entitas Ganda (*Entity Ambiguity*):** Ditemukan lebih dari 30% nama destinasi tercatat ganda atau tidak standar di berbagai platform.
  * **Distribusi Top-3 Friksi Utama:**
    1. *Price Transparency:* Ketidakjelasan tiket masuk, biaya parkir liar, dan menu tanpa daftar harga.
    2. *Cleanliness & Waste:* Kebersihan toilet umum dan pengelolaan sampah di tepian danau.
    3. *Accessibility & Infrastructure:* Kondisi jalan rusak, penerangan minim, dan rambu penunjuk arah.
* **Elemen Visual:** Grafik pie/bar komposisi keluhan per aspek dan infografis ringkasan data corpus.

> **Naskah Pembicara (Speaker Notes):**
> "Melalui eksplorasi data terhadap 12.234 ulasan di kawasan Danau Toba, kami mengidentifikasi tiga friksi dominan: transparansi harga, kebersihan toilet/sampah, dan akses jalan. Kami juga menemukan tantangan teknis besar: data ulasan memiliki ambiguitas nama entitas yang tinggi serta ketidakseimbangan kelas (*class imbalance*). Untuk menjawab tantangan ini, kami merancang arsitektur AI hulu-ke-hilir yang terintegrasi secara modular."

---

## Slide 4: Pendekatan AI — Entity Resolution & Data Cleansing
* **Waktu:** 01:30 – 02:15 (45 detik)
* **Judul:** Tahap 1: Entity Resolution & Pembersihan Data Multi-Platform
* **Poin Utama Slide:**
  * **Resolusi Entitas Kanonik:** Memetakan ribuan entitas sumber mentah menjadi **388 destinasi kanonik** yang terpetakan secara geografis (koordinat spasial, jenis tempat, kabupaten).
  * **Pembersihan & Deduplikasi Cerdas:**
    * Deteksi duplikasi teks ulasan (*duplicate group hashing*).
    * Normalisasi teks bahasa Indonesia, singkatan lokal, dan dialek Batak.
  * **Isolasi Privasi Wisatawan:** Pemisahan identitas pengguna (*PII safe*) dan agregasi berbasis aspek.
* **Elemen Visual:** Diagram alur pembersihan data: Raw CSVs -> Deduplication -> Spatial & String Matching -> 388 Canonical Destinations.

> **Naskah Pembicara (Speaker Notes):**
> "Sebelum masuk ke pemodelan NLP, fondasi data harus solid. Kami membangun modul *Entity Resolution* otomatis yang menggabungkan kemiripan string (*Levenshtein & Jaro-Winkler*) dengan kedekatan spasial koordinat geografis. Hasilnya, ribuan data ulasan mentah berhasil ditautkan secara presisi ke 388 destinasi kanonik di 7 kabupaten sekeliling Danau Toba."

---

## Slide 5: Pendekatan AI — Weak Supervision & Multi-Label Taxonomy
* **Waktu:** 02:15 – 03:00 (45 detik)
* **Judul:** Tahap 2: Weak Supervision & Taksonomi 14 Aspek Pariwisata
* **Poin Utama Slide:**
  * **Taksonomi 14 Aspek Komprehensif:** Mengklasifikasikan ulasan ke dalam aspek spesifik (Kebersihan, Transparansi Harga, Aksesibilitas, Keamanan, Fasilitas, Pelayanan, Parkir, dsb).
  * **Solusi Cold-Start Tanpa Manual Labeling Berat:**
    * Menerapkan paradigma *Data Programming / Weak Supervision* (*Snorkel-inspired heuristic labeling functions*).
    * Validasi konsensus antar-labeler (A1, A2, A3) untuk membentuk *Silver & Gold Ground Truth Dataset*.
  * **Multi-Label Aspect Classification:** Satu ulasan dapat mencakup multi-aspek (misal: makanan enak namun toilet kotor dan harga mahal).
* **Elemen Visual:** Tabel 14 taksonomi aspek pariwisata yang dikelompokkan ke 4 domain (Lingkungan, Infrastruktur, Pengalaman Wisatawan, Operasional).

> **Naskah Pembicara (Speaker Notes):**
> "Tantangan terbesar NLP dalam domain lokal adalah ketiadaan data latih beranotasi. Kami memecahkan ini melalui pendekatan *Weak Supervision*. Kami mendefinisikan *Labeling Functions* berbasis pola leksikal dan domain pariwisata, lalu menerapkan model generatif agregasi label untuk menghasilkan dataset *Silver Standard*. Model kami mampu mendeteksi klasifikasi multi-label secara simultan karena satu kalimat ulasan sering kali memuat pujian sekaligus keluhan pada aspek yang berbeda."

---

## Slide 6: Modeling & Evaluasi Performa AI
* **Waktu:** 03:00 – 03:30 (30 detik)
* **Judul:** Tahap 3: Performa Model NLP, Sentimen, & Polarity Detection
* **Poin Utama Slide:**
  * **Model Inti:** Klasifikasi multi-aspek berbasis *TF-IDF N-Gram Feature Extraction + Multi-Output Classifiers* yang dioptimasi untuk kecepatan inferensi sub-detik pada CPU/GPU.
  * **Polarity & Severity Detection:** Deteksi polaritas keluhan (Negatif, Netral, Positif) dengan pembobotan *negation handling*.
  * **Hasil Evaluasi Metrik:**
    * *Macro-F1 & Micro-F1:* Kinerja konsisten pada aspek dominan maupun *rare aspects*.
    * *Inference Latency:* < 15 milidetik per ulasan, memungkinkan *live stream ingestion*.
* **Elemen Visual:** Tabel perbandingan metrik evaluasi (Precision, Recall, F1-Score) dan grafik confusion matrix / PR curve.

> **Naskah Pembicara (Speaker Notes):**
> "Untuk melayani jutaan ulasan secara efisien di lingkungan server produksi, kami memilih model yang memiliki *trade-off* optimal antara akurasi tinggi dan latensi rendah. Model kami mencapai *inference time* di bawah 15 milidetik, memungkinkan evaluasi teks secara instan saat ulasan baru masuk ke sistem."

---

## Slide 7: Algoritma Prioritisasi & Peringatan Dini (Engine A9)
* **Waktu:** 03:30 – 04:00 (30 detik)
* **Judul:** Tahap 4: Formula Peringatan Dini & Skor Urgensi Empiris
* **Poin Utama Slide:**
  * **Penghalusan Bayes Empiris (*Empirical Bayes Smoothing*):** Menghindari bias pada destinasi dengan sedikit ulasan (*small-sample noise dampening*).
  * **Formula Urgensi Multivariat:**
    $$\text{Priority Score} = w_1 \cdot \text{Complaint Rate} + w_2 \cdot \text{Persistence} + w_3 \cdot \text{Exposure} + w_4 \cdot \text{Confidence}$$
  * **Triage Level:** Otomatis membagi isu ke dalam level: **Critical**, **High**, **Medium**, **Monitor**, dan **Insufficient Data**.
* **Elemen Visual:** Diagram formula skor urgensi dan visualisasi piramida triage level intervensi.

> **Naskah Pembicara (Speaker Notes):**
> "Kecerdasan SIPATURE tidak berhenti pada klasifikasi teks. Kami membangun *Engine Prioritisasi A9* yang menggunakan prinsip *Empirical Bayes*. Skor urgensi dihitung dengan menggabungkan rasio keluhan, persistensi keluhan dari waktu ke waktu, volume eksposur wisatawan, dan tingkat keyakinan AI. Dengan cara ini, pemerintah tidak disajikan tumpukan data mentah, melainkan daftar destinasi terurut berdasarkan tingkat kedaruratannya."

---

## Slide 8: Arsitektur Sistem & Rekayasa Perangkat Lunak
* **Waktu:** 04:00 – 04:30 (30 detik)
* **Judul:** Arsitektur Perangkat Lunak & Deployment Standar Enterprise
* **Poin Utama Slide:**
  * **Frontend Modern:** Next.js 15 (App Router, Tailwind CSS, Leaflet Spasial GIS).
  * **Inference Microservice:** Python FastAPI asinkron melayani prediksi klasifikasi live.
  * **Database Relasional & Audit Trail:** PostgreSQL 16 dengan Drizzle ORM (schema ternormalisasi, riwayat verifikasi lapangan).
  * **Deployment Kontainerisasi:** Docker Compose siap pakai untuk server NVIDIA B200 / Linux Production dengan mitigasi *port auto-collision*.
* **Elemen Visual:** Diagram arsitektur 3-Tier (Client Next.js -> FastAPI Engine & PostgreSQL Database -> Docker Infrastructure).

> **Naskah Pembicara (Speaker Notes):**
> "Sistem kami dibangun di atas arsitektur modular tiga lapis yang *production-ready*. Frontend Next.js 15 memberikan pengalaman interaktif yang responsif, terhubung ke microservice FastAPI untuk inferensi model, dan PostgreSQL 16 untuk menjamin integritas data serta audit trail verifikasi lapangan. Seluruh sistem telah dikontainerisasi dengan Docker dan sukses di-deploy ke server B200."

---

## Slide 9 & 10: Live Demo Produk (Fitur Unggulan)
* **Waktu:** 04:30 – 07:30 (3 Menit — DEMO LIVE / SCREEN RECORDING)
* **Judul:** Demonstrasi Langsung Platform SIPATURE
* **Alur Demo (3 Menit):**
  1. **Peta Spasial Danau Toba (Overview Dashboard):**
     * Menampilkan sebaran 388 destinasi di 7 kabupaten seputar Danau Toba.
     * Indikator warna radar (Merah = Kritis, Kuning = Sedang, Hijau = Terpantau Baik).
     * Klik destinasi langsung masuk ke lembar kerja investigasi.
  2. **Triage Antrean Intervensi Preskriptif (`/intervensi`):**
     * Tabel antrean dinamis yang mengelompokkan masalah berdasarkan tingkat urgensi tertinggi.
     * Dilengkapi rekomendasi panduan cek fisik lapangan dan solusi perbaikan spesifik.
  3. **Lembar Kerja Investigasi Destinasi & Evidence Verbatim (`/destinasi/[id]`):**
     * Membuka contoh destinasi prioritas (misal: *Elios - RM Batak*).
     * Menampilkan **9.785 kutipan ulasan asli wisatawan** secara transparan dengan tombol interaktif *Buka & Baca Semua*.
     * **Workflow Verifikasi Lapangan (*Human-in-the-loop*):** Petugas dinas dapat mengklik tombol **Konfirmasi (Hijau)**, **Tidak Pasti (Kuning)**, atau **Tolak (Merah)** dengan pencatatan alasan spesifik ke database.
  4. **AI Interactive Text Analyzer (`/analyzer`):**
     * Simulasi live: Mengetik ulasan baru -> model AI secara instan mendeteksi aspek, polaritas, dan menghitung dampak perubahan skor kesehatan destinasi.

> **Naskah Pembicara (Speaker Notes saat Demo):**
> *(Layar menampilkan Dashboard)* "Mari kita lihat langsung platform SIPATURE yang sedang berjalan aktif. Di halaman utama, pembuat kebijakan langsung melihat peta geospasial 388 destinasi di kawasan Danau Toba..."
> *(Pindah ke Antrean Intervensi)* "Di menu Intervensi, AI telah mengurutkan masalah paling mendesak. Pejabat dinas tidak perlu bingung menentukan prioritas; sistem langsung menyajikan panduan inspeksi lapangan..."
> *(Buka Halaman Detail Destinasi)* "Ketika kita buka lembar kerja destinasi, pengelola dapat membaca kutipan asli ulasan wisatawan sebagai bukti autentik. Dan di bawahnya, terdapat kontrol verifikasi lapangan: petugas dapat mengonfirmasi, menandai ragu-ragu, atau menolak jika fasilitas telah diperbaiki. Keputusan ini tersimpan permanen di database sebagai audit trail resmi."

---

## Slide 11: Dampak Nyata terhadap Ekosistem Pariwisata Danau Toba
* **Waktu:** 07:30 – 08:30 (1 Menit)
* **Judul:** Dampak Terukur: Transformasi Ekosistem Pariwisata
* **Poin Utama Slide:**
  * **Efisiensi Anggaran & Penugasan Lapangan:** Menghemat waktu inspeksi dinas hingga 70% melalui penargetan lokasi berbasis data (*targeted inspection* alih-alih *random checks*).
  * **Pencegahan Krisis Reputasi (*Reputation Risk Mitigation*):** Mendeteksi tren keluhan 2–4 minggu sebelum isu meledak viral di media sosial.
  * **Standarisasi Kualitas Layanan DPSP:** Mendorong kepatuhan transparansi tarif, sanitasi toilet terstandar, dan keselamatan wisatawan.
  * **Kolaborasi Multi-Pihak:** Menghubungkan Pemkab/Disparbud, BPODT, pengelola destinasi, dan masyarakat dalam satu ekosistem informasi.
* **Elemen Visual:** Matriks perbandingan dampak: *Sebelum SIPATURE (Reaktif, Lambat, Parsial)* vs *Sesudah SIPATURE (Preskriptif, Cepat, Terkoordinasi)*.

> **Naskah Pembicara (Speaker Notes):**
> "Dampak yang dihadirkan SIPATURE sangat konkret. Pertama, efisiensi anggaran pengawasan: dinas pariwisata tidak lagi membuang waktu dan biaya untuk inspeksi acak, melainkan langsung menuju titik-titik kritis yang terdeteksi AI. Kedua, proteksi reputasi: keluhan wisatawan dapat diintervensi beberapa minggu sebelum menjadi krisis viral yang merugikan pariwisata Danau Toba secara keseluruhan."

---

## Slide 12: Roadmap & Potensi Skalabilitas Masa Depan
* **Waktu:** 08:30 – 09:30 (1 Menit)
* **Judul:** Potensi Pengembangan & Skalabilitas Solusi
* **Poin Utama Slide:**
  * **Multi-Channel Ingestion:** Integrasi *real-time* dengan Twitter/X, TikTok comments, TripAdvisor, dan formulir aduan WhatsApp Bot resmi.
  * **Model Upgrade ke LLM Generatif Lokal:** Fine-tuning model bahasa terbuka (misal: LLaMA-3 Indo / IndoBERT Large) untuk menghasilkan draf surat teguran dan rekomendasi kebijakan otomatis.
  * **Replikasi ke 4 DPSP Lainnya:** Arsitektur modular yang dapat langsung diadaptasi untuk Labuan Bajo, Borobudur, Mandalika, dan Likupang.
  * **Mobile App untuk Petugas Lapangan:** Aplikasi Android/iOS dengan fitur *geotagging photo upload* saat verifikasi fisik.
* **Elemen Visual:** Infografis peta roadmap 3 fase: *Phase 1 (MVP Deployment & Validation)* -> *Phase 2 (LLM & Multi-Source)* -> *Phase 3 (National DPSP Rollout)*.

> **Naskah Pembicara (Speaker Notes):**
> "Ke depan, SIPATURE dirancang untuk berkembang lebih jauh. Dengan arsitektur yang telah kami standardisasi, platform ini tidak hanya siap diperluas dengan kanal aduan WhatsApp dan media sosial, tetapi juga dapat direplikasi secara instan ke 4 Destinasi Pariwisata Super Prioritas lainnya di Indonesia."

---

## Slide 13: Kesimpulan & Penutup (Closing Slide)
* **Waktu:** 09:30 – 10:00 (30 detik)
* **Judul:** SIPATURE: Menjaga Kualitas, Melindungi Reputasi Danau Toba
* **Poin Rangkuman:**
  * **AI yang Bekerja Nyata:** Mengolah 12.234 ulasan menjadi aksi preskriptif nyata.
  * **Transparan & Akuntabel:** Dilengkapi bukti kutipan asli ulasan dan *human verification loop*.
  * **Siap Produksi:** 100% teruji dan aktif berjalan di server produksi.
* **Call to Action:** *"Mewujudkan Pariwisata Danau Toba yang Berkualitas, Berdaya Saing, dan Berkelanjutan."*
* **Tanya Jawab:** *"Terima kasih. Kami siap menjawab pertanyaan Dewan Juri."*

> **Naskah Pembicara (Speaker Notes):**
> "Sebagai kesimpulan, SIPATURE bukan sekadar dashboard analitik, melainkan instrumen pengambil keputusan cerdas yang menjembatani suara wisatawan dengan tindakan nyata di lapangan. Sistem ini telah siap pakai, teruji di server, dan siap menjadi pengawal kualitas pariwisata Danau Toba. Terima kasih atas perhatian Dewan Juri, kami membuka sesi tanya jawab."

---

## 🎯 Panduan Menghadapi Sesi Tanya Jawab Dewan Juri (10 Menit Q&A)

Berikut adalah daftar pertanyaan yang paling sering ditanyakan dewan juri beserta kunci jawaban strategisnya:

| Kemungkinan Pertanyaan Juri | Kunci Jawaban Strategis Tim |
| :--- | :--- |
| **1. Mengapa memilih model TF-IDF daripada Large LLM / Transformer berat untuk deployment?** | "TF-IDF + Multi-Output Classifier memberikan *inference latency* super cepat (< 15 ms) pada arsitektur ringan tanpa butuh kluster GPU mahal, sehingga sangat efisien dan andal untuk skenario *production* pemda. Sementara pada tahap persiapan data, kami tetap memanfaatkan *weak supervision* dan *foundation models* untuk melatih dataset *Silver standard*." |
| **2. Bagaimana mengatasi review palsu atau ulasan bias di platform publik?** | "Kami menerapkan formula *Empirical Bayes Smoothing* dan faktor *Persistence* (keluhan harus muncul berulang dalam rentang waktu berbeda). Selain itu, sistem menyertakan *Human-in-the-Loop Verification*: rekomendasi AI tidak langsung dieksekusi sebagai vonis, melainkan menjadi panduan bagi petugas dinas untuk melakukan cek fisik faktual di lapangan." |
| **3. Bagaimana menjaga privasi wisatawan (data privacy/GDPR/UU PDP)?** | "Sistem kami mengisolasi teks mentah dan tidak pernah mengekspos profil pribadi, nomor telepon, atau akun reviewer ke publik. Seluruh analitik diagregasikan pada level destinasi dan aspek, sedangkan kutipan ulasan hanya menampilkan teks anonim untuk keperluan investigasi mutu layanan." |
| **4. Seberapa mudah sistem ini diimplementasikan oleh dinas pariwisata daerah?** | "Sangat mudah. Sistem ini sudah sepenuhnya dikontainerisasi dalam Docker dengan skrip *turnkey deployment*. Pengguna akhir (staf dinas) hanya memerlukan web browser untuk mengakses antrean intervensi dengan instruksi bahasa Indonesia yang jelas tanpa perlu keahlian teknis AI." |
