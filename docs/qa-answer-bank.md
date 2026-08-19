# SIPATURE — Q&A Answer Bank (Final Round)

Kumpulan jawaban terstruktur untuk sesi tanya-jawab juri (10 menit). Semua angka
wajib telusur ke `docs/` dan artifact ML. Jangan mengarang angka yang tidak ada.

---

## 1. Problem Framing

### Q: Kenapa bukan sentiment dashboard biasa?
A: Sentiment dashboard hanya bilang "review ini positif/negatif". SIPATURE menjawab
pertanyaan operasional yang berbeda: **"isu mana yang harus diverifikasi dulu, dan
apa tindakan berikutnya?"**. Kami menghubungkan review → aspek → sinyal → evidence
→ prioritas yang dapat dijelaskan → kandidat intervensi. Bedanya ada di *decision
chain*, bukan di klasifikasi teks.

### Q: Kenapa tidak pakai LLM / RAG / chatbot?
A: (1) Masalahnya bukan *retrieval* atau *conversation*, tapi *prioritization* yang
tracing-friendly. (2) LLM sulit dijamin deterministik dan offline di DGX B200.
(3) Kami buktikan secara empiris bahwa TF-IDF (interpretable, deterministic, murah)
sudah cukup untuk deteksi aspek dan bahkan mengalahkan IndoBERT pada benchmark kami.
Pilihan teknologi mengikuti masalah, bukan tren.

### Q: Apa novelty-nya?
A: Mengubah ulasan yang *belum terstruktur* menjadi *early-warning signal* yang
terprioritaskan + *evidence verbatim* + *verifikasi manusia*. Dua hal yang kami
anggap baru: (1) leakage-safe split berbasis destinasi untuk entitas yang saling
terhubung via duplicate/repeated-text, dan (2) prioritas *missing-aware* yang
renormalisasi bobot bila komponen (severity/facility/feasibility) tidak tersedia —
tidak pernah menganggap data hilang sebagai kondisi sehat.

---

## 2. Data & Anotasi

### Q: Label Anda dari mana? Apa ini human-gold?
A: Ada dua lapis. **Training/baseline** memakai AI-assisted weak supervision
(silver): 3 rule-pass deterministik + konsensus 2/3 pada 1.320 review (mean
pass-agreement 0,8827) — ini *bukan* inter-annotator agreement. **Benchmark final**
memakai **human-gold** dari 3 anggota tim (A1–A3) pada sample yang sama: 1.320
record, inter-annotator agreement aspect Jaccard **0,9664**, polarity **0,9804**,
severity weighted-κ **1,0**; 117 record di-adjudikasi. Metrik gold dilaporkan
terpisah dari silver dan terikat `gold_sha256` (`7b5b6057…`).

### Q: Kenapa tidak annotate manual penuh?
A: 12.234 review berteks × 14 aspek multilabel tidak feasible untuk anotasi penuh
dalam waktu hackathon. Kami pakai weak supervision untuk membangun benchmark awal
yang deterministik, lalu memvalidasinya dengan **human-gold 3 annotator** pada
sample 1.320 review yang sama. Hasil agreement memenuhi threshold yang kami
tetapkan sebelumnya (aspect Jaccard ≥0,70 → aktual 0,9664; polarity ≥0,75 → 0,9804;
severity κ ≥0,60 → 1,0).

### Q: Bagaimana menangani imbalance / rare aspect?
A: (1) Oversampling berbobot saat sampling anotasi (rare aspect ×3, complaint ×2.5).
(2) Split leakage-safe menjamin seluruh 14 aspek muncul di validation/test.
(3) TF-IDF pakai `class_weight="balanced"`; IndoBERT pakai BCE weighted by
negatives/positives. Rare aspect tetap dilaporkan jujur (mis. `opening_hours`
support 2 di test — F1 tidak stabil, kami tidak klaim).

### Q: Kenapa cuma 1.320 review yang di-anotasi, bukan semua 12.234?
A: Karena anotasi dan inferensi adalah dua proses berbeda. Anotasi (1.320 review
= 120 pilot triple-annotated + 1.200 main) dipakai untuk **melatih** dan
**mengukur** model — bukan untuk memberi label ke seluruh data. Sisanya
(~11.000 review) tetap diproses lewat **inferensi model** (12.234 textual →
9.785 prediksi aspek), jadi dashboard tetap mencakup seluruh review. Sample 1.320
sudah representatif karena stratified (destination, rating, panjang, bahasa,
recency) + oversampling rare-aspect; dan anotasi penuh 12.234 × 14 aspek tidak
feasible untuk 3 orang. Prinsipnya: label manusia cukup untuk benchmark, model
yang menggeneralisasi ke seluruh korpus.

---

## 3. Model & Evaluasi

### Q: Kenapa TF-IDF, bukan deep learning?
A: Kami **mencoba** IndoBERT (base-p1, 124,5M param, fine-tune 4 epoch). Hasil
locked silver-test aspect Macro F1 **0,5247 vs TF-IDF 0,7201**. Pada human-gold,
TF-IDF **0,5777** vs IndoBERT **0,4254**. TF-IDF dipilih karena interpretable,
deterministik, CPU-only (latency 0,1 ms/review), dan offline. Ini bukti kami
memilih metode karena cocok, bukan karena tren.

### Q: Kenapa keyword malah lebih tinggi dari TF-IDF di human-gold?
A: Benar, keyword baseline 0,7056 > TF-IDF 0,5777 pada gold-v1. Keyword adalah
rule leksikal yang sangat dekat dengan definisi aspek di taxonomy, sehingga
cenderung cocok dengan penilaian manusia; di silver angka itu sirkular (0,9768),
di gold ia menjadi ukuran yang jujur. TF-IDF adalah model *yang dilatih* — lebih
general dan tidak bergantung lexicon, tapi pada label manusia ia belum mengungguli
keyword. Kami laporkan keduanya secara terpisah dan tidak menyembunyikan gap ini.

### Q: Tapi TF-IDF itu kan metode lama / bukan "AI"?
A: TF-IDF adalah *feature extraction*; classifier-nya adalah Logistic Regression
one-vs-rest yang *dilatih*. Pipeline kami juga melibatkan entity resolution
(fuzzy matching + union-find), kalibrasi probabilitas, dan ranking yang dapat
dijelaskan. "AI" di sini ada di *rekayasa data + evaluasi rigor*, bukan sekadar
arsitektur. Dan kami transparan: kami juga mengevaluasi IndoBERT dan menolaknya
berdasarkan metrik.

### Q: Bagaimana mencegah data leakage?
A: Split per **destination**, bukan per review. Destinasi yang terhubung lewat
technical-duplicate atau normalized repeated-text digabung (union-find) dan
ditempatkan di split yang sama. Hasil: 0 overlap destination/duplicate/
repeated-text/review di train/validation/test (922/196/202). Test terkunci
(`test_is_locked`), hanya dievaluasi **sekali** setelah model & threshold dibekukan.

### Q: Angka 0,9768 keyword itu artinya model Anda bagus banget?
A: Justru sebaliknya — angka itu **peringatan**, bukan prestasi. Keyword baseline
berbagi vocabulary dengan silver rules, jadi 0,9768 itu *sirkular* (mengukur
dirinya sendiri). Kami memakainya sebagai *ceiling* referensi, dan memilih TF-IDF
(0,7201) yang lebih independen. Pada human-gold, keyword turun ke 0,7056 — barulah
ini ukuran yang jujur terhadap penilaian manusia.

### Q: Bagaimana kalibrasi / confidence?
A: Aspect detection pakai threshold per-aspek yang di-tune di validation.
Probabilitas di-kalibrasi dengan temperature scaling (temperature 0,6, ECE 0,2021,
Brier 0,1258 di locked test). Polarity pakai fallback leksikal tanpa probabilitas
(diungkap eksplisit). Confidence di UI adalah *agreement/vote*, bukan probabilitas
terkalibrasi.

### Q: Kenapa tidak ada severity?
A: Gate support severity gagal: kelas `high` hanya 19 contoh train (< minimum 20).
Kami **menolak** melatih daripada mengklaim model yang tidak didukung. Di pipeline,
severity = `unavailable_no_supported_model` dan bobotnya direnormalisasi (missing
tidak dianggap baik).

---

## 4. Entity Resolution

### Q: Bagaimana menyatukan entitas yang sama?
A: Normalisasi nama (NFKD, casefold, diakritik) → blocking per jenis → exact match,
fuzzy (name ≥0,90 + address ≥0,65 + margin ≥0,08) auto-match, manual-review
(name ≥0,75), dan anchor cluster dengan jarak ≤500m. Hasil: 388 canonical
destination (322 anchor + 66 unresolved placeholder). Reviewed-pair precision
0,9714, recall 0,4304, false-merge rate 0,0286. Unresolved **tidak** diberi
prioritas operasional.

---

## 5. Priority Engine & Evidence

### Q: Darimana priority score?
A: Kombinasi transparan: complaint_frequency (0,20) + model_confidence (0,15) +
persistence (0,15) + visitor_exposure (0,10). Severity/facility_gap/feasibility
tidak tersedia → bobotnya dikeluarkan dan sisanya **renormalisasi**. Setiap isu
menampilkan komponen + kontribusinya (explainability).

### Q: Apakah evidence-nya bisa dipercaya?
A: Evidence adalah **kutipan verbatim** dari review (bukan generatif), dengan
aspect_probability dan provenance (source file + row). Ada evidence gate: isu tanpa
evidence tidak jadi actionable. Sensitivity analysis (+20% satu-per-satu) memberi
top-20 Jaccard 0,8182–1,0000. Tapi kami jujur: evidence belum dinilai manusia, jadi
tetap "reported issue", bukan fakta lapangan.

### Q: Bagaimana mencegah bias popularitas?
A: Exposure memakai visitor_exposure ternormalisasi (log), bukan count mentah.
Priority bukan ditentukan jumlah review semata. Data-confidence turun bila
mention rendah. Kami mendokumentasikan popularity bias sebagai limitation.

---

## 6. Responsible AI & Privasi

### Q: Bagaimana melindungi identitas reviewer?
A: Reviewer name, review ID, source file/row **tidak pernah** masuk bundle aplikasi
maupun export publik. Evidence text ditahan (`withheld_pending_privacy_review`)
sampai privacy review. Static privacy scan menolak key terlarang.

### Q: Apakah Anda tidak menjelekkan destinasi tertentu?
A: Kami sengaja memakai istilah "reported issue" dan "early-warning signal", bukan
"destinasi kotor/buruk". Setiap alert = "perlu verifikasi lapangan", bukan vonis.
Unresolved identity & insufficient data tidak diberi rank. Ada workflow rejected
alert untuk human oversight.

### Q: Apa risikonya kalau salah?
A: Risiko utama adalah reputational harm bila alert salah. Mitigasi: evidence
verbatim, confidence + data-sufficency, human verification wajib, dan satu
rejected-alert case sengaja disiapkan untuk menunjukkan oversight.

---

## 7. Simulator

### Q: Apakah simulator Anda memprediksi dampak (kausal)?
A: **Tidak, dan kami katakan eksplisit di UI.** Simulator adalah analisis skenario
non-kausal "jika isu X ditangani, bagaimana priority score berubah", berbasis
asumsi penghapusan isu. Bukan prediksi kausal, bukan jaminan dampak.

---

## 8. Deployment & Skala

### Q: Bagaimana deployment di DGX B200?
A: Docker Compose 3-service: `web` (Next.js standalone), `inference` (FastAPI +
TF-IDF), `db` (PostgreSQL 16). Offline: model & data dibundle (tidak download saat
startup). Inference TF-IDF CPU-only (<1 ms/review), jadi tidak bergantung GPU.
`sipature-ml` reproducible via CLI + config hash.

### Q: Bagaimana kalau datanya makin besar?
A: Arsitektur batch-first + SQL. TF-IDF inference dan agregasi berjalan linear.
Entity resolution memakai blocking (bukan O(n²) penuh). PostgreSQL + index untuk
query. Untuk skala jauh lebih besar, pipeline tinggal diparalelkan per batch.

### Q: Seberapa reproducible?
A: Seluruh pipeline dari raw CSV → export punya hash SHA-256 di tiap stage + config
hash + manifest. Seed 42, dependency ter-lock. Kami reproduksi penuh pipeline di
Colab (hasil identik dengan run asli). `scripts/refresh.sh` menyelaraskan seluruh
stack setelah perubahan.

---

## 9. Pilot & Keberlanjutan

### Q: Apa rencana pilot?
A: 5–10 destinasi beragam (wisata/kuliner/akomodasi), blind review oleh pengelola
sebelum melihat ranking model, verifikasi lapangan top alerts (catat
confirmed/rejected/uncertain). KPI: verification rate, time-to-verification,
intervention adoption, waktu tersimpan. Kami **tidak** menjanjikan revenue/visitor
growth untuk prototype.

### Q: Apa yang belum selesai / limitation terbesar?
A: (1) Model dilatih pada label **silver** (weak supervision); human-gold dipakai
sebagai benchmark evaluasi, bukan data training. (2) Evidence belum dinilai
manusia. (3) Severity/facility-gap/feasibility belum tersedia. (4) Analyzer
(sandbox leksikal) bukan model utama. Kami ungkap semua ini di `/metode` dan
model card.

---

## 10. Cheat Sheet Angka (hafalkan)

| Metrik | Nilai |
|---|---|
| Raw → clean reviews | 22.302 → 22.169 (12.234 textual) |
| Canonical destinations | 388 (322 anchor + 66 unresolved) |
| Entity resolution | precision 0,9714 · false-merge 0,0286 |
| Split | 922/196/202 · leakage 0 |
| TF-IDF aspect (silver locked test) | Macro F1 0,7201 · Micro 0,8040 |
| TF-IDF aspect (human-gold) | Macro F1 0,5777 · Micro 0,6910 |
| Keyword (silver, circular) | Macro F1 0,9768 |
| Keyword (human-gold) | Macro F1 0,7056 |
| IndoBERT aspect (silver locked test) | Macro F1 0,5247 |
| IndoBERT aspect (human-gold) | Macro F1 0,4254 · Micro 0,4174 |
| IndoBERT polarity | Macro F1 0,7459 (silver) · 0,5077 (gold) |
| Gold inter-annotator agreement | aspect Jaccard 0,9664 · polarity 0,9804 · severity κ 1,0 |
| Inferensi full-corpus | 9.785 prediksi · 1.682 sinyal · 103 actionable · 210 isu |
| Sensitivity | top-20 Jaccard 0,8182–1,0000 |
