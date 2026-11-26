#!/usr/bin/env bash
# Create an env file from its example, filling every secret with a fresh random value.
# Never overwrites an existing file.
#
# Usage: scripts/generate-env.sh                                  (.env from .env.example)
#        scripts/generate-env.sh .env.prod.example .env.prod      (production stack)
set -euo pipefail
cd "$(dirname "$0")/.."

example="${1:-.env.example}"
target="${2:-.env}"

if [[ -f "$target" ]]; then
  echo "✓ $target already exists, left unchanged"
  exit 0
fi

random_secret() { openssl rand -hex 32; }

while IFS= read -r line || [[ -n "$line" ]]; do
  case "$line" in
    POSTGRES_PASSWORD= | JWT_SECRET_KEY=) echo "${line}$(random_secret)" ;;
    *) echo "$line" ;;
  esac
done < "$example" > "$target"
chmod 600 "$target"

echo "✓ $target created with freshly generated secrets"
