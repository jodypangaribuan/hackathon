# SIPATURE Project Charter

## Preliminary Round — Scope Lock v1.0

**Status:** Scope locked, administrasi tim menunggu konfirmasi  
**Tanggal keputusan:** 28 Juli 2026  
**Deadline resmi:** 2 Agustus 2026, 20:00 WIB  
**Deadline internal:** 2 Agustus 2026, 08:00 WIB  
**Nama tim:** `[DIISI SETELAH KONFIRMASI]`  
**Ketua:** `[DIISI SETELAH KONFIRMASI]`  
**Anggota:** `[DIISI SETELAH KONFIRMASI]`

> Dokumen dan artefak submission tidak boleh mencantumkan nama, logo, atau identitas institusi pendidikan.

## 1. Nama dan Makna Solusi

**SIPATURE** diambil dari semangat *marsipature*, yaitu membenahi, membangun, dan memperbaiki. Nama ini mencerminkan tujuan produk: mengubah suara wisatawan menjadi bukti yang dapat diperiksa dan tindakan pembenahan yang bertanggung jawab.

**Catatan:** makna, ejaan, dan narasi publik nama ini masih harus divalidasi dengan penutur Batak Toba sebelum submission.

## 2. Problem Statement

Dataset pariwisata Toba memiliki ribuan rating, ulasan, metadata destinasi, fasilitas, koordinat, harga, jam operasional, dan informasi transportasi. Namun, review masih berupa teks tidak terstruktur dan informasi lintas file belum sepenuhnya terhubung. Rating rata-rata juga tidak menjelaskan masalah operasional spesifik dan dapat menyembunyikan keluhan berulang tentang kebersihan, sanitasi, sampah, akses jalan, parkir, harga, keamanan, pelayanan, dan perawatan.

Akibatnya, pengelola destinasi dan perencana pemerintah memiliki data, tetapi belum memiliki cara yang konsisten untuk menentukan:

> Masalah destinasi mana yang perlu diverifikasi terlebih dahulu, apa buktinya, seberapa yakin sistem, dan intervensi apa yang relevan?

## 3. Target Users

### Pengguna Utama

**Pengelola destinasi**, yang perlu menemukan keluhan berulang, memeriksa bukti, dan menentukan isu yang harus diverifikasi lebih dahulu.

### Pengguna Sekunder

**BPODT, pemerintah daerah, dan perencana program pariwisata**, yang memerlukan gambaran regional tentang persebaran masalah, gap fasilitas, kualitas data, dan prioritas alokasi sumber daya.

### Beneficiaries

- Wisatawan, melalui pengalaman yang lebih bersih, aman, transparan, dan terawat.
- Masyarakat lokal, melalui pengelolaan destinasi yang lebih berkelanjutan.
- Pelaku pariwisata, melalui feedback yang terstruktur dan dapat ditindaklanjuti.

## 4. Solusi dan Output Utama

SIPATURE adalah **Dashboard & Decision Support berbasis NLP, intervention ranking, data integration, dan geospatial analytics**.

Rantai utama:

```text
Raw review
-> aspect, polarity, dan severity detection
-> destination-level signal
-> verbatim evidence dan confidence
-> transparent intervention priority
-> human field verification
-> candidate intervention
```

Output produk:

- Regional overview dan intelligence map.
- Destination evidence page.
- Intervention priority queue.
- Data confidence dan provenance indicators.
- Field-verification recommendation.
- Scenario-based intervention simulator dengan asumsi eksplisit.

## 5. Scope yang Dikunci

### Termasuk

- Cleaning dan integrasi dataset panitia.
- Conservative entity resolution.
- Indonesian tourism review classification.
- Multilabel aspect detection.
- Aspect-level polarity dan negative issue severity.
- Destination aggregation dan Bayesian smoothing.
- Transparent health dan priority score.
- Geospatial issue visualization dan facility-gap context.
- Evidence, confidence, missing-data state, dan human verification workflow.
- Keyword dan TF-IDF baselines serta IndoBERT sebagai primary model yang akan dievaluasi.

### Tidak Termasuk

- General-purpose chatbot, LLM, RAG, atau agentic workflow.
- Itinerary generation.
- Booking atau payment.
- Full UMKM marketplace.
- Computer vision atau multimodal analysis.
- Real-time crowd tracking.
- Scientific water, air, biodiversity, atau pollution monitoring.
- Guaranteed causal impact prediction.
- Pernyataan bahwa destinasi pasti aman, berbahaya, bersih, atau tercemar hanya berdasarkan review.
- Login, permission kompleks, dan notification engine pada preliminary MVP.

## 6. Positioning dan Diferensiasi

SIPATURE bukan generic sentiment dashboard atau review summarizer. Nilai utamanya adalah menghubungkan:

```text
specific issue -> supporting evidence -> priority explanation
-> required verification -> candidate operational response
```

Setiap alert harus menjawab:

- Isu apa yang dilaporkan?
- Berapa review yang mendukungnya?
- Kutipan mana yang menjadi bukti?
- Apa confidence dan kecukupan datanya?
- Metadata apa yang mendukung atau bertentangan?
- Apa yang harus diverifikasi manusia?

## 7. Demo Cases yang Dikunci

### Kasus Utama — Kawah Putih Dolok Tinggi Raja

| Field | Nilai baseline saat ini |
| --- | --- |
| ID | `kawah-putih-dolok-tinggi-raja` |
| Google Maps rating | 4.0 |
| Review berteks | 47 |
| Baseline rank | 1 |
| Baseline friction score | 35.0 |
| Confidence | Medium |
| Isu utama | Harga/pungli, keamanan/sikap, akses jalan |

**Alasan pemilihan:** rating keseluruhan masih cukup tinggi tetapi review memuat sinyal berulang dan evidence kuat lintas beberapa aspek. Kasus ini menunjukkan mengapa rating rata-rata tidak cukup.

**Evidence kandidat:**

> “Biaya PungLi juga mahal, dan ditarik biaya guide yang sangat mahal...”

> “Tempatnya bagus, tetapi jalan menuju ke lokasi astaga parah banget...”

Kutipan final harus diverifikasi ulang terhadap source row dan dianonimkan sebelum digunakan.

### Backup — Bagus Bay Guest House

| Field | Nilai baseline saat ini |
| --- | --- |
| ID | `bagus-bay-guest-house` |
| Google Maps rating | 5.0 |
| Review berteks | 71 |
| Baseline rank | 3 |
| Baseline friction score | 12.2 |
| Confidence | High |
| Isu utama | Keamanan/sikap, toilet/sanitasi, kebersihan |

**Alasan pemilihan:** evidence lebih banyak dan isu berbeda dari kasus utama. Kontras rating agregat dan review negatif dapat menjadi cerita demo kuat, tetapi harus dijelaskan hati-hati karena rating dan review mungkin berasal dari snapshot/subset berbeda.

### Failure Case — Puncak Paralayang Sibodiala

| Field | Nilai baseline saat ini |
| --- | --- |
| ID | `puncak-paralayang-sibodiala` |
| Google Maps rating | 4.7 |
| Review berteks | 9 |
| Rank | Tidak diperingkat |
| Baseline friction score | 0.0 |
| Confidence | Low |

**Kegagalan yang ditunjukkan:** review menyebut jalan gelap, rusak, berbatu, terjal, dan berbahaya, tetapi baseline menghasilkan friksi nol. Kemungkinan penyebabnya adalah rating bintang lima dan mixed positive-negative clauses. Kasus ini menunjukkan kelemahan keyword + rating baseline, pentingnya clause/context understanding, minimum support, dan human oversight.

## 8. Status Teknis Saat Scope Lock

Data aplikasi saat ini mencakup 22.302 review, 12.280 review berteks, dan 320 tempat berkoordinat. Namun, skor dan label pada aplikasi saat ini berasal dari **keyword + rating baseline**, bukan output IndoBERT terlatih dan tervalidasi.

Konsekuensi:

- Nilai baseline hanya untuk prototipe UI dan exploratory signal.
- Tidak boleh diklaim sebagai performa model final.
- Demo preliminary final harus memakai model aktual atau menampilkan label baseline secara eksplisit.
- Semua hasil final wajib menggunakan locked-test evaluation.

## 9. Success Statement

SIPATURE berhasil jika tim dapat membuktikan satu rantai lengkap:

```text
Raw review
-> human-verified label
-> evaluated model prediction
-> destination signal
-> verbatim evidence
-> explainable priority
-> human-verifiable intervention
```

## 10. Kepatuhan dan Keputusan yang Belum Selesai

- [ ] Nama tim, ketua, anggota, dan eligibility terverifikasi.
- [ ] Makna/ejaan/narasi SIPATURE divalidasi penutur Batak Toba.
- [ ] Seluruh anggota menyetujui project charter.
- [ ] Seluruh anggota dapat menyampaikan pitch 30 detik secara konsisten.

## Pitch 30 Detik

> SIPATURE mengubah ribuan ulasan pariwisata Toba menjadi sinyal masalah spesifik, bukti verbatim, dan prioritas verifikasi yang transparan. Dengan NLP, integrasi data, dan analitik geospasial, SIPATURE membantu pengelola destinasi dan pemerintah mengetahui masalah mana yang perlu diperiksa lebih dahulu serta intervensi apa yang layak dipertimbangkan. SIPATURE tidak menggantikan inspeksi lapangan; sistem ini menunjukkan ke mana tim yang terbatas harus melihat terlebih dahulu berdasarkan bukti.
