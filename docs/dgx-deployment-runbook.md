# DGX B200 Deployment Runbook (draft — diisi saat staging rehearsal)

Panduan deploy step-by-step untuk final round di DGX B200. Isi file ini dari
hasil **staging rehearsal** (lihat `SIPATURE-Hackathon-TODO.md` §B2), lalu saat
final tinggal **salin-tempel** persis.

> ⚠️ Jangan isi langkah di sini sebelum benar-benar diuji di staging.
> Setiap langkah harus sudah terverifikasi (command + output yang diharapkan).

---

## 0. Prasyarat & asumsi

- [ ] OS / Docker versi di DGX: `[ISI DARI TECHNICAL MEETING]`
- [ ] Akses network (internal), port yang diizinkan: `[ISI]`
- [ ] Model TF-IDF (`a10bddb1…`) tersedia di `ml/artifacts/models/tfidf-aspect-silver-v1/`
- [ ] Bundle data (`src/data/generated/*.json`) sudah ter-generate
- [ ] `.env` sudah disalin dari `.env.example` (password diganti)

## 1. Build image

```bash
[ISI COMMAND + OUTPUT YANG DIHARAPKAN]
```

## 2. Start service

```bash
[ISI]
```

## 3. Seed database

```bash
[ISI]
```

## 4. Verifikasi health

```bash
[ISI — contoh: curl /api/health, /api/places, /api/analyze]
```

## 5. Fallback & offline check

```bash
[ISI]
```

## 6. Cold start / restart check

```bash
[ISI]
```

## 7. Refresh data (bila diperlukan)

```bash
[ISI — scripts/refresh.sh]
```

## 8. Rollback / troubleshooting

- `[ISI langkah rollback bila demo gagal]`

---

## Checklist final sebelum presentasi

- [ ] Semua service healthy
- [ ] Data seed benar (388 destinasi, 103 actionable)
- [ ] Demo offline tanpa internet
- [ ] Backup artifact tersedia
- [ ] Versi/hash model & data tercatat
