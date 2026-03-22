#!/bin/bash
# Auto-start OBS and begin recording after boot
# OBS must have a profile/scene already configured for Elgato capture + HLS output

# Wait for desktop to be ready
sleep 10

# Launch OBS minimized if not already running
if ! pgrep -x "OBS" > /dev/null; then
    open -a "OBS" --args --minimize-to-tray
    sleep 8  # Give OBS time to initialize and connect to Elgato
fi

# Start recording via OBS websocket CLI or AppleScript
# OBS has a built-in AppleScript dictionary — use it to start recording
osascript -e '
    delay 2
    tell application "System Events"
        tell process "OBS"
            -- Cmd+Shift+R is the default OBS "Start Recording" hotkey
            keystroke "r" using {command down, shift down}
        end tell
    end tell
'

echo "[$(date)] OBS auto-start complete"
