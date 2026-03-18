# Dashboard Launchers

## Quick Start

**If dashboard.py is already running:**
```bash
/Users/apple/apex-exotics/open-dashboard.sh
```

**Start everything from scratch:**
```bash
/Users/apple/apex-exotics/launch-dashboard.sh
```

## What Opens

1. **VSeeBox Stream** - http://localhost:5000
   - Live sports channels via sports-monitor
   - Channel switching controls
   - EPG info overlay

2. **Market Chart** - TradingView S&P 500
   - Real-time market data
   - Technical indicators
   - Multi-timeframe analysis

## Customization

### Change market chart symbol
Edit `launch-dashboard.sh` or `open-dashboard.sh`:
```bash
# For Nasdaq:
open -a "Google Chrome" "https://www.tradingview.com/chart/?symbol=NASDAQ:NDX"

# For Bitcoin:
open -a "Google Chrome" "https://www.tradingview.com/chart/?symbol=BTCUSD"

# For futures:
open -a "Google Chrome" "https://www.tradingview.com/chart/?symbol=CME_MINI:ES1!"
```

### Use Safari instead of Chrome
Replace `"Google Chrome"` with `"Safari"`:
```bash
open -a "Safari" http://localhost:5000
```

### Add edgar-monitor dashboard
Add to launcher:
```bash
cd /Users/apple/apex-exotics/edgar-monitor
python3 dashboard.py &
sleep 2
open -a "Google Chrome" http://localhost:5001
```

## Auto-launch on Login

Add to power recovery script:
```bash
# In /Users/apple/apex-exotics/power-recovery.sh
/Users/apple/apex-exotics/launch-dashboard.sh &
```

## Stop Dashboard

```bash
# Kill sports-monitor dashboard
pkill -f "python3 dashboard.py"

# Or just close the terminal window
```
