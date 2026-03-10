#!/bin/bash
# Complete workflow: Scan stocks + futures, detect patterns, ask Jarvis, show dashboard

echo "🚀 APEX EXOTICS - UNSUPERVISED LEARNING MARKET MONITOR"
echo "======================================================"
echo ""

echo "📊 Step 1: Scanning micro-cap stocks..."
python3 market_open_synthetic.py
echo ""

echo "🔍 Step 2: Detecting stock patterns..."
python3 detect_patterns.py
echo ""

echo "📈 Step 3: Scanning CME futures..."
python3 futures_scanner.py
echo ""

echo "🤖 Step 4: Analyzing futures with Jarvis..."
python3 futures_patterns.py
echo ""

echo "💡 Step 5: Asking Jarvis about stocks..."
python3 ask_jarvis.py
echo ""

echo "📊 FINAL DASHBOARD"
echo "======================================================"
python3 dashboard_view.py
echo ""

echo "✅ Complete! Data saved to:"
echo "   • data/market_open_snapshot.json"
echo "   • data/pattern_detection.json"
echo "   • data/futures_snapshot.json"
echo "   • data/futures_analysis.json"
echo "   • data/jarvis_analysis.json"
