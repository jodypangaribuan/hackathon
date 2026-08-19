# DGX B200 Deployment Runbook

Panduan deploy step-by-step untuk final round di DGX B200. Diisi dari hasil
**staging rehearsal** (2026-08-19, macOS + Docker/OrbStack, CPU) + **ketentuan
panitia** (Technical Meeting 19 Agustus 2026). Saat final tinggal **salin-tempel**
persis.

> Rehearsal dijalankan dengan Docker 29.4.0 / Compose v5.1.2. Di DGX (Linux)
> mesin Docker-nya native, command-nya identik. Aplikasi CPU-only (TF-IDF),
> GPU B200 tidak dipakai untuk inference.

---

## A. Infrastruktur DGX (dari panitia)

- **OS:** Ubuntu 22.04 LTS · Python 3.10.12 · GCC/G++ 11.4.0 · CUDA 12.4/12.8
- **GPU:** 1× MIG NVIDIA B200 (VRAM 45 GB) — **tidak dipakai** (app CPU-only).
- **Akses SSH:** `ssh <team_name>@<IP> -p <Port>` (kredensial diberikan panitia saat registrasi 21 Agustus).
- **Transfer file:** SFTP (WinSCP/FileZilla) dari laptop → server. Gunakan SFTP, **bukan `git clone`** (device peserta tanpa internet).
- **Direktori:** `/workspace` (private, tempat project/source) · `/data` (dataset read-only).
- **Internet:** server DGX **punya akses internet** (bisa `docker pull`/`pip install`); device peserta tidak.
- **Docker:** ⚠️ wajib konfirmasi ke admin HPC apakah Docker + Compose terpasang / diizinkan (custom image perlu formulir pengajuan). **Pastikan sebelum lockdown.**

## B. Checklist sebelum lockdown (kerjakan SEKARANG)

- [ ] Konfirmasi ke panitia/admin HPC: Docker Engine + Compose terpasang di server DGX? Versi?
- [ ] Siapkan kredensial SSH + port tim (didapat saat registrasi).
- [ ] Siapkan arsip repo (source code) untuk di-SFTP ke `/workspace`.

---

## 0. Prasyarat & asumsi

- [ ] Docker Engine + Compose plugin terpasang di DGX (`docker --version`, `docker compose version`).
- [ ] Akses network internal; port yang dibuka: `3000` (web), `8000` (inference), `5432` (db, internal saja).
- [ ] Model TF-IDF `a10bddb1432d93e9b041c6821e669001c5db8b8fd372b519f6f31b0111aac7ce` ada di `ml/artifacts/models/tfidf-aspect-silver-v1/model.joblib` (hash diverifikasi `load_tfidf_contract` terhadap `ml/configs/a9.yaml`).
- [ ] Bundle data `sipature-app/src/data/generated/{places,interventions,corpus}.json` sudah ter-generate.
- [ ] `.env` sudah disalin dari `.env.example` dan `POSTGRES_PASSWORD` diganti.

## 0b. Transfer repo ke DGX (via SFTP)

```bash
# Dari laptop (tanpa internet): upload repo ke /workspace via SFTP/WinSCP.
# Pastikan folder ter-upload: ml/  sipature-api/  sipature-app/  (termasuk model + generated data)
```

Karena server punya internet, langkah build (§1) bisa langsung di server —
base image ditarik dari Docker Hub saat build. Tidak perlu `docker save`/`load`.

## 1. Build image

```bash
cd sipature-app
docker compose build
```

Hasil yang diharapkan (build selesai tanpa error):

```
 Image sipature-inference:demo Built
 Image sipature-app:demo Built
```

`db` memakai image publik `postgres:16-alpine` (ditarik otomatis).

## 2. Start service

```bash
docker compose up -d
docker compose ps   # tunggu semua "(healthy)"
```

Hasil yang diharapkan — 3 service `(healthy)`:

```
NAME                 SERVICE     STATUS
martahuta-web        web         Up (healthy)  0.0.0.0:3000->3000
sipature-db          db          Up (healthy)  0.0.0.0:5432->5432
sipature-inference   inference   Up (healthy)  0.0.0.0:8000->8000
```

## 3. Seed database

```bash
cd sipature-app
set -a; . ./.env; set +a
DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:${POSTGRES_PORT}/${POSTGRES_DB}" \
  npm run db:seed
```

Hasil yang diharapkan:

```
Seeded: 388 destinations, 14 aspects, 1121 signals.
```

Verifikasi angka (harus cocok):

```bash
docker exec -e PGPASSWORD="$POSTGRES_PASSWORD" sipature-db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -t -c "
SELECT 'destinations', count(*) FROM destinations
UNION ALL SELECT 'aspects', count(*) FROM aspects
UNION ALL SELECT 'actionable_dest', count(*) FROM destinations WHERE priority <> 'Insufficient Data'
UNION ALL SELECT 'actionable_issues', count(*) FROM destination_signals WHERE priority <> 'Insufficient Data';"
```

```
 destinations    | 388
 aspects         |  14
 actionable_dest | 103
 actionable_issues | 210
```

## 4. Verifikasi health

```bash
curl -s http://localhost:8000/health
curl -s http://localhost:3000/api/health
curl -s http://localhost:3000/api/places
```

Hasil yang diharapkan:

- inference `/health`: `{"status":"ok","a9_version":"a9-tfidf-lexical-v1.0.4","aspect_model":"tfidf-aspect-silver-v1","polarity_version":"lexical-polarity-v1","severity_status":"unavailable_no_supported_model"}`
- web `/api/health`: `mode=database`, `placesLoaded=388`, `actionableDestinations=103`, `evidenceStatus=withheld_pending_privacy_review`.
- web `/api/places`: `total=388`.

Live inference (TF-IDF):

```bash
curl -s -X POST http://localhost:3000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"Toiletnya kotor dan bau, parkir sempit dan mahal, pemandangan indah sekali"}'
```

Hasil yang diharapkan: `"mode":"production"`, `"method":"tfidf_aspect_lexical_polarity"`,
`"modelVersion":"tfidf-aspect-silver-v1"`, dan `hits` berisi aspek terdeteksi
(minimal `scenery`, `parking`, `cleanliness`, `sanitation`).

## 5. Fallback & offline check

Matikan `inference`, lalu panggil `/api/analyze` — harus jatuh ke sandbox leksikal:

```bash
docker compose stop inference
curl -s -X POST http://localhost:3000/api/analyze \
  -H "Content-Type: application/json" -d '{"text":"Toiletnya kotor dan bau"}'
docker compose start inference
```

Hasil yang diharapkan saat inference mati: `"mode":"baseline"`, `"method":"lexical_demo_v1"`.

Offline: model + data sudah di-bundle ke image (bukan download saat startup), jadi
selama image ter-build, runtime tidak butuh internet. Uji offline = `docker compose up`
tanpa koneksi eksternal (web tetap melayani halaman + data precomputed).

## 6. Cold start / restart check

```bash
docker compose down
docker compose up -d
docker compose ps        # tunggu healthy
curl -s http://localhost:3000/api/health   # placesLoaded=388, actionable=103
```

Hasil yang diharapkan: data **persist** (volume `pgdata`) — destinasi tetap 388,
actionable 103, issues 210. (Rehearsal: setelah down+up, angka tetap 388/103/210.)

## 7. Refresh data (bila diperlukan)

```bash
bash scripts/refresh.sh --no-sync   # regenerate bundle + seed + rebuild web&inference
# atau tanpa generate:  bash scripts/refresh.sh --no-sync --no-generate
```

Siklus: (1) sync Drive (opsional) → (2) `npm run data:generate` → (3) seed DB →
(4) `docker compose up -d --build web inference`. Rehearsal: siklus selesai tanpa
error; web + inference kembali healthy.

Catatan regenerasi setelah gold: ganti `app-export.json` di
`ml/artifacts/a9/<run>-export/` dengan export A9 baru (gold), perbarui hash di
`generate-product-data.mjs`, lalu jalankan `scripts/refresh.sh`.

## 8. Rollback / troubleshooting

- **Service gagal start**: `docker compose logs <service>`; pastikan `.env` terisi
  dan port tidak bentrok (`lsof -i :3000`).
- **Model hash mismatch saat start inference**: pastikan model di
  `ml/artifacts/models/tfidf-aspect-silver-v1/` adalah `a10bddb1…` (lihat §0);
  salin dari Drive bila perlu (`scripts/sync-drive.sh pull`).
- **DB tidak ke-seed**: hapus volume (`docker compose down -v`) lalu `up -d` agar
  `db/schema.sql` auto-init ulang, kemudian seed ulang (§3).
- **Rollback versi**: `docker compose down` lalu checkout tag/commit lama dan
  `docker compose up -d --build`.

---

## Checklist final sebelum presentasi

- [ ] Semua service healthy (`docker compose ps` — 3× healthy)
- [ ] Data seed benar (388 destinasi, 14 aspek, 103 actionable, 210 issues)
- [ ] `/api/analyze` mode production (TF-IDF) + fallback baseline teruji
- [ ] Demo offline tanpa internet (model + data ter-bundle)
- [ ] Backup artifact tersedia (Drive: model, data, runbook)
- [ ] Versi/hash model & data tercatat (model `a10bddb1…`, app-export `8037d072…`)
