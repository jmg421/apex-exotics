#!/usr/bin/env python3
"""
Test suite for Goldman Sachs analyzer.
"""

import pytest
from goldman_analyzer import goldman_analysis, extract_risks, extract_opportunities
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def load_test_company(ticker='AFCG'):
    """Load company from ENIS database."""
    with open(DATA_DIR / "enis_scores.json") as f:
        companies = json.load(f)
    
    company = next((c for c in companies if c.get('ticker') == ticker), None)
    if not company:
        raise ValueError(f"Company {ticker} not found")
    
    return company

def test_goldman_analysis_structure():
    """Verify Goldman analysis returns required fields."""
    company_data = load_test_company('AFCG')
    result = goldman_analysis(company_data)
    
    assert 'recommendation' in result
    assert 'conviction' in result
    assert 'price_target' in result
    assert 'key_risks' in result
    assert 'key_opportunities' in result
    assert 'ticker' in result
    
    print(f"\n✓ Goldman analysis structure valid")

def test_goldman_analysis_with_real_data():
    """Test with actual ENIS company data."""
    company = load_test_company('AFCG')
    result = goldman_analysis(company)
    
    # Should have valid recommendation
    assert result['recommendation'] in ['BUY', 'HOLD', 'AVOID']
    assert result['conviction'] in ['HIGH', 'MEDIUM', 'LOW']
    
    # Should identify key risks
    assert len(result['key_risks']) > 0
    
    print(f"\nGoldman Analysis for {company['ticker']}:")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"  Conviction: {result['conviction']}")
    print(f"  Price Target: ${result.get('price_target', 'N/A')}")
    print(f"  Risks: {len(result['key_risks'])}")
    print(f"  Opportunities: {len(result['key_opportunities'])}")

def test_extract_risks():
    """Test risk extraction from analysis text."""
    mock_text = """
    Risk Factors:
    - High debt levels at 49.9% of assets
    - No revenue growth visibility
    - Illiquid stock with low trading volume
    """
    
    risks = extract_risks(mock_text)
    
    assert len(risks) > 0
    assert any('debt' in r.lower() for r in risks)
    print(f"\n✓ Extracted {len(risks)} risks")

def test_extract_opportunities():
    """Test opportunity extraction from analysis text."""
    mock_text = """
    Opportunities:
    - Strong cash position (25.8% of assets)
    - Profitable operations
    - Undervalued vs peers
    """
    
    opps = extract_opportunities(mock_text)
    
    assert len(opps) > 0
    assert any('cash' in o.lower() for o in opps)
    print(f"\n✓ Extracted {len(opps)} opportunities")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
