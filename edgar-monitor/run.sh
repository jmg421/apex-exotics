#!/bin/bash
# Run the full EDGAR monitoring pipeline

cd "$(dirname "$0")"
source venv/bin/activate

echo "=========================================="
echo "EDGAR MICRO-CAP MONITOR"
echo "=========================================="
echo ""

echo "1. Fetching latest SEC filings..."
python feed_parser.py
echo ""

echo "2. Filtering for micro-caps (<$100M)..."
python market_cap.py
echo ""

echo "3. Parsing financial metrics..."
python financials.py
echo ""

echo "4. Scoring companies..."
python scorer.py
echo ""

echo "5. Checking for alerts..."
python alerts.py
echo ""

echo "=========================================="
echo "Pipeline complete!"
echo "=========================================="
