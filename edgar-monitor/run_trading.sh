#!/bin/bash
# Daily trading workflow - run this once per day

set -e

echo "🚀 ENIS Trading System - Daily Run"
echo "=================================="
echo ""

# Activate venv
source venv/bin/activate

# 1. Run batch analysis
echo "📊 Step 1: Analyzing all companies..."
python auto_trader.py

echo ""
echo "=================================="

# 2. Monitor positions
echo "📈 Step 2: Checking open positions..."
python position_monitor.py

echo ""
echo "=================================="

# 3. Generate report
echo "📋 Step 3: Generating daily report..."
python daily_report.py

echo ""
echo "✅ Daily run complete!"
echo ""
echo "Review: data/trading_report_$(date +%Y-%m-%d).md"
