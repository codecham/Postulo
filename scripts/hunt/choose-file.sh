#!/usr/bin/env bash
# Pick a file in the macOS "Open" dialog that Chrome just showed for an upload field.
#
# Claude in Chrome can click an upload field but cannot use the system dialog it opens:
# this types the file's path into it ("Go to folder"), then confirms.
# Usage: scripts/hunt/choose-file.sh "/path/to/CV.pdf"
# Needs, once: System Settings > Privacy & Security > Accessibility, allow your terminal.
set -euo pipefail

file="${1:?usage: choose-file.sh <file>}"
[[ -f "$file" ]] || { echo "No file at $file" >&2; exit 1; }

osascript - "$file" <<'APPLESCRIPT'
on run argv
  set previousClipboard to the clipboard
  -- Paste rather than type: keystroke mangles accents in folder names
  set the clipboard to (item 1 of argv)
  tell application "Google Chrome" to activate
  delay 1
  tell application "System Events"
    keystroke "g" using {command down, shift down}
    delay 0.8
    keystroke "a" using {command down}
    keystroke "v" using {command down}
    delay 0.8
    key code 36 -- Return: go to the file
    delay 0.8
    key code 36 -- Return: open it
  end tell
  delay 0.5
  set the clipboard to previousClipboard
end run
APPLESCRIPT
