#!/usr/bin/env bash
# ==============================================================================
# SIPATURE — Script Pengemasan Aset Server B200
# Jalankan script ini di laptop lokal sebelum upload/transfer ke server B200.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${ROOT_DIR}"

OUTPUT_FILE="sipature-server-bundle.tar.gz"

echo "========================================================"
echo "📦 SIPATURE: Mengemas Aset Runtime untuk Server B200"
echo "========================================================"

# 1. Validasi keberadaan file model ML
if [ ! -f "ml/artifacts/models/tfidf-aspect-silver-v1/model.joblib" ]; then
  echo "❌ Error: Model ML tidak ditemukan di ml/artifacts/models/tfidf-aspect-silver-v1/model.joblib"
  exit 1
fi

# 2. Validasi file data generated web app
if [ ! -f "sipature-app/src/data/generated/corpus.json" ] || [ ! -f "sipature-app/src/data/generated/evidence.json" ]; then
  echo "❌ Error: Data generated tidak lengkap di sipature-app/src/data/generated/"
  exit 1
fi

# 3. Pastikan .env lokal ada atau buat default
if [ ! -f "sipature-app/.env" ]; then
  echo "⚠️ sipature-app/.env tidak ditemukan, membuat dari .env.example..."
  cp sipature-app/.env.example sipature-app/.env
  sed -i '' 's/CHANGE_ME_use_a_strong_password/sipature_dev_password/g' sipature-app/.env 2>/dev/null || sed -i 's/CHANGE_ME_use_a_strong_password/sipature_dev_password/g' sipature-app/.env
fi

# 4. Buat file tarball
echo "📁 Mengompres file yang terkena .gitignore..."
tar -czvf "${OUTPUT_FILE}" \
  ml/artifacts/models/tfidf-aspect-silver-v1 \
  sipature-app/src/data/generated \
  sipature-app/.env

FILE_SIZE=$(du -h "${OUTPUT_FILE}" | cut -f1)

echo ""
echo "========================================================"
echo "✅ BERHASIL! File bundle telah dibuat: ${OUTPUT_FILE} (${FILE_SIZE})"
echo "========================================================"
echo ""
echo "Langkah selanjutnya untuk transfer ke server B200:"
echo "1. Upload bundle ke server via scp:"
echo "   scp ${OUTPUT_FILE} <user>@<server-b200-ip>:~/hackathon/"
echo ""
echo "2. Di server B200, lakukan git clone & jalankan deploy:"
echo "   git clone <REPO_URL> hackathon"
echo "   cd hackathon"
echo "   tar -xzvf ../${OUTPUT_FILE}   (atau tar -xzvf ${OUTPUT_FILE})"
echo "   ./scripts/deploy-server.sh"
echo "========================================================"
