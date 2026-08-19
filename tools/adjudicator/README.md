# SIPATURE Adjudicator

Web tool adjudikasi untuk label gold yang berselisih (setelah `annotation-agreement`).

## Alur lengkap

1. Anotasi selesai → `A1/A2/A3_completed.jsonl` di `ml/data/annotations/gold/`.
2. `sipature-ml annotation-agreement ... --output agreement.json` (gates harus lolos).
3. Siapkan queue: `python tools/adjudicator/prepare_adjudication.py <A1> <A2> <A3>
   --agreement agreement.json --out-dir ml/data/annotations/gold` menghasilkan
   `adjudicated_auto.jsonl` (majority-vote 2/3) + `adjudication_queue.json` (manual).
4. Jalankan tool ini, adjudikasi 71 review yang tersisa.
5. Export `adjudicated.jsonl` (auto + manual).
6. `sipature-ml freeze-gold ...` → `gold.jsonl`.

## Run

```bash
cd tools/adjudicator
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8002
```

Buka `http://localhost:8002`.

## Konfigurasi (env var)

- `GOLD_DIR`: folder gold (default: `ml/data/annotations/gold`).
- `ADJUDICATION_QUEUE`: path queue JSON.
- `ADJUDICATED_AUTO`: path hasil auto-adjudikasi.
- `ADJUDICATED_OUTPUT`: path output `adjudicated.jsonl`.
- `ADJUDICATOR_USERNAME` / `ADJUDICATOR_PASSWORD`: basic auth opsional.

Progress tersimpan otomatis di `tools/adjudicator/data/adjudicator.json` (atomic).
