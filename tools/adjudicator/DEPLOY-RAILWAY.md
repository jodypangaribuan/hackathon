# Deploy SIPATURE Adjudicator ke Railway (always-on)

## 1. Siapkan akun & CLI (sekali)

```bash
brew install railway
railway login            # login via browser
```

## 2. Buat project + service

```bash
cd tools/adjudicator
railway init              # buat project baru
railway up                # deploy pertama (build Nixpacks)
```

## 3. Tambah volume (untuk state + gold)

```bash
railway volume add -m /data
```

## 4. Seed otomatis

File `seed/adjudication_queue.json` + `seed/adjudicated_auto.jsonl` sudah
ter-bundle di image. Saat startup, bila `GOLD_DIR` kosong, keduanya otomatis
disalin ke volume. Tidak perlu upload manual.

## 5. Set environment variables (dashboard → Variables)

| Variable | Nilai |
|---|---|
| `GOLD_DIR` | `/data/gold` |
| `STATE_DIR` | `/data/state` |
| `ADJUDICATOR_USERNAME` | `tim` |
| `ADJUDICATOR_PASSWORD` | `ganti-password-kuat` |

## 6. Redeploy & akses

```bash
railway up
railway open   # buka URL publik (akan minta basic-auth)
```

## 7. Alur selesai

1. Adjudicator menyelesaikan seluruh review (progress tersimpan di volume).
2. Klik **Export adjudicated.jsonl** → unduh file.
3. Lokal: jalankan `sipature-ml freeze-gold` dengan file tersebut (lihat
   `tools/adjudicator/README.md`).

## Catatan keamanan

- Review text + label gold bersifat restricted — pastikan `ADJUDICATOR_PASSWORD` kuat.
- Volume Railway persisten: progress tidak hilang walau service restart/redeploy.
