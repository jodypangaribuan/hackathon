# 🚀 Panduan Deployment SIPATURE ke Server NVIDIA B200

Dokumen ini memandu proses deployment sistem **SIPATURE** ke server **NVIDIA B200 / Linux Server** agar berjalan **100% lancar, deterministik, dan tanpa kendala missing files**.

---

## 📌 1. Mengapa Ada File yang Perlu Diunggah Terpisah?

Repositori Git mengelola seluruh kode sumber aplikasi, skrip ML, dan konfigurasi. Namun, beberapa file artefak model dan database berukuran biner/sensitif dikecualikan oleh `.gitignore`:

| Kategori | File / Direktori | Status di Git | Fungsi & Mengapa Diperlukan |
| :--- | :--- | :--- | :--- |
| **Model ML** | `ml/artifacts/models/tfidf-aspect-silver-v1/` (`model.joblib`, `manifest.json`) | ❌ *Gitignored* | Bobot model terlatih untuk service **Inference FastAPI** (`sipature-inference`) |
| **Data Teragregasi** | `sipature-app/src/data/generated/` (`places.json`, `corpus.json`, `evidence.json`, `interventions.json`) | ❌ *Gitignored* | Data olahan 388 destinasi, 1.121 sinyal aspek, dan 9.785 kutipan ulasan untuk seeding database PostgreSQL |
| **Kredensial** | `sipature-app/.env` | ❌ *Gitignored* | Konfigurasi koneksi PostgreSQL dan port container |
| **Source Code & Docker** | Seluruh folder `sipature-app/`, `sipature-api/`, `ml/`, `db/` | ✅ *Tersimpan di Git* | Kode aplikasi Next.js 15, FastAPI, Drizzle ORM, schema SQL, dan Dockerfile |

> **Ukuran Total Bundle Aset:** Hanya **~3.1 MB** (sangat cepat ditransfer via `scp` atau media penyimpanan dalam 1-2 detik).

---

## ⚡ 2. Panduan Deployment Cepat (Metode Otomatis — 2 Menit)

Tersedia skrip otomasi yang sudah disiapkan di dalam repositori:

### Langkah 1: Di Laptop Lokal (Sebelum Berangkat / Saat Menyiapkan File)
Buka terminal di root project repositori ini, lalu jalankan:

```bash
./scripts/package-server-bundle.sh
```
*Skrip ini akan memvalidasi kelengkapan model & data, lalu membuat arsip siap kirim: **`sipature-server-bundle.tar.gz`** (ukuran ~3.1 MB).*

---

### Langkah 2: Di Server B200 (Clone Repositori)
Karena server B200 memiliki akses internet, lakukan clone repositori langsung:

```bash
git clone <URL_GIT_REPOSITORY> hackathon
cd hackathon
```

---

### Langkah 3: Transfer Bundle Aset ke Server B200
Kirimkan file `sipature-server-bundle.tar.gz` dari laptop lokal ke server B200 menggunakan `scp` (atau copy via flashdisk/Drive jika ada):

```bash
# Jalankan dari laptop lokal:
scp sipature-server-bundle.tar.gz <username>@<ip-server-b200>:~/hackathon/
```

---

### Langkah 4: Di Server B200 (Jalankan Deploy Satu Perintah)
Masuk ke terminal server B200 pada folder `hackathon`, lalu jalankan:

```bash
./scripts/deploy-server.sh
```

**Apa yang dilakukan oleh skrip `deploy-server.sh` secara otomatis?**
1. Mengekstrak bundle model & data ke lokasi yang tepat (`ml/artifacts/models/` dan `sipature-app/src/data/generated/`).
2. Menyiapkan file `sipature-app/.env`.
3. Membangun (*build*) dan menyalakan 3 kontainer Docker (`martahuta-web`, `sipature-inference`, `sipature-db`).
4. Mengisi (*seed*) database PostgreSQL dengan data 388 destinasi dan 9.785 kutipan ulasan.
5. Memverifikasi endpoint *health check* dan menampilkan URL aktif.

---

## 🛠️ 3. Panduan Deployment Manual (Langkah-demi-Langkah Tanpa Skrip)

Jika ingin menjalankan setiap perintah secara manual di server B200:

### 1. Ekstrak Bundle Aset
Pastikan file `sipature-server-bundle.tar.gz` diletakkan di root folder project pada server, lalu ekstrak:
```bash
tar -xzvf sipature-server-bundle.tar.gz
```

### 2. Pastikan File `.env` Siap
```bash
cd sipature-app
if [ ! -f .env ]; then
  cp .env.example .env
  # Ganti password database jika diperlukan
  sed -i 's/CHANGE_ME_use_a_strong_password/sipature_dev_password/g' .env
fi
```

### 3. Bangun dan Jalankan Docker Compose
```bash
docker compose up -d --build
```

### 4. Seed Database PostgreSQL
Setelah kontainer berjalan aktif:
```bash
docker compose exec martahuta-web npm run db:seed
```

### 5. Verifikasi Health Endpoint
```bash
curl -s http://localhost:3000/api/health
curl -s http://localhost:8000/health
```

---

## 🔍 4. Uji Coba & Verifikasi Layanan

Setelah deploy berhasil, akses layanan melalui browser atau HTTP client:

| Layanan | Port Internal | URL Akses di Server | URL Akses dari Luar / Jaringan |
| :--- | :--- | :--- | :--- |
| **Aplikasi Web (SIPATURE)** | `3000` | `http://localhost:3000` | `http://<IP_SERVER_B200>:3000` |
| **Inference Service (FastAPI)** | `8000` | `http://localhost:8000` | `http://<IP_SERVER_B200>:8000` |
| **Dokumentasi API (Swagger)** | `8000` | `http://localhost:8000/docs` | `http://<IP_SERVER_B200>:8000/docs` |
| **Database PostgreSQL** | `5432` | `localhost:5432` | `localhost:5432` |

### Endpoint Kritis yang Perlu Dicek:
* **Dashboard Utama:** `http://<IP_SERVER_B200>:3000/`
* **Antrean Intervensi:** `http://<IP_SERVER_B200>:3000/intervensi`
* **Detail Destinasi & Ulasan:** `http://<IP_SERVER_B200>:3000/destinasi/dest_resto_e5c1241a2468f4`
* **Health API Web:** `http://<IP_SERVER_B200>:3000/api/health`
* **Health API Model:** `http://<IP_SERVER_B200>:8000/health`

---

## 🆘 5. Penanganan Masalah (Troubleshooting)

### A. Kontainer Web atau Inference Tidak Mau Menyala
Periksa log kontainer terkait:
```bash
docker compose -f sipature-app/docker-compose.yml logs -f web
docker compose -f sipature-app/docker-compose.yml logs -f inference
```

### B. Error: `Model file not found` pada saat build inference
* **Penyebab:** Folder `ml/artifacts/models/tfidf-aspect-silver-v1/` belum diekstrak atau kosong.
* **Solusi:** Jalankan `tar -xzvf sipature-server-bundle.tar.gz` di root project, lalu jalankan ulang `docker compose up -d --build`.

### C. Data Destinasi Kosong di Web
* **Penyebab:** Database PostgreSQL belum di-seed setelah kontainer pertama kali dibuat.
* **Solusi:** Jalankan perintah seeding:
  ```bash
  docker compose -f sipature-app/docker-compose.yml exec martahuta-web npm run db:seed
  ```

### D. Port 3000 atau 8000 Sudah Terpakai di Server
Edit file `sipature-app/.env` dan ubah port host yang diinginkan:
```bash
WEB_PORT=3010
INFERENCE_PORT=8010
```
Lalu restart kontainer:
```bash
docker compose -f sipature-app/docker-compose.yml up -d
```
