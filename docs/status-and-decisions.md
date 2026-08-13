# SIPATURE — Status & Keputusan (Handoff Log)

Dokumen ini adalah catatan komprehensif sesi kerja 13–14 Agustus 2026: apa yang
dikerjakan, keputusan yang diambil, status terkini, dan arah ke depan. Tujuannya
agar tim tidak lupa dan tidak keluar arah. Append saja ke bawah bila ada
perubahan; jangan menulis ulang bagian historis.

---

## 1. Ringkasan Sesi

Sesi ini berhasil **mereproduksi seluruh pipeline ML (A1–A9) secara deterministik**
di Google Colab, lalu **mengintegrasikan model ke produk** melalui service
FastAPI + Docker, dan **meregenerasi data dashboard** dari export A9 baru.

Hasil terpenting: semua metrik ML identik dengan run original
(`20260801-…`), membuktikan reproducibility kuat — argumen penting untuk juri.

---

## 2. Keputusan Kunci (Jangan Diubah Tanpa Alasan)

| # | Keputusan | Alasan | Catatan |
|---|---|---|---|
| 1 | **Expert review eksternal DIBATALKAN** | Tidak memungkinkan minta reviewer luar | Diganti: sensitivity analysis + gold annotation tim |
| 2 | **Gold annotation = 3 anggota tim sendiri** | Menutup kelemahan "silver bukan gold" | Pakai `annotation-agreement`/`freeze-gold` yang sudah ada |
| 3 | **TF-IDF (0.72) > IndoBERT (0.52) untuk aspek** | Model lebih baik + interpretable + offline + cheap | Cerita jujur: "pilih model sesuai masalah, bukan tren" |
| 4 | **IndoBERT polarity (0.7459) BELUM dipakai di produksi** | A9 pakai `lexical-polarity-v1` (CPU, deterministic) | Potensi upgrade ke depan (butuh GPU) |
| 5 | **FastAPI untuk inference, Next.js untuk frontend** | Model Python tidak bisa jalan di Node | Arsitektur 2-service: `web` + `inference` |
| 6 | **Model TF-IDF = `a10bddb1…` (baru), bukan `9132efbf…` (lama)** | Notebook 05 melatih ulang, hash berubah | `a9.yaml` + `generate-product-data.mjs` sudah diupdate |
| 7 | **Severity TIDAK tersedia** | Gate support gagal (high=19 < 20) | Jangan pernah klaim severity |

---

## 3. Timeline Kerja (13–14 Agustus 2026)

### 3.1 Infrastruktur
- Init **codebase-memory MCP**: index repo (`sipature`, 2452 nodes), buat ADR,
  tambah `.codebase-memory/` ke `.gitignore`.

### 3.2 Reproduksi pipeline ML (Colab, notebook 01–09)

Semua notebook dibuat/dirapikan dengan konvensi: **step marker (`## Step N`)**,
**config cell**, **guard immutable output**, dan **run summary**.

| Notebook | Hasil | Konsisten dgn run asli? |
|---|---|---|
| 01 EDA + inventory | 14 CSV, 16 figures | ✓ |
| 02 Cleaning + ER | 22.302→22.169 clean, 388 destinations (322 anchor + 66 unresolved) | ✓ |
| 03 Sampling + silver | 1.320 records (489 consensus/497 no-support/334 review-rec) | ✓ |
| 04 Split | 922/196/202, leakage 0, terkunci | ✓ |
| 05 Baselines | Keyword 0.9768, TF-IDF 0.7201 | ✓ |
| 06 IndoBERT train | aspect 0.4012, polarity 0.7044, severity skip | ✓ |
| 07 (ex-08) A8 | aspect 0.5247, polarity 0.7459, ECE 0.2021 | ✓ |
| 08 A9 inference+agg | 9.785 prediksi, 1.682 sinyal, 280 dest | ✓ |
| 09 A9 prioritize+export | 388 dest, 103 actionable, 210 issue, `app-export.json` | ✓ |

Catatan teknis penting:
- Notebook 07 (stub polarity/severity) **dihapus**; 08 di-rename jadi 07.
- Setiap run GPU (06, 07) butuh **T4 GPU** + restart setelah install (numpy cache).
- Split manifest dibuat ulang → hash manifest berubah (field `locked_at`), tapi
  hash `train`/`validation`/`test` deterministik (sama).

### 3.3 Integrasi produk
- Update `a9.yaml` hash model TF-IDF → `a10bddb1…` (model) + `072b4346…` (manifest).
- Buat service **`sipature-api/`** (FastAPI, struktur clean: config/schemas/service/routers/dependencies).
  - `GET /health`, `POST /predict-review` (load `model.joblib` via `load_tfidf_contract`).
- Update `docker-compose.yml` → 3 service: `web` (Next.js) + `inference` (FastAPI) + `db` (PostgreSQL 16).
- Wiring: `/api/analyze` proxy ke FastAPI (`INFERENCE_URL`), fallback ke sandbox leksikal.
- Regenerate data dashboard dari export A9 baru (`8037d072…`).
- Tambah **`.env` / `.env.example`** (config terpusat, credential tidak di-commit).
- Buat **schema PostgreSQL** (`sipature-app/db/schema.sql`) + **Drizzle ORM** (`src/db/schema.ts`, `src/db/index.ts`, `drizzle.config.ts`).
- Setup **rclone** untuk sinkronisasi Drive ↔ lokal (`scripts/sync-drive.sh pull/push`).

### 3.4 Dokumentasi
- Update `SIPATURE-Hackathon-TODO.md` (F1–F3 checklist + gap items).
- Selaraskan 8 file docs/report terkait keputusan expert-review & gold annotation.
- Tambah section "Local ↔ Drive Sync (rclone)" di `docs/reproducibility-runbook.md`.

---

## 4. Status Terkini (Apa yang Sudah Jalan)

### ML Pipeline — ✅ SELESAI & konsisten
| Stage | Status |
|---|---|
| A1 Inventory/EDA | ✅ |
| A2 Cleaning/ER | ✅ |
| A3 Annotation (silver) | ✅ |
| A4 Split | ✅ |
| A5 Baselines | ✅ |
| A6 IndoBERT | ✅ |
| A7 Calibration + locked test | ✅ |
| A8 Inference + aggregation | ✅ |
| A9 Prioritization + export | ✅ |

### Produk — ✅ Jalan lokal (Docker)
```bash
cd sipature-app && docker compose up -d --build
# web        : http://localhost:3000  (Next.js)
# inference  : http://localhost:8000  (FastAPI)
# db         : postgres:16-alpine :5432 (schema auto-init)
```
- Analyzer: live model (TF-IDF, `mode: "production"`).
- Dashboard/map: **live query** dari PostgreSQL via Drizzle (`src/lib/data.ts` async).
- DB: schema + Drizzle ORM aktif; seed via `npm run db:seed`.

### Prasyarat build ulang (jangan lupa)
1. Model TF-IDF baru (`a10bddb1…`) harus ada di `ml/artifacts/models/tfidf-aspect-silver-v1/` (atau `scripts/sync-drive.sh pull`).
2. Data `src/data/generated/*.json` harus ada (jangan di-`gitignore` dari Docker build).
3. `cp .env.example .env` sebelum `docker compose up` (jika belum ada).

---

## 5. Sisa Pekerjaan (Arah ke Depan, Prioritas)

### Wajib untuk Final (21–22 Agustus)
1. **DGX B200 deployment** (C5) — build image, verifikasi GPU, cold start.
2. **Offline demo** (C6) — tanpa internet eksternal.
3. **Presentasi 10 menit + demo script** (C8).
4. **Q&A answer bank** (C9) — leakage, Macro F1, reputational harm, dll.

### Gap ML (nilai tambah, bukan blocker)
| Item | Rubrik | Status |
|---|---|---|
| Gold annotation 3 anggota tim | D3 | Belum |
| Facility gap analysis (`Fasilitas`) | D5 | Belum |
| Integrasi transportasi | D5 | Belum |
| IndoBERT polarity di produksi | D3 | Belum (opsional) |
| Error analysis manual (FP/FN) | D3 | Belum |
| Model card | D6 | Belum (draft) |
| Impact quantification (KPI) | D2 | Belum |

---

## 6. North Star (Arah yang Harus Dipegang)

```text
Raw review → cleaned/linked → silver labels → model (TF-IDF aspek + lexical polarity)
→ calibrated → destination signal → verbatim evidence → explainable priority
→ human verification → candidate intervention
```

**Yang TIDAK boleh:**
- Klaim metric yang belum diukur (severity, expert, human-gold).
- Sebut keyword baseline sebagai IndoBERT terlatih.
- Pakai locked test untuk tuning.
- Tampilkan reviewer identity / institusi.
- Butuh internet/model download saat demo final.
