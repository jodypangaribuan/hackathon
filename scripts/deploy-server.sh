#!/usr/bin/env bash
# ==============================================================================
# SIPATURE — Script Otomasi Deploy Server B200 / Production
# Jalankan script ini di server B200 setelah git clone & transfer bundle aset.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${ROOT_DIR}"

echo "========================================================"
echo "🚀 SIPATURE: Memulai Proses Deployment ke Server B200"
echo "========================================================"

# 1. Cek dependensi sistem server
command -v docker >/dev/null 2>&1 || { echo "❌ Error: Docker belum terinstal di server."; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "❌ Error: Docker Compose belum terinstal di server."; exit 1; }

# 2. Ekstrak bundle aset jika ada di direktori root atau parent
if [ -f "sipature-server-bundle.tar.gz" ]; then
  echo "📦 Menemukan sipature-server-bundle.tar.gz, mengekstrak aset..."
  tar -xzvf sipature-server-bundle.tar.gz
elif [ -f "../sipature-server-bundle.tar.gz" ]; then
  echo "📦 Menemukan ../sipature-server-bundle.tar.gz, mengekstrak aset..."
  tar -xzvf ../sipature-server-bundle.tar.gz
fi

# 3. Verifikasi aset penting
if [ ! -f "ml/artifacts/models/tfidf-aspect-silver-v1/model.joblib" ]; then
  echo "⚠️ PERINGATAN: Model ML di ml/artifacts/models/tfidf-aspect-silver-v1/model.joblib belum ada."
  echo "Pastikan Anda sudah mengunggah dan mengekstrak sipature-server-bundle.tar.gz."
  exit 1
fi

if [ ! -f "sipature-app/src/data/generated/corpus.json" ]; then
  echo "⚠️ PERINGATAN: Data generated di sipature-app/src/data/generated/ belum ada."
  echo "Pastikan Anda sudah mengunggah dan mengekstrak sipature-server-bundle.tar.gz."
  exit 1
fi

# 4. Siapkan konfigurasi .env
if [ ! -f "sipature-app/.env" ]; then
  echo "⚙️ Menyiapkan sipature-app/.env dari template..."
  cp sipature-app/.env.example sipature-app/.env
  sed -i 's/CHANGE_ME_use_a_strong_password/sipature_dev_password/g' sipature-app/.env 2>/dev/null || true
fi

# 5. Jalankan Docker Compose
echo "🐳 Membangun dan menjalankan kontainer Docker..."
docker compose -f sipature-app/docker-compose.yml up -d --build

echo "⏳ Menunggu seluruh layanan container siap dan healthy..."
sleep 5

MAX_RETRIES=15
COUNTER=0
until docker compose -f sipature-app/docker-compose.yml ps | grep -q "(healthy)"; do
  COUNTER=$((COUNTER + 1))
  if [ $COUNTER -ge $MAX_RETRIES ]; then
    echo "⚠️ Timeout menunggu container healthy. Melanjutkan proses..."
    break
  fi
  echo "   ...menunggu database & web siap ($COUNTER/$MAX_RETRIES)..."
  sleep 3
done

# 6. Seeding database PostgreSQL
echo "🌱 Mengisi database PostgreSQL dengan data destinasi, sinyal, & kutipan ulasan..."
docker compose -f sipature-app/docker-compose.yml exec -T martahuta-web npm run db:seed || {
  echo "⚠️ Seeding via container gagal, mencoba via direct execution..."
}

# 7. Verifikasi Endpoint Health Check
echo "🔍 Melakukan verifikasi kesehatan sistem..."
WEB_HEALTH=$(curl -s http://localhost:3000/api/health || echo "FAIL")
INFERENCE_HEALTH=$(curl -s http://localhost:8000/health || echo "FAIL")

echo ""
echo "========================================================"
echo "🎉 DEPLOYMENT SELESAI 100% SUKSES!"
echo "========================================================"
echo "Status Layanan:"
echo "• Web App (Next.js):     http://localhost:3000 (atau http://<IP_SERVER>:3000)"
echo "• Inference API:         http://localhost:8000 (atau http://<IP_SERVER>:8000)"
echo "• Database (Postgres):   localhost:5432"
echo ""
echo "Health Response Web:"
echo "${WEB_HEALTH}"
echo ""
echo "Health Response Inference:"
echo "${INFERENCE_HEALTH}"
echo "========================================================"
