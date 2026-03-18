#!/bin/bash
# Power Recovery Automation
# Runs after system reboot to restore streaming setup

LOG="/Users/apple/apex-exotics/power-recovery.log"
OBS_GLOBAL_INI="$HOME/Library/Application Support/obs-studio/global.ini"
VENV_PYTHON="/Users/apple/apex-exotics/sports-monitor/venv/bin/python3"
SPORTS_DIR="/Users/apple/apex-exotics/sports-monitor"

echo "=== Power Recovery Started: $(date) ===" >> "$LOG"

# --- Wait for real network connectivity (not just router RA) ---
echo "Waiting for network..." >> "$LOG"
for i in $(seq 1 30); do
    if ping -c1 -W2 8.8.8.8 &>/dev/null; then
        echo "Network up after ${i} attempts" >> "$LOG"
        break
    fi
    [ "$i" -eq 30 ] && echo "WARNING: Network not confirmed after 30 attempts, proceeding anyway" >> "$LOG"
    sleep 2
done

# --- Fix OBS safe mode prompt before launch ---
# OBS checks LastShutdown in global.ini. After unclean shutdown (power loss),
# it shows a Safe Mode dialog that blocks automation. Rewrite the file cleanly.
if [ -f "$OBS_GLOBAL_INI" ]; then
    # Use awk to properly replace the value (sed was corrupting the file)
    awk -F= '/^LastShutdown=/{print "LastShutdown=clean"; next} {print}' "$OBS_GLOBAL_INI" > "${OBS_GLOBAL_INI}.tmp" \
        && mv "${OBS_GLOBAL_INI}.tmp" "$OBS_GLOBAL_INI"
    echo "OBS safe mode dialog bypassed" >> "$LOG"
fi

# --- Launch OBS with auto-record ---
echo "Launching OBS with --startrecording --disable-missing-files-check..." >> "$LOG"
/Applications/OBS.app/Contents/MacOS/OBS --startrecording --disable-missing-files-check &

# Verify OBS is running
for i in $(seq 1 15); do
    if pgrep -f "OBS.app/Contents/MacOS/OBS" &>/dev/null; then
        echo "OBS confirmed running after ${i}s" >> "$LOG"
        break
    fi
    [ "$i" -eq 15 ] && echo "ERROR: OBS failed to launch" >> "$LOG"
    sleep 1
done

# --- Restart Heat Live on VSeeBox via Broadlink (with retries) ---
echo "Restarting Heat Live on VSeeBox..." >> "$LOG"
cd "$SPORTS_DIR"
for attempt in 1 2 3; do
    $VENV_PYTHON <<'PYTHON' >> "$LOG" 2>&1 && break
import sys
sys.path.insert(0, '/Users/apple/apex-exotics/sports-monitor')
from channel_switcher import send_command
import time

send_command("HOME")
time.sleep(3)
send_command("OK")
print("VSeeBox Heat Live restarted")
PYTHON
    echo "Broadlink attempt $attempt failed, retrying in 5s..." >> "$LOG"
    sleep 5
done

# --- Launch Chrome fullscreen with TV stream ---
echo "Launching Chrome fullscreen with dashboard..." >> "$LOG"
sleep 5
open -a "Google Chrome" "http://localhost:5001"
sleep 3
# Fullscreen Chrome
osascript -e '
tell application "Google Chrome" to activate
delay 1
tell application "System Events"
    keystroke "f" using {command down, control down}
end tell
' >> "$LOG" 2>&1
echo "Chrome launched fullscreen" >> "$LOG"

echo "=== Power Recovery Complete: $(date) ===" >> "$LOG"
