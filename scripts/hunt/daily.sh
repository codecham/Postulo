#!/usr/bin/env bash
# The daily job hunt: start Postulo, let Claude prepare today's applications, notify.
#
# launchd starts it every morning (see install.sh). Run it by hand with `make hunt`.
# Logs: ~/Library/Logs/Postulo/hunt-<date>.log
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WEB_URL="http://localhost:${WEB_PORT:-3000}"
LOG_DIR="$HOME/Library/Logs/Postulo"
# Claude's working files (offers read, applications written): personal, kept 2 weeks
WORK_DIR="$HOME/.cache/postulo/hunt"
# launchd starts jobs with a minimal PATH: add where Homebrew, uv and claude live
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$HOME/.claude/local:$PATH"

# What Claude may do without asking: it runs unattended, so anything else is refused
ALLOWED_TOOLS=(
  "Bash(uv run python -m scripts.hunt:*)"
  "Bash(uv run python -m scripts.application_instructions:*)"
  "Bash(uv run python -m scripts.check_application:*)"
  "Read"
  # File permission checks only match Edit(path) rules, which cover Write too
  "Edit(~/.cache/postulo/**)"
  # Read an offer's full text when Chrome is not available (read-only)
  "WebFetch"
  "mcp__claude-in-chrome__*"
)

notify() {
  osascript -e "display notification \"$1\" with title \"Postulo\"" || true
}

fail() {
  echo "Hunt failed: $1"
  notify "The daily hunt failed: $1. See $LOG"
  exit 1
}

wait_for_docker() {
  docker info >/dev/null 2>&1 && return 0
  open -a Docker
  for _ in $(seq 60); do
    sleep 3
    docker info >/dev/null 2>&1 && return 0
  done
  return 1
}

main() {
  mkdir -p "$LOG_DIR"
  LOG="$LOG_DIR/hunt-$(date +%F).log"
  if [[ -t 1 ]]; then
    exec > >(tee -a "$LOG") 2>&1  # run by hand: show the progress too
  else
    exec >>"$LOG" 2>&1
  fi
  echo "=== Hunt started $(date) (log: $LOG)"
  cd "$ROOT" || fail "no repository at $ROOT"
  mkdir -p "$WORK_DIR"
  find "$WORK_DIR" -mindepth 1 -mtime +14 -delete

  echo "--- Starting Docker and Postulo"
  wait_for_docker || fail "Docker did not start"
  make up || fail "Postulo did not start"
  open -g -a "Google Chrome" || fail "Google Chrome is not installed"

  echo "--- Claude is browsing the job boards and writing applications (15 to 30 minutes)"
  (cd apps/api && claude -p "/daily-hunt" --chrome --allowedTools "${ALLOWED_TOOLS[@]}") \
    || fail "Claude stopped with an error"

  local ready
  ready="$(cd apps/api && uv run python -m scripts.hunt ready --count)" || ready="?"
  notify "$ready application(s) ready: review them, then run /send-applications"
  open -a "Google Chrome" "$WEB_URL/jobs?status=saved"
  echo "=== Hunt finished $(date): $ready ready"
}

main "$@"
