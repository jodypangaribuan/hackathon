# Tools

Kumpulan tool pendukung (non-produksi) untuk SIPATURE.

| Tool | Fungsi |
|---|---|
| [`annotator/`](annotator/) | Web tool anotasi gold untuk 3 anggota tim |

---

## Menjalankan Annotator

Tool anotasi gold untuk anggota tim (A1, A2, A3). Satu server, diakses via browser.

### 1. Prasyarat

- Python 3.9+
- `fastapi` + `uvicorn` terpasang

```bash
pip install -r tools/annotator/requirements.txt
```

### 2. Jalankan server

```bash
cd tools/annotator
python3 -m uvicorn app:app --host 0.0.0.0 --port 8001
```

Dengan auto-restart (rekomendasi, server bangkit sendiri bila crash):

```bash
bash tools/annotator/run.sh
```

### 2b. Backup progress

```bash
bash tools/annotator/backup.sh   # salin data/*.json ke backups/<timestamp>/
```

### Ketahanan data (kenapa progress aman)

- Progress tersimpan **server-side** ke `tools/annotator/data/<id>.json` setiap
  kali ada perubahan (auto-save). Bukan di browser.
- Penulisan file bersifat **atomic** (temp + rename) — aman dari korupsi bila
  server mati di tengah tulis.
- Bila tunnel (ngrok) putus: data aman; teman tinggal buka ulang URL setelah
  tunnel up lagi, progress otomatis ter-load.
- `run.sh` menjalankan server dalam loop restart (crash → bangkit lagi).

### 3. Buka di browser

```bash
# di mesin yang sama
open http://localhost:8001
```

Agar anggota tim lain bisa akses (jaringan lokal / DGX yang sama), pakai IP host:

```
http://<ip-host>:8001
```

Cek IP host di macOS/Linux:

```bash
ipconfig getifaddr en0   # macOS
hostname -I              # Linux
```

### 4. Alur anggota tim

1. Pilih ID annotator (A1/A2/A3).
2. Annotate seluruh review yang ditugaskan (pilot + main).
3. Progress tersimpan otomatis di `tools/annotator/data/<id>.json`.
4. Klik **Export JSONL** → unduh `<id>_completed.jsonl`.

### 5. Hitung agreement & freeze gold

Setelah ketiganya selesai, dari folder `ml/`:

```bash
sipature-ml annotation-agreement \
  <A1_completed.jsonl> <A2_completed.jsonl> <A3_completed.jsonl> \
  --output agreement.json

sipature-ml freeze-gold \
  <A1_completed.jsonl> <A2_completed.jsonl> <A3_completed.jsonl> \
  --adjudicated adjudicated.jsonl --metrics agreement.json --output gold.jsonl
```

### Matikan server

Tekan `Ctrl+C` di terminal tempat uvicorn berjalan.
