# SIPATURE Annotator

Web tool anotasi gold untuk 3 anggota tim (A1, A2, A3).

## Run

```bash
cd tools/annotator
pip install -r requirements.txt
python3 -m uvicorn app:app --host 0.0.0.0 --port 8001
```

Buka `http://localhost:8001` (atau `http://<ip-host>:8001` untuk anggota lain).
Lihat `tools/README.md` untuk panduan lengkap.

## Alur

1. Setiap anggota memilih ID-nya (A1/A2/A3).
2. Annotate seluruh review yang ditugaskan (pilot + main, dari
   `ml/data/annotations/{pilot,main}_<id>_annotations.jsonl`).
3. Progress tersimpan otomatis ke `tools/annotator/data/<id>.json`.
4. Klik **Export JSONL** → unduh `<id>_completed.jsonl`.

## Validasi & agreement

Setelah ketiganya selesai, jalankan (dari `ml/`):

```bash
sipature-ml annotation-agreement \
  <path/A1_completed.jsonl> <path/A2_completed.jsonl> <path/A3_completed.jsonl> \
  --output agreement.json

sipature-ml freeze-gold \
  <A1> <A2> <A3> \
  --adjudicated adjudicated.jsonl --metrics agreement.json --output gold.jsonl
```

## Konfigurasi (env var)

- `ANNOTATION_DIR`: lokasi template JSONL (default `ml/data/annotations`).
- State per annotator tersimpan di `tools/annotator/data/`.
