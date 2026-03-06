#!/bin/bash
# Run the full ENIS pipeline with network intelligence

cd "$(dirname "$0")"
source venv/bin/activate

echo "=========================================="
echo "ENIS - EDGAR Network Intelligence System"
echo "Patented MGF Analysis (US 10,176,442 & 10,997,540)"
echo "=========================================="
echo ""

echo "Running all tests..."
pytest test_enis_scorer.py test_daily_digest.py test_validation.py -v --tb=short
if [ $? -ne 0 ]; then
    echo "Tests failed. Fix issues before running pipeline."
    exit 1
fi
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

echo "4. Extracting company relationships..."
python relationships.py
echo ""

echo "5. Building network graph..."
python network.py
echo ""

echo "6. Calculating MGF metrics + scoring..."
python enis_scorer.py
echo ""

echo "7. Running LLM deep analysis..."
python batch_analyzer.py
echo ""

echo "8. Generating daily digest..."
python daily_digest.py
echo ""

echo "9. Checking for alerts..."
python alerts.py
echo ""

echo "=========================================="
echo "ENIS Pipeline Complete!"
echo "View digest: cat data/digest_$(date +%Y%m%d).md"
echo "=========================================="
