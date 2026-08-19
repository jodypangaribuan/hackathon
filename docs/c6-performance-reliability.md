# C6 — Performance & Reliability Report

**Tanggal:** 2026-08-19
**Lingkungan:** Docker/OrbStack lokal (macOS) — identik dengan target DGX B200
**App:** CPU-only (TF-IDF + lexical polarity), 3-service (`web` + `inference` + `db`)

Hasil pengukuran dan uji ketahanan untuk Final Round. Semua angka diukur pada
deployment lokal yang menyamai DGX (B2 rehearsal), bukan pada GPU.

## 1. Latency

| Endpoint | p50 | p95 | mean | max |
|---|---|---|---|---|
| `/predict-review` (FastAPI, TF-IDF) | 2,1 ms | 3,1 ms | 2,8 ms | 55,6 ms (warmup pertama) |
| `/api/analyze` (Next.js → FastAPI) | 6,5 ms | 9,8 ms | 6,9 ms | 9,8 ms |

- 100 request `/predict-review` → 100% OK.
- Latency log per-request tersedia tanpa PII (`latency_ms`, `input_chars`).

## 2. Memory & Page Load

| Service | Memori |
|---|---|
| `web` (Next.js standalone) | 95,5 MiB |
| `inference` (FastAPI) | 132,6 MiB |
| `db` (PostgreSQL 16) | 22,7 MiB |

| Halaman | Load |
|---|---|
| `/` (overview) | 0,145 s |
| `/intervensi` | 0,077 s |
| `/destinasi/{id}` | 0,055 s |

GPU memory: N/A (aplikasi tidak memakai GPU).

## 3. Input & Request Robustness

- Empty → 400/422; non-string → 422; >5000 char → 422 (lihat `sipature-api/tests`).
- 100 request berulang → stabil tanpa error.

## 4. Failure & Fallback

| Kegagalan | Perilaku | Status |
|---|---|---|
| Service inference mati | `/api/analyze` turun ke `mode: baseline` (sandbox leksikal) | ✅ verified |
| Tile peta eksternal gagal | turun ke `TobaMapFallback` (SVG luring, nol jaringan) | ✅ code-verified |
| DB mati | aplikasi 500; recovery via `docker compose restart db` / re-seed (`dgx-deployment-runbook.md` §8) | ⚠️ tanpa fallback in-app |

## 5. Offline

- Model TF-IDF + data precomputed di-bundle ke image (tidak download saat startup).
- Satu-satunya dependensi eksternal = tile peta (degradasi ke SVG luring).
- Demo berjalan penuh tanpa internet eksternal.

## 6. Precomputed Demo Data

- `sipature-app/src/data/generated/{places,interventions,corpus}.json` — privacy-safe
  bundle hasil A9 (`a9-tfidf-lexical-v1.0.4`), di-seed ke Postgres oleh `db:seed`.
