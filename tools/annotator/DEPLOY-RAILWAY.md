# Deploy SIPATURE Annotator ke Railway (always-on)

## 1. Siapkan akun & CLI (sekali)

```bash
brew install railway
railway login            # login via browser
```

## 2. Buat project + service

```bash
cd tools/annotator
railway init              # buat project baru
railway up                # deploy pertama (build Nixpacks)
```

## 3. Tambah volume (untuk data + state)

```bash
railway volume add -m /data
```

## 4. Upload template anotasi ke volume

Buka dashboard Railway → service → tab **Volumes** → **Files** explorer.
Buat folder `/data/annotations`, lalu upload 6 file template dari
`ml/data/annotations/`:

- `pilot_A1_annotations.jsonl`, `pilot_A2_annotations.jsonl`, `pilot_A3_annotations.jsonl`
- `main_A1_annotations.jsonl`, `main_A2_annotations.jsonl`, `main_A3_annotations.jsonl`

## 5. Set environment variables (dashboard → Variables)

| Variable | Nilai |
|---|---|
| `ANNOTATION_DIR` | `/data/annotations` |
| `STATE_DIR` | `/data/state` |
| `ANNOTATOR_USERNAME` | `tim` |
| `ANNOTATOR_PASSWORD` | `ganti-password-kuat` |

## 6. Redeploy & akses

```bash
railway up
railway open   # buka URL publik (akan minta basic-auth)
```

Bagikan URL + username/password ke anggota tim. Setiap anggota memilih ID
annotator sendiri; progress tersimpan di volume (persisten, aman dari restart).

## Catatan keamanan

- Review text bersifat restricted — pastikan `ANNOTATOR_PASSWORD` kuat.
- Volume Railway persisten: progress tidak hilang walau service restart/redeploy.
