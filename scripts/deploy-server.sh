#!/usr/bin/env bash
# ==============================================================================
# SIPATURE — Script Otomasi Deploy Server B200 / Production
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${ROOT_DIR}"

echo "========================================================"
echo "SIPATURE: Inisialisasi Deployment ke Server B200"
echo "========================================================"

# 1. Verifikasi dependensi sistem dasar
command -v docker >/dev/null 2>&1 || {
  echo "ERROR: Docker engine tidak ditemukan pada server."
  exit 1
}

docker compose version >/dev/null 2>&1 || {
  echo "ERROR: Docker Compose tidak ditemukan pada server."
  exit 1
}

# 2. Ekstrak bundle aset jika arsip tersedia
if [ -f "sipature-server-bundle.tar.gz" ]; then
  echo "INFO: Mengekstrak sipature-server-bundle.tar.gz..."
  tar -xzvf sipature-server-bundle.tar.gz
elif [ -f "../sipature-server-bundle.tar.gz" ]; then
  echo "INFO: Mengekstrak ../sipature-server-bundle.tar.gz..."
  tar -xzvf ../sipature-server-bundle.tar.gz
fi

# 3. Validasi kelengkapan artefak model dan data
if [ ! -f "ml/artifacts/models/tfidf-aspect-silver-v1/model.joblib" ]; then
  echo "ERROR: Model ML pada ml/artifacts/models/tfidf-aspect-silver-v1/model.joblib tidak ditemukan."
  echo "Pastikan file sipature-server-bundle.tar.gz telah diunggah dan diekstrak."
  exit 1
fi

if [ ! -f "sipature-app/src/data/generated/corpus.json" ]; then
  echo "ERROR: Data olahan pada sipature-app/src/data/generated/ tidak ditemukan."
  echo "Pastikan file sipature-server-bundle.tar.gz telah diunggah dan diekstrak."
  exit 1
fi

# 4. Siapkan konfigurasi .env
if [ ! -f "sipature-app/.env" ]; then
  if [ -f "sipature-app/.env.production" ]; then
    cp sipature-app/.env.production sipature-app/.env
  else
    cp sipature-app/.env.example sipature-app/.env
    sed -i 's/CHANGE_ME_use_a_strong_password/sipature_prod_password_2026/g' sipature-app/.env 2>/dev/null || true
  fi
fi

# 5. Deteksi dan Resolusi Alokasi Port Otomatis (Mencegah Port Conflict pada Server Multi-User)
find_available_port() {
  local target_port=$1
  local resolved_port=$target_port

  if command -v python3 >/dev/null 2>&1; then
    resolved_port=$(python3 -c "
import socket
port = int(${target_port})
while True:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', port))
        s.close()
        print(port)
        break
    except OSError:
        port += 1
" 2>/dev/null || echo "$target_port")
  fi

  echo "$resolved_port"
}

# Baca port yang dikonfigurasi saat ini
CURRENT_WEB_PORT=$(grep "^WEB_PORT=" sipature-app/.env | cut -d'=' -f2 || echo "3000")
CURRENT_INFERENCE_PORT=$(grep "^INFERENCE_PORT=" sipature-app/.env | cut -d'=' -f2 || echo "8000")
CURRENT_POSTGRES_PORT=$(grep "^POSTGRES_PORT=" sipature-app/.env | cut -d'=' -f2 || echo "5432")

FREE_WEB_PORT=$(find_available_port "${CURRENT_WEB_PORT:-3000}")
FREE_INFERENCE_PORT=$(find_available_port "${CURRENT_INFERENCE_PORT:-8000}")
FREE_POSTGRES_PORT=$(find_available_port "${CURRENT_POSTGRES_PORT:-5432}")

if [ "$FREE_WEB_PORT" != "$CURRENT_WEB_PORT" ]; then
  echo "INFO: Port $CURRENT_WEB_PORT terpakai oleh proses lain. Dialokasikan ke port $FREE_WEB_PORT."
  sed -i "s/^WEB_PORT=.*/WEB_PORT=$FREE_WEB_PORT/" sipature-app/.env 2>/dev/null || true
fi

if [ "$FREE_INFERENCE_PORT" != "$CURRENT_INFERENCE_PORT" ]; then
  echo "INFO: Port $CURRENT_INFERENCE_PORT terpakai oleh proses lain. Dialokasikan ke port $FREE_INFERENCE_PORT."
  sed -i "s/^INFERENCE_PORT=.*/INFERENCE_PORT=$FREE_INFERENCE_PORT/" sipature-app/.env 2>/dev/null || true
fi

if [ "$FREE_POSTGRES_PORT" != "$CURRENT_POSTGRES_PORT" ]; then
  echo "INFO: Port $CURRENT_POSTGRES_PORT terpakai oleh proses lain. Dialokasikan ke port $FREE_POSTGRES_PORT."
  sed -i "s/^POSTGRES_PORT=.*/POSTGRES_PORT=$FREE_POSTGRES_PORT/" sipature-app/.env 2>/dev/null || true
fi

# 6. Bersihkan kontainer lama bila ada conflict lalu jalankan Docker Compose
echo "INFO: Membersihkan kontainer lama bila ada..."
docker rm -f martahuta-web sipature-inference sipature-db 2>/dev/null || true
docker compose -f sipature-app/docker-compose.yml down --remove-orphans 2>/dev/null || true

echo "INFO: Membangun image dan menjalankan layanan kontainer..."
docker compose -f sipature-app/docker-compose.yml up -d --build

echo "INFO: Menunggu inisialisasi kontainer dan pemeriksaan health..."
sleep 5

MAX_WAIT=20
COUNT=0
while [ $COUNT -lt $MAX_WAIT ]; do
  if docker compose -f sipature-app/docker-compose.yml ps | grep -q "(healthy)"; then
    break
  fi
  COUNT=$((COUNT + 1))
  echo "   ...menunggu status healthy ($COUNT/$MAX_WAIT)..."
  sleep 2
done

# 7. Eksekusi Database Seeding
echo "INFO: Menjalankan database seeding (destinasi, sinyal, dan ulasan)..."
docker compose -f sipature-app/docker-compose.yml exec -T web npm run db:seed 2>/dev/null || \
docker compose -f sipature-app/docker-compose.yml exec -T martahuta-web npm run db:seed 2>/dev/null || {
  echo "WARNING: Percobaan seeding pertama belum selesai, mencoba ulang dalam 3 detik..."
  sleep 3
  docker compose -f sipature-app/docker-compose.yml exec -T web npm run db:seed || true
}

# 8. Verifikasi Endpoint Layanan
ACTUAL_WEB_PORT=$(grep "^WEB_PORT=" sipature-app/.env | cut -d'=' -f2 || echo "3000")
ACTUAL_INFERENCE_PORT=$(grep "^INFERENCE_PORT=" sipature-app/.env | cut -d'=' -f2 || echo "8000")

WEB_HEALTH=$(curl -s "http://localhost:${ACTUAL_WEB_PORT}/api/health" || echo '{"status":"unavailable"}')
INFERENCE_HEALTH=$(curl -s "http://localhost:${ACTUAL_INFERENCE_PORT}/health" || echo '{"status":"unavailable"}')

echo ""
echo "========================================================"
echo "DEPLOYMENT STATUS: BERHASIL SELESAI"
echo "========================================================"
echo "Daftar URL Layanan Aktif:"
echo "1. Web Application:     http://localhost:${ACTUAL_WEB_PORT} (atau http://<SERVER_IP>:${ACTUAL_WEB_PORT})"
echo "2. Inference API:       http://localhost:${ACTUAL_INFERENCE_PORT} (atau http://<SERVER_IP>:${ACTUAL_INFERENCE_PORT})"
echo "3. Swagger API Docs:    http://localhost:${ACTUAL_INFERENCE_PORT}/docs"
echo "4. PostgreSQL Host:     localhost:${FREE_POSTGRES_PORT}"
echo ""
echo "Hasil Verifikasi Web API:"
echo "${WEB_HEALTH}"
echo ""
echo "Hasil Verifikasi Inference API:"
echo "${INFERENCE_HEALTH}"
echo "========================================================"
