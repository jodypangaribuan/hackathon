#!/usr/bin/env bash
# Jalankan annotator dengan auto-restart.
# Bila server crash, akan bangkit lagi otomatis (progress aman — tersimpan di data/).
set -uo pipefail
cd "$(dirname "$0")"

until python3 -m uvicorn app:app --host 0.0.0.0 --port 8001; do
  echo "[$(date '+%H:%M:%S')] Server berhenti — restart dalam 3 detik..."
  sleep 3
done
