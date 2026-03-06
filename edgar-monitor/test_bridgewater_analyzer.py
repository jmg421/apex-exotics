#!/usr/bin/env python3
"""
Test suite for Bridgewater risk analyzer.
"""

import pytest
from bridgewater_analyzer import bridgewater_risk_analysis, parse_risk_assessment
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def load_test_company_with_concentration(ticker='TASK'):
    """Load company with concentration data."""
    # Load from relationships
    with open(DATA_DIR / "relationships.json") as f:
        relationships = json.load(f)
    
    # Find company by ticker (need to search through all)
    for cik, data in relationships.items():
        if ticker in data.get('company', ''):
            rels = data['relationships']
            concentration = max(rels.get('customer_concentration', [0])) if rels.get('customer_concentration') else 0
            
            return {
                'ticker': ticker,
                'cik': cik,
                'company': data['company'],
                'concentration': concentration,
                'market_cap': 100000000,  # Mock
                'debt_to_assets': 30
            }
    
    raise ValueError(f"Company {ticker} not found")

def test_bridgewater_risk_analysis():
    """Test risk analysis for high-concentration company."""
    company_data = {
        'ticker': 'TASK',
        'company': 'TaskUs, Inc.',
        'concentration': 87,
        'market_cap': 100000000,
        'debt_to_assets': 30
    }
    
    result = bridgewater_risk_analysis(company_data)
    
    assert 'risk_score' in result
    assert result['risk_score'] >= 7  # High concentration = high risk
    assert 'recommendation' in result
    assert result['recommendation'] in ['AVOID', 'HEDGE', 'SHORT']
    
    print(f"\n✓ Risk analysis for {company_data['ticker']}:")
    print(f"  Risk Score: {result['risk_score']}/10")
    print(f"  Recommendation: {result['recommendation']}")

def test_low_concentration_company():
    """Test that low concentration gets lower risk score."""
    company_data = {
        'ticker': 'AFCG',
        'company': 'Advanced Flower Capital Inc.',
        'concentration': 0,
        'market_cap': 50000000,
        'debt_to_assets': 50
    }
    
    result = bridgewater_risk_analysis(company_data)
    
    assert result['risk_score'] < 5  # Lower risk
    print(f"\n✓ Low concentration company:")
    print(f"  Risk Score: {result['risk_score']}/10")

def test_parse_risk_assessment():
    """Test risk assessment parsing."""
    mock_response = """
    Risk Score: 8/10
    
    This company faces extreme concentration risk.
    
    Recommendation: SHORT
    """
    
    result = parse_risk_assessment(mock_response)
    
    assert result['risk_score'] == 8
    assert result['recommendation'] == 'SHORT'
    print(f"\n✓ Parsed risk assessment correctly")

def test_high_concentration_real_data():
    """Test with actual high-concentration company from ENIS."""
    try:
        company = load_test_company_with_concentration('TaskUs')
        result = bridgewater_risk_analysis(company)
        
        print(f"\nBridgewater Risk Analysis for {company['company']}:")
        print(f"  Concentration: {company['concentration']}%")
        print(f"  Risk Score: {result['risk_score']}/10")
        print(f"  Recommendation: {result['recommendation']}")
        
        assert result['risk_score'] >= 7
    except ValueError as e:
        pytest.skip(f"Company not found: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
