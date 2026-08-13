#!/usr/bin/env bash
# ============================================================================
# refresh.sh — refresh seluruh stack setelah experiment ML baru.
#
# Siklus lengkap (satu perintah untuk lockdown/final):
#   1. Sinkronisasi artifact dari Google Drive (bila rclone tersedia).
#   2. Regenerate bundle aplikasi (places/interventions/corpus.json).
#   3. Pastikan PostgreSQL hidup + seed ulang (atomic).
#   4. Rebuild & restart service web + inference.
#
# Jalankan dari mana saja:
#   scripts/refresh.sh
#
# Opsional (skip langkah):
#   scripts/refresh.sh --no-sync      # tanpa sinkronisasi Drive
#   scripts/refresh.sh --no-generate  # tanpa regenerate bundle (pakai yang ada)
# ============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_DIR="$REPO_ROOT/sipature-app"

DO_SYNC=true
DO_GENERATE=true
for arg in "$@"; do
  case "$arg" in
    --no-sync) DO_SYNC=false ;;
    --no-generate) DO_GENERATE=false ;;
  esac
done

# Baca .env untuk kredensial DB (jika ada).
if [ -f "$APP_DIR/.env" ]; then
  set -a; . "$APP_DIR/.env"; set +a
fi
POSTGRES_USER="${POSTGRES_USER:-sipature}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-sipature_dev_password}"
POSTGRES_DB="${POSTGRES_DB:-sipature}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:${POSTGRES_PORT}/${POSTGRES_DB}"

# 1. Sync dari Drive (opsional).
if [ "$DO_SYNC" = true ] && command -v rclone >/dev/null 2>&1; then
  echo "==> [1/4] Sinkronisasi Google Drive -> lokal"
  "$REPO_ROOT/scripts/sync-drive.sh" pull || echo "   (sync dilewati — rclone belum terkonfigurasi?)"
else
  echo "==> [1/4] Sync dilewati"
fi

# 2. Regenerate bundle.
if [ "$DO_GENERATE" = true ]; then
  echo "==> [2/4] Regenerate product data"
  (cd "$APP_DIR" && npm run data:generate)
else
  echo "==> [2/4] Regenerate dilewati"
fi

# 3. DB up + seed (atomic).
echo "==> [3/4] Start db + seed"
(cd "$APP_DIR" && docker compose up -d db >/dev/null)
for _ in $(seq 1 30); do
  if docker exec sipature-db pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
(cd "$APP_DIR" && DATABASE_URL="$DATABASE_URL" npm run db:seed)

# 4. Rebuild & restart web + inference.
echo "==> [4/4] Rebuild & restart web + inference"
(cd "$APP_DIR" && docker compose up -d --build web inference)

echo ""
echo "Selesai. Verifikasi:"
echo "  curl http://localhost:3000/api/health"
echo "  curl http://localhost:8000/health"
