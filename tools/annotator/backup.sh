#!/usr/bin/env bash
# Backup progress anotasi ke folder timestamped.
# Jalankan berkala (mis. cron) atau manual sebelum kejadian penting.
set -euo pipefail
cd "$(dirname "$0")"
BACKUP_DIR="backups/$(date '+%Y%m%d-%H%M%S')"
mkdir -p "$BACKUP_DIR"
cp -f data/*.json "$BACKUP_DIR"/ 2>/dev/null || true
echo "Backup tersimpan di: $BACKUP_DIR"
ls -la "$BACKUP_DIR" 2>/dev/null || echo "(belum ada data untuk di-backup)"
