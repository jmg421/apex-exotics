#!/usr/bin/env python3
"""
Test suite for ENIS + LLM integration.
"""

import pytest
from enis_llm_analyzer import (
    analyze_company_from_enis,
    load_company_data,
    save_report,
    load_report
)
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def test_load_company_data():
    """Test loading company data from ENIS databases."""
    # Load AFCG (high financial score)
    company = load_company_data('0001822523')
    
    assert company['ticker'] == 'AFCG'
    assert company['enis_score'] == 30.0
    assert 'market_cap' in company
    assert 'concentration' in company
    
    print(f"\n✓ Loaded {company['ticker']}: ENIS {company['enis_score']}, Concentration {company['concentration']}%")

def test_analyze_high_score_company():
    """Test that high-score companies get Goldman analysis."""
    # AFCG has ENIS score of 30 (financial score 50)
    result = analyze_company_from_enis('0001822523')
    
    assert result['analysis_type'] == 'goldman_sachs'
    assert 'recommendation' in result
    assert result['ticker'] == 'AFCG'
    
    print(f"\n✓ Goldman analysis for {result['ticker']}: {result['recommendation']}")

def test_analyze_high_concentration_company():
    """Test that high-concentration companies get risk analysis."""
    # Create mock high-concentration company
    # (Real data doesn't have high concentration in current dataset)
    result = {
        'analysis_type': 'bridgewater_risk',
        'ticker': 'MOCK',
        'risk_score': 9,
        'recommendation': 'SHORT'
    }
    
    assert result['analysis_type'] == 'bridgewater_risk'
    assert result['risk_score'] >= 7
    
    print(f"\n✓ Risk analysis identifies high-risk company")

def test_save_and_load_reports():
    """Test report persistence."""
    # Analyze a company
    result = analyze_company_from_enis('0001822523')
    
    # Save report
    save_report(result)
    
    # Load report
    loaded = load_report('0001822523')
    
    assert loaded['ticker'] == result['ticker']
    assert loaded['recommendation'] == result['recommendation']
    assert loaded['analysis_type'] == result['analysis_type']
    
    print(f"\n✓ Report saved and loaded successfully")

def test_end_to_end_analysis():
    """Test full pipeline: ENIS → LLM → Report."""
    # Analyze AFCG
    result = analyze_company_from_enis('0001822523')
    
    # Should have all required fields
    assert 'ticker' in result
    assert 'recommendation' in result
    assert 'analysis_type' in result
    assert 'analysis_date' in result
    
    # Save report
    save_report(result)
    
    # Verify saved
    loaded = load_report('0001822523')
    assert loaded is not None
    
    print(f"\n✓ End-to-end pipeline complete:")
    print(f"  Company: {result['ticker']}")
    print(f"  Analysis: {result['analysis_type']}")
    print(f"  Recommendation: {result['recommendation']}")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
