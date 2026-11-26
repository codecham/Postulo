#!/usr/bin/env bash
# Dump the production database into backups/, and keep only the most recent dumps.
#
# Usage: scripts/backup-db.sh            (or `make backup`)
# Env:   BACKUP_DIR (default: backups), BACKUP_KEEP (default: 14 dumps),
#        COMPOSE_ARGS (default: the production stack)
#
# Run it every night from cron on the server, for example:
#   0 3 * * * cd /srv/postulo && scripts/backup-db.sh >> backups/backup.log 2>&1
# Then copy backups/ off the server (another disk, object storage...): a backup kept
# on the same machine does not survive the loss of that machine.
set -euo pipefail
cd "$(dirname "$0")/.."

backup_dir="${BACKUP_DIR:-backups}"
keep="${BACKUP_KEEP:-14}"
read -r -a compose <<< "docker compose ${COMPOSE_ARGS:--f compose.prod.yaml --env-file .env.prod}"

mkdir -p "$backup_dir"
chmod 700 "$backup_dir"
target="$backup_dir/postulo-$(date -u +%Y%m%dT%H%M%SZ).dump"

# Custom format (-Fc): compressed, and pg_restore can restore it table by table.
# The variables are expanded inside the container, where they hold the real values.
"${compose[@]}" exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$target.partial"
mv "$target.partial" "$target"
chmod 600 "$target"
echo "✓ Database saved to $target ($(du -h "$target" | cut -f1))"

# Delete the oldest dumps beyond the number to keep
old_dumps=$(ls -1t "$backup_dir"/postulo-*.dump | tail -n +"$((keep + 1))")
for dump in $old_dumps; do
  rm -- "$dump"
  echo "  removed old backup $dump"
done
