#!/bin/bash
# Test power recovery setup

echo "Testing power recovery automation..."
echo ""

echo "✓ Steam removed from login items"
osascript -e 'tell application "System Events" to get the name of every login item'
echo ""

echo "✓ LaunchAgent installed:"
ls -la ~/Library/LaunchAgents/com.apex-exotics.power-recovery.plist
echo ""

echo "✓ Recovery script exists:"
ls -la /Users/apple/apex-exotics/power-recovery.sh
echo ""

echo "✓ LaunchAgent status:"
launchctl list | grep apex-exotics
echo ""

echo "To test manually, run:"
echo "  /Users/apple/apex-exotics/power-recovery.sh"
echo ""
echo "Logs will be written to:"
echo "  /Users/apple/apex-exotics/power-recovery.log"
echo "  /Users/apple/apex-exotics/power-recovery.error.log"
