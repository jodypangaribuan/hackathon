# Model Selection & Evaluasi Final

Catatan keputusan model + strategi evaluasi, agar tidak lupa arah di final.

---

## 1. Perbandingan vs SILVER — SUDAH FINAL & TERKUNCI

Hasil locked silver test (A6/A8), dievaluasi **sekali** dan tidak boleh dibuka ulang:

| Model | Macro F1 (locked silver test) | Status |
|---|---|---|
| Keyword | 0,9768 | ⚠️ sirkular (berbagi vocabulary dengan silver rules) |
| **TF-IDF** | **0,7201** / Micro 0,8040 | ✅ **dipilih untuk deteksi aspek** |
| IndoBERT (aspek) | 0,5247 | Ditolak (kalah + lebih mahal) |
| IndoBERT (polarity) | 0,7459 | Dilatih, **belum** dipakai produksi |

**Locked-test policy:** jangan buka ulang silver test untuk memilih/menyetel ulang
model. Keputusan aspek = TF-IDF sudah final.

## 2. Perbandingan vs GOLD — BENCHMARK BARU (sah)

Gold annotation (3 anggota tim) adalah benchmark **manusia yang independen** dari
silver. Ini kesempatan evaluasi jujur yang baru:

- Jalankan ketiga model (keyword, TF-IDF, IndoBERT) pada 1.320 review gold.
- Hitung F1 terhadap **label manusia** (bukan silver).
- Ini bukan re-tune — hanya inferensi + hitung F1 (cepat, tanpa training ulang).
- Cerita final: "kami bandingkan 3 model terhadap human gold, dan TF-IDF tetap
  terbaik karena X".

## 3. Keputusan produksi

| Komponen | Model saat ini | Upgrade bila gold membenarkan |
|---|---|---|
| Deteksi aspek | TF-IDF (`tfidf-aspect-silver-v1`) | Tetap, kecuali gold menunjukkan IndoBERT jauh lebih baik |
| Polarity | Lexical fallback (`lexical-polarity-v1`) | **IndoBERT polarity (0,7459)** ← kandidat upgrade utama |

Produksi yang terpasang di `sipature-api` (TF-IDF aspek + lexical polarity) tetap
jalan; upgrade hanya bila hasil gold membenarkan.

## 4. Alur setelah gold selesai

1. `annotation-agreement` + `freeze-gold` → `gold.jsonl` + Cohen's kappa.
2. Evaluasi 3 model vs gold → angka F1 terhadap manusia.
3. Update `model-card.md`, laporan, `/metode`, dan `qa-answer-bank.md`.
4. Keputusan polarity (lexical vs IndoBERT) berdasarkan hasil gold.
5. Deploy + demo + presentasi (prioritas utama final).

## 5. Yang TIDAK boleh

- Membuka ulang silver test untuk tuning/selection.
- Mengganti model produksi tanpa dasar (gold harus membenarkan).
- Mengklaim metrik gold sebelum benar-benar dihitung.
