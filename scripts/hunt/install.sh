#!/usr/bin/env bash
# Install the daily hunt on macOS: settings file + a launchd job every weekday morning.
#
# Usage: scripts/hunt/install.sh [HH:MM]   (default 08:00)
#        scripts/hunt/install.sh --uninstall
# launchd runs a missed job when the Mac wakes up, so a Mac asleep at 8:00 hunts later.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LABEL="app.postulo.hunt"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
SETTINGS="$HOME/.config/postulo/hunt.json"

uninstall() {
  launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
  rm -f "$PLIST"
  echo "Daily hunt removed (settings kept in $SETTINGS)."
}

create_settings() {
  [[ -f "$SETTINGS" ]] && return 0
  mkdir -p "$(dirname "$SETTINGS")"
  local email
  read -r -p "Email of your Postulo account: " email
  [[ "$email" =~ ^[^@[:space:]/\&]+@[^@[:space:]/\&]+$ ]] || { echo "Invalid email" >&2; exit 1; }
  sed "s/you@example.com/$email/" "$ROOT/scripts/hunt/settings.example.json" >"$SETTINGS"
  chmod 600 "$SETTINGS"  # it holds personal data
  echo "Settings created: $SETTINGS (add your phone, links and usual answers there)."
}

weekday_entries() {
  local hour="$1" minute="$2"
  for day in 1 2 3 4 5; do
    printf '    <dict><key>Weekday</key><integer>%s</integer><key>Hour</key><integer>%s</integer><key>Minute</key><integer>%s</integer></dict>\n' \
      "$day" "$((10#$hour))" "$((10#$minute))"
  done
}

write_plist() {
  local hour="$1" minute="$2"
  mkdir -p "$(dirname "$PLIST")"
  cat >"$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array><string>/bin/bash</string><string>$ROOT/scripts/hunt/daily.sh</string></array>
  <key>StartCalendarInterval</key>
  <array>
$(weekday_entries "$hour" "$minute")
  </array>
  <key>StandardOutPath</key><string>$HOME/Library/Logs/Postulo/launchd.log</string>
  <key>StandardErrorPath</key><string>$HOME/Library/Logs/Postulo/launchd.log</string>
</dict>
</plist>
PLIST
}

main() {
  if [[ "${1:-}" == "--uninstall" ]]; then
    uninstall
    return
  fi
  local time="${1:-08:00}"
  [[ "$time" =~ ^([01][0-9]|2[0-3]):([0-5][0-9])$ ]] || { echo "Time must be HH:MM" >&2; exit 1; }
  local hour="${BASH_REMATCH[1]}" minute="${BASH_REMATCH[2]}"
  create_settings
  mkdir -p "$HOME/Library/Logs/Postulo"
  write_plist "$hour" "$minute"
  launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
  launchctl bootstrap "gui/$(id -u)" "$PLIST"
  echo "Daily hunt installed: every weekday at $time. Run it now with \`make hunt\`."
}

main "$@"
