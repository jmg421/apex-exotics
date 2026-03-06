#!/bin/bash
# Quick ENIS run - skip tests and data collection, just analyze existing data

cd "$(dirname "$0")"
source venv/bin/activate

echo "=========================================="
echo "ENIS Quick Analysis"
echo "=========================================="
echo ""

echo "1. Running LLM analysis on existing companies..."
python batch_analyzer.py
echo ""

echo "2. Generating daily digest..."
python daily_digest.py
echo ""

echo "3. Running validation..."
python validation.py
echo ""

echo "=========================================="
echo "Analysis Complete!"
echo ""
echo "View digest:"
echo "  cat data/digest_$(date +%Y%m%d).md"
echo ""
echo "View reports:"
echo "  cat data/llm_reports.json | jq"
echo "=========================================="
