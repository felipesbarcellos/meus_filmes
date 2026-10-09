#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"
INTERVAL_SECONDS="${BACKUP_INTERVAL_SECONDS:-86400}"
DB_HOST="${DB_HOST:-db}"
DB_NAME="${MYSQL_DATABASE:?MYSQL_DATABASE is required}"

run_backup() {
  mkdir -p "$BACKUP_DIR"

  local timestamp file tmp
  timestamp="$(date +%Y%m%d_%H%M%S)"
  file="${BACKUP_DIR}/${DB_NAME}_${timestamp}.sql.gz"
  tmp="${file}.tmp"

  echo "[backup] starting dump of '${DB_NAME}' -> ${file}"

  if mysqldump -h "$DB_HOST" -uroot --no-tablespaces --single-transaction \
      --routines --triggers "$DB_NAME" | gzip > "$tmp"; then
    mv "$tmp" "$file"
    echo "[backup] completed: ${file}"
  else
    rm -f "$tmp"
    echo "[backup] FAILED to create backup" >&2
    return 1
  fi

  echo "[backup] pruning backups older than ${RETENTION_DAYS} day(s)"
  find "$BACKUP_DIR" -type f -name "${DB_NAME}_*.sql.gz" -mtime +"${RETENTION_DAYS}" -delete
}

if [[ "${1:-}" == "--loop" ]]; then
  echo "[backup] loop mode enabled (interval: ${INTERVAL_SECONDS}s, retention: ${RETENTION_DAYS}d)"
  while true; do
    run_backup || echo "[backup] an error occurred, will retry on next cycle" >&2
    sleep "$INTERVAL_SECONDS"
  done
else
  run_backup
fi
