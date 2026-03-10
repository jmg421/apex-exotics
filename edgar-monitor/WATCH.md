# How to Watch the Autonomous System

## Option 1: Live Dashboard (Recommended)
```bash
python3 dashboard_live.py
```
- Refreshes every 10 seconds
- Shows recent signals and decisions
- Clean, easy to read

## Option 2: Continuous Monitoring
```bash
./watch_autonomous.sh
```
- Runs scans every 5 minutes during market hours
- Shows full output in terminal
- Logs everything to files

## Option 3: Manual Scans
```bash
# Run once
python3 autonomous.py

# View signals
cat data/autonomous_signals.json

# View log
tail -f data/autonomous_log.txt
```

## Option 4: Background Process
```bash
# Run in background
nohup ./watch_autonomous.sh > autonomous_output.log 2>&1 &

# Check if running
ps aux | grep watch_autonomous

# View output
tail -f autonomous_output.log

# Stop it
pkill -f watch_autonomous
```

## Files to Monitor

- `data/autonomous_signals.json` - All trade signals
- `data/autonomous_log.txt` - Full activity log
- `data/pattern_detection.json` - Stock patterns
- `data/futures_analysis.json` - Futures analysis
- `data/news_context.json` - News analysis

## Quick Commands

```bash
# See latest decision
tail -1 data/autonomous_signals.json | python3 -m json.tool

# Count total scans
wc -l data/autonomous_signals.json

# See all TRADE signals
grep '"action": "TRADE"' data/autonomous_signals.json

# Watch log in real-time
tail -f data/autonomous_log.txt
```
