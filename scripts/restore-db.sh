#!/usr/bin/env bash
# Replace the production database with a dump made by scripts/backup-db.sh.
#
# Usage: scripts/restore-db.sh backups/postulo-20261126T030000Z.dump   (or `make restore file=...`)
# The API and the worker are stopped during the restore, then started again.
set -euo pipefail
cd "$(dirname "$0")/.."

dump="${1:?Usage: scripts/restore-db.sh <file.dump>}"
[[ -f "$dump" ]] || { echo "No such file: $dump" >&2; exit 1; }
read -r -a compose <<< "docker compose ${COMPOSE_ARGS:--f compose.prod.yaml --env-file .env.prod}"

read -r -p "This replaces every row of the database with $dump. Continue? [y/N] " answer
[[ "$answer" == y ]] || { echo "Cancelled"; exit 1; }

"${compose[@]}" stop api worker
# --clean --if-exists: drop each object before recreating it from the dump
"${compose[@]}" exec -T db sh -c \
  'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner' < "$dump"
"${compose[@]}" start api worker
echo "✓ Database restored from $dump"
