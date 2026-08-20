# Panduan Deployment SIPATURE ke Server NVIDIA B200 / Production

Dokumen ini memandu proses deployment sistem SIPATURE ke server NVIDIA B200 / Linux Server agar berjalan deterministik, otomatis, dan bebas dari kendala konflik alokasi port pada server multi-user.

---

## 1. Ringkasan Kebutuhan Aset

Repositori Git mengelola seluruh kode sumber aplikasi Next.js 15, FastAPI inference service, skrip machine learning, dan Drizzle ORM. Beberapa file biner model dan data teragregasi dikecualikan dari Git melalui `.gitignore` demi efisiensi dan tata kelola repositori:

| Komponen | Jalur File / Direktori | Status Git | Keterangan & Tujuan |
| :--- | :--- | :--- | :--- |
| **Model ML Terlatih** | `ml/artifacts/models/tfidf-aspect-silver-v1/` (`model.joblib`, `manifest.json`) | Tidak di-commit | Diperlukan oleh kontainer `sipature-inference` untuk inferensi live klasifikasi aspek ulasan. |
| **Data Olahan Agregat** | `sipature-app/src/data/generated/` (`places.json`, `corpus.json`, `evidence.json`, `interventions.json`) | Tidak di-commit | Diperlukan untuk seeding awal database PostgreSQL (388 destinasi dan 9.785 kutipan ulasan). |
| **Konfigurasi Environment** | `sipature-app/.env` & `sipature-app/.env.production` | Tidak di-commit | Memuat kredensial database PostgreSQL, alokasi port host, dan URL interkoneksi service. |
| **Source Code & Dockerfiles** | Folder `sipature-app/`, `sipature-api/`, `ml/`, `db/`, `scripts/` | Terlacak di Git | Kode Next.js 15, FastAPI, skrip Drizzle ORM, schema SQL, dan file `docker-compose.yml`. |

> **Ukuran File Bundle:** Seluruh file yang dikecualikan di atas dikemas ke dalam arsip `sipature-server-bundle.tar.gz` berukuran **~3.1 MB** (dapat ditransfer dalam hitungan detik via `scp` atau media penyimpanan).

---

## 2. Alur Deployment Otomatis (Metode yang Disarankan)

### Langkah 1: Pengemasan Aset di Laptop Lokal (Sebelum Deploy)
Jalankan skrip pengemasan di direktori root repositori lokal:

```bash
./scripts/package-server-bundle.sh
```

Skrip ini akan:
1. Memvalidasi kelengkapan bobot model `model.joblib` dan file manifest.
2. Memvalidasi seluruh data JSON hasil agregasi analitik (`corpus.json`, `evidence.json`, `places.json`, `interventions.json`).
3. Menyiapkan konfigurasi environment production `sipature-app/.env.production`.
4. Menghasilkan arsip terkompresi: `sipature-server-bundle.tar.gz` (~3.1 MB).

---

### Langkah 2: Kloning Repositori di Server B200
Pada server B200 (yang memiliki koneksi internet), lakukan kloning repositori:

```bash
git clone <URL_GIT_REPOSITORY> hackathon
cd hackathon
```

---

### Langkah 3: Transfer Arsip Bundle ke Server B200
Dari terminal laptop lokal, transfer file `sipature-server-bundle.tar.gz` ke direktori project di server B200:

```bash
scp sipature-server-bundle.tar.gz <username>@<ip-server-b200>:~/hackathon/
```

*Catatan: Jika menggunakan flashdisk atau penyimpanan bersama, salin file `sipature-server-bundle.tar.gz` langsung ke dalam folder `hackathon/` pada server.*

---

### Langkah 4: Eksekusi Deployment di Server B200
Pada terminal server B200 di dalam direktori `hackathon`, jalankan:

```bash
./scripts/deploy-server.sh
```

### Mekanisme Ketahanan (*Robustness*) yang Dijalankan oleh `deploy-server.sh`:
1. **Ekstraksi Otomatis:** Mengekstrak model dan data olahan ke direktori tujuan yang tepat.
2. **Inisialisasi Environment:** Mempersiapkan `sipature-app/.env` dari bundle production.
3. **Resolusi Port Otomatis (Anti-Collision):** 
   - Memeriksa apakah port default `3000` (Web), `8000` (Inference), atau `5432` (PostgreSQL) sudah dialokasikan/dipakai oleh user lain di server.
   - Jika port terpakai, skrip secara otomatis mencari port berikutnya yang bebas (misal `3001`, `8001`, `5433`) dan memperbarui file `.env` sebelum kontainer dibangun.
4. **Build & Up Docker Compose:** Menjalankan `docker compose up -d --build`.
5. **Pemeriksaan Health Kontainer:** Menunggu hingga seluruh kontainer berstatus `healthy`.
6. **Database Seeding Otomatis:** Mengisi database dengan seluruh korpus 388 destinasi dan 9.785 kutipan ulasan.
7. **Verifikasi Output:** Menampilkan endpoint URL yang aktif beserta hasil respon HTTP API.

---

## 3. Alur Deployment Manual (Alternatif Langkah-demi-Langkah)

Jika ingin menjalankan setiap tahapan secara manual tanpa bantuan skrip otomasi:

### 1. Ekstrak Arsip Aset
Letakkan `sipature-server-bundle.tar.gz` di root project, kemudian jalankan:
```bash
tar -xzvf sipature-server-bundle.tar.gz
```

### 2. Verifikasi Konfigurasi Environment
```bash
cd sipature-app
if [ ! -f .env ]; then
  cp .env.production .env 2>/dev/null || cp .env.example .env
fi
```

*Jika port 3000, 8000, atau 5432 sudah digunakan di server, sesuaikan nilai `WEB_PORT`, `INFERENCE_PORT`, atau `POSTGRES_PORT` di dalam file `.env`.*

### 3. Bangun dan Nyalakan Kontainer
```bash
docker compose up -d --build
```

### 4. Jalankan Seeding Database
```bash
docker compose exec -T web npm run db:seed
```

### 5. Verifikasi Status Layanan
```bash
curl -s http://localhost:3000/api/health
curl -s http://localhost:8000/health
```

---

## 4. Daftar Port dan URL Layanan

Setelah proses deployment selesai, layanan dapat diakses melalui:

| Layanan | Port Default | URL Akses Lokal Server | URL Akses Jaringan Luar |
| :--- | :--- | :--- | :--- |
| **Web Dashboard (SIPATURE)** | `3000` (atau auto) | `http://localhost:3000` | `http://<IP_SERVER_B200>:3000` |
| **Inference Service (FastAPI)** | `8000` (atau auto) | `http://localhost:8000` | `http://<IP_SERVER_B200>:8000` |
| **Dokumentasi API (Swagger)** | `8000` (atau auto) | `http://localhost:8000/docs` | `http://<IP_SERVER_B200>:8000/docs` |
| **Database PostgreSQL** | `5432` (atau auto) | `localhost:5432` | `localhost:5432` |

---

## 5. Panduan Pemecahan Masalah (Troubleshooting)

### Kasus A: Port Sudah Digunakan oleh Pengguna Lain di Server
* Skrip `deploy-server.sh` secara default sudah menangani hal ini secara otomatis.
* Jika menjalankan manual, buka file `sipature-app/.env`, ganti `WEB_PORT` menjadi port kosong (misal: `3010`) dan `INFERENCE_PORT` menjadi `8010`, lalu jalankan `docker compose up -d`.

### Kasus B: Data Destinasi Belum Muncul di Web
* Jalankan perintah database seeding secara manual:
  ```bash
  docker compose -f sipature-app/docker-compose.yml exec -T web npm run db:seed
  ```

### Kasus C: Memeriksa Log Kontainer
* Untuk memeriksa log service web Next.js:
  ```bash
  docker compose -f sipature-app/docker-compose.yml logs -f web
  ```
* Untuk memeriksa log service inference FastAPI:
  ```bash
  docker compose -f sipature-app/docker-compose.yml logs -f inference
  ```
* Untuk memeriksa log service database PostgreSQL:
  ```bash
  docker compose -f sipature-app/docker-compose.yml logs -f db
  ```
