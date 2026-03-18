# Power Outage Recovery - Setup Complete

## What Was Done

### 1. Steam Auto-Launch Disabled ✓
- Removed Steam from login items
- Steam will no longer launch on reboot

### 2. OBS Auto-Start with Recording ✓
- Created `/Users/apple/apex-exotics/power-recovery.sh`
- OBS launches automatically on login
- Sends Cmd+Ctrl+R to start recording after 3 seconds
- LaunchAgent installed: `com.apex-exotics.power-recovery`

### 3. VSeeBox Heat Live Restart ✓
- Uses existing Broadlink IR transmitter setup
- Sends HOME command to VSeeBox
- Sends OK to launch Heat Live app
- Uses your existing `channel_switcher.py` module

### 4. Heikin-Ashi Doji Research ✓
- Created `/Users/apple/apex-exotics/edgar-monitor/HEIKIN_ASHI_DOJI.md`
- Includes detection logic, trading signals, and integration ideas
- Ready to implement in pattern_scanner.py

## Files Created

```
/Users/apple/apex-exotics/power-recovery.sh
/Users/apple/Library/LaunchAgents/com.apex-exotics.power-recovery.plist
/Users/apple/apex-exotics/test-recovery.sh
/Users/apple/apex-exotics/edgar-monitor/HEIKIN_ASHI_DOJI.md
```

## How It Works

On next reboot:
1. System boots → User logs in
2. LaunchAgent triggers `power-recovery.sh`
3. Script waits 5 seconds for system to stabilize
4. OBS launches and starts recording
5. Broadlink sends IR commands to VSeeBox
6. Heat Live app restarts
7. All actions logged to `power-recovery.log`

## Testing

Test manually without rebooting:
```bash
/Users/apple/apex-exotics/power-recovery.sh
```

Check logs:
```bash
tail -f /Users/apple/apex-exotics/power-recovery.log
```

Verify LaunchAgent:
```bash
launchctl list | grep apex-exotics
```

## Troubleshooting

### OBS doesn't start recording
- Check OBS hotkey settings (should be Cmd+Ctrl+R)
- Verify OBS is installed in /Applications/OBS.app
- Check error log: `cat /Users/apple/apex-exotics/power-recovery.error.log`

### VSeeBox doesn't respond
- Verify Broadlink device is powered on and connected
- Test manually: `cd /Users/apple/apex-exotics/sports-monitor && ./channel_switcher.py command HOME`
- Check IR codes in `broadlink_config.py`

### Script doesn't run on login
- Reload LaunchAgent: `launchctl unload ~/Library/LaunchAgents/com.apex-exotics.power-recovery.plist && launchctl load ~/Library/LaunchAgents/com.apex-exotics.power-recovery.plist`
- Check permissions: `ls -la /Users/apple/apex-exotics/power-recovery.sh` (should be executable)

## Customization

### Change OBS recording hotkey
Edit line 21 in `power-recovery.sh`:
```applescript
keystroke "r" using {command down, control down}
```

### Adjust VSeeBox navigation sequence
Edit lines 28-32 in `power-recovery.sh` to add more commands:
```python
send_command("HOME")
time.sleep(2)
send_command("DOWN")  # Navigate to app
time.sleep(1)
send_command("OK")    # Launch app
```

### Add more startup tasks
Add new sections before the final echo in `power-recovery.sh`

## Next Steps for edgar-monitor

1. Implement Heikin-Ashi Doji detection in `pattern_scanner.py`
2. Add HA candle calculation to market data pipeline
3. Backtest HA Doji signals on historical data
4. Integrate with autonomous trading system
5. Add HA Doji visualization to dashboard

See `HEIKIN_ASHI_DOJI.md` for implementation details.
