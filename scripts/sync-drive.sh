#!/usr/bin/env bash
# ============================================================================
# sync-drive.sh — sinkronisasi artifact ML antara Google Drive dan folder lokal.
#
# Google Drive adalah "source of truth" untuk artifact restricted (hasil Colab).
# Script ini menyamakan folder lokal (ml/) dengan Drive (atau sebaliknya).
#
# PRASYARAT: rclone sudah terpasang & remote `gdrive` mengarah ke My Drive.
#   brew install rclone
#   rclone config   # pilih "drive", ikuti OAuth, beri nama remote "gdrive"
#
#   # Bila remote menunjuk ke folder SIPATURE langsung, set:
#   export RCLONE_REMOTE="gdrive:SIPATURE"
#   # Bila remote menunjuk ke My Drive root:
#   export RCLONE_REMOTE="gdrive:/My Drive/SIPATURE"
#
# Penggunaan:
#   scripts/sync-drive.sh pull   # Drive -> lokal (ambil data terbaru)
#   scripts/sync-drive.sh push   # lokal -> Drive (unggah hasil lokal)
# ============================================================================
set -euo pipefail

RCLONE_REMOTE="${RCLONE_REMOTE:-gdrive:/My Drive/SIPATURE}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Mapping "<drive-subdir>|<local-subdir>" (relatif terhadap REPO_ROOT).
# `runs/` sengaja TIDAK disertakan (besar, model IndoBERT ~GB).
MAPPINGS=(
  "data/raw|ml/data/raw"
  "data/interim|ml/data/interim"
  "data/processed|ml/data/processed"
  "data/annotations|ml/data/annotations"
  "data/splits|ml/data/splits"
  "models|ml/artifacts/models"
  "metrics|ml/artifacts/metrics"
  "figures|ml/artifacts/figures"
  "reports|ml/artifacts/reports"
  "a9|ml/artifacts/a9"
  "predictions|ml/artifacts/predictions"
)

# File yang tidak ikut disinkronkan (ditrack git / noise OS).
EXCLUDES=(
  "--exclude" "README.md"
  "--exclude" ".gitkeep"
  "--exclude" ".DS_Store"
)

mode="${1:-}"
case "$mode" in
  pull)
    for pair in "${MAPPINGS[@]}"; do
      drive_rel="${pair%%|*}"; local_rel="${pair##*|}"
      local_dir="$REPO_ROOT/$local_rel"
      mkdir -p "$local_dir"
      echo "▼ $drive_rel  ⇒  $local_rel"
      rclone sync "$RCLONE_REMOTE/$drive_rel" "$local_dir" "${EXCLUDES[@]}"
    done
    echo "Sinkronisasi pull selesai."
    ;;
  push)
    for pair in "${MAPPINGS[@]}"; do
      drive_rel="${pair%%|*}"; local_rel="${pair##*|}"
      local_dir="$REPO_ROOT/$local_rel"
      [ -d "$local_dir" ] || continue
      echo "▲ $local_rel  ⇒  $drive_rel"
      rclone sync "$local_dir" "$RCLONE_REMOTE/$drive_rel" "${EXCLUDES[@]}"
    done
    echo "Sinkronisasi push selesai."
    ;;
  *)
    echo "Usage: $0 [pull|push]" >&2
    echo "  pull  = Google Drive -> lokal (ambil data terbaru dari Drive)" >&2
    echo "  push  = lokal -> Google Drive (unggah hasil lokal)" >&2
    exit 2
    ;;
esac
