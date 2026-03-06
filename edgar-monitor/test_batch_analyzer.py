#!/usr/bin/env python3
"""
Test suite for batch analyzer.
"""

import pytest
from batch_analyzer import analyze_all_companies, filter_actionable
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def test_analyze_all_companies():
    """Test batch analysis of all ENIS companies."""
    results = analyze_all_companies()
    
    assert len(results) > 0
    assert all('recommendation' in r or 'risk_score' in r for r in results)
    
    print(f"\n✓ Analyzed {len(results)} companies")
    for r in results[:3]:
        print(f"  - {r['ticker']}: {r.get('recommendation', 'N/A')}")

def test_filter_actionable_recommendations():
    """Test filtering for BUY and SHORT recommendations."""
    # Load existing reports
    with open(DATA_DIR / "llm_reports.json") as f:
        reports = json.load(f)
    
    results = list(reports.values())
    actionable = filter_actionable(results)
    
    for r in actionable:
        rec = r.get('recommendation')
        risk = r.get('risk_score', 0)
        assert rec in ['BUY', 'SHORT'] or risk >= 7
    
    print(f"\n✓ Found {len(actionable)} actionable recommendations")
    for r in actionable:
        rec = r.get('recommendation') or f"Risk {r.get('risk_score')}/10"
        print(f"  - {r['ticker']}: {rec}")

def test_batch_processing_creates_reports():
    """Test that batch processing creates report files."""
    results = analyze_all_companies()
    
    # Check that reports were saved
    assert (DATA_DIR / "llm_reports.json").exists()
    
    with open(DATA_DIR / "llm_reports.json") as f:
        reports = json.load(f)
    
    assert len(reports) > 0
    print(f"\n✓ {len(reports)} reports saved")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
