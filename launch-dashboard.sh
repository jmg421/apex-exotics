#!/bin/bash
# Launch default dashboard: VSeeBox stream + market chart

echo "🚀 Launching default dashboard..."

# 1. Start sports-monitor dashboard (VSeeBox stream)
echo "Starting sports-monitor dashboard..."
cd /Users/apple/apex-exotics/sports-monitor
python3 dashboard.py &
DASHBOARD_PID=$!
sleep 2

# 2. Open dashboard in Chrome
echo "Opening VSeeBox stream..."
open -a "Google Chrome" http://localhost:5001

# 3. Open market chart (TradingView)
echo "Opening market chart..."
open -a "Google Chrome" "https://www.tradingview.com/chart/?symbol=SPX"

echo "✓ Dashboard launched"
echo "  VSeeBox: http://localhost:5001"
echo "  Market Chart: TradingView"
echo ""
echo "Press Ctrl+C to stop dashboard"

# Wait for dashboard process
wait $DASHBOARD_PID
