#!/usr/bin/env bash
# ==============================================================================
# SIPATURE — Script Pengemasan Aset Server B200 / Production
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${ROOT_DIR}"

OUTPUT_FILE="sipature-server-bundle.tar.gz"

echo "========================================================"
echo "SIPATURE: Pengemasan Aset Runtime Server B200"
echo "========================================================"

# 1. Validasi keberadaan file model ML
if [ ! -f "ml/artifacts/models/tfidf-aspect-silver-v1/model.joblib" ]; then
  echo "ERROR: Model ML tidak ditemukan di ml/artifacts/models/tfidf-aspect-silver-v1/model.joblib"
  exit 1
fi

# 2. Validasi file data generated web app
if [ ! -f "sipature-app/src/data/generated/corpus.json" ] || [ ! -f "sipature-app/src/data/generated/evidence.json" ]; then
  echo "ERROR: Data generated tidak lengkap di sipature-app/src/data/generated/"
  exit 1
fi

# 3. Buat dan siapkan file .env production yang siap pakai (turnkey)
cat << 'EOF' > sipature-app/.env.production
# ============================================================================
# SIPATURE — Konfigurasi Environment Production
# ============================================================================

# Database PostgreSQL
POSTGRES_USER=sipature
POSTGRES_PASSWORD=sipature_prod_password_2026
POSTGRES_DB=sipature
POSTGRES_PORT=5432
DATABASE_URL=postgresql://sipature:sipature_prod_password_2026@localhost:5432/sipature

# Port Host Layanan (Dapat disesuaikan otomatis bila ada port conflict)
WEB_PORT=3000
INFERENCE_PORT=8000

# Inference Configuration
INFERENCE_MODEL_DIR=/app/model
INFERENCE_URL=http://localhost:8000
EOF

# Sinkronkan .env jika belum ada
if [ ! -f "sipature-app/.env" ]; then
  cp sipature-app/.env.production sipature-app/.env
fi

# 4. Buat file tarball aset
echo "Mengompresi artefak model, data olahan, dan konfigurasi environment..."
tar -czvf "${OUTPUT_FILE}" \
  ml/artifacts/models/tfidf-aspect-silver-v1 \
  sipature-app/src/data/generated \
  sipature-app/.env \
  sipature-app/.env.production

FILE_SIZE=$(du -h "${OUTPUT_FILE}" | cut -f1)

echo ""
echo "========================================================"
echo "SUKSES: File bundle telah dibuat: ${OUTPUT_FILE} (${FILE_SIZE})"
echo "========================================================"
echo ""
echo "Langkah selanjutnya untuk transfer ke server B200:"
echo "1. Upload bundle ke server via scp:"
echo "   scp ${OUTPUT_FILE} <user>@<server-b200-ip>:~/hackathon/"
echo ""
echo "2. Di server B200, jalankan:"
echo "   git clone <REPO_URL> hackathon"
echo "   cd hackathon"
echo "   ./scripts/deploy-server.sh"
echo "========================================================"
