#!/bin/bash
# Quick launcher - just opens the URLs without starting servers
# Use this if dashboard.py is already running

echo "🚀 Opening dashboard views..."

# VSeeBox stream
open -a "Google Chrome" http://localhost:5001

# Market chart
open -a "Google Chrome" "https://www.tradingview.com/chart/?symbol=SPX"

echo "✓ Dashboard opened"
