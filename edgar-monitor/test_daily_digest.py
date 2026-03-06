#!/usr/bin/env python3
"""
Tests for daily digest generator.
"""

import pytest
from daily_digest import (
    load_reports,
    categorize_recommendations,
    format_company_section,
    generate_digest
)

def test_load_reports():
    """Test loading reports from JSON."""
    reports = load_reports()
    assert isinstance(reports, list)
    assert len(reports) >= 0

def test_categorize_recommendations():
    """Test categorization logic."""
    reports = [
        {'recommendation': 'BUY', 'conviction': 'HIGH'},
        {'recommendation': 'AVOID', 'conviction': 'HIGH'},
        {'recommendation': 'SHORT', 'conviction': 'MEDIUM'},
        {'recommendation': 'PASS', 'conviction': 'LOW'},
        {'recommendation': 'HEDGE', 'risk_score': 8}
    ]
    
    longs, shorts, passes = categorize_recommendations(reports)
    
    assert len(longs) == 1  # BUY with HIGH
    assert len(shorts) == 3  # AVOID/HIGH, SHORT, risk>=7
    assert len(passes) == 1  # PASS

def test_format_company_section():
    """Test company section formatting."""
    report = {
        'ticker': 'TEST',
        'cik': '0001234567',
        'recommendation': 'BUY',
        'conviction': 'HIGH',
        'price_target': 50.0,
        'enis_score': 75.0,
        'key_risks': ['Risk 1', 'Risk 2'],
        'key_opportunities': ['Opp 1', 'Opp 2']
    }
    
    section = format_company_section(report)
    assert 'TEST' in section
    assert 'BUY' in section
    assert 'HIGH' in section
    assert '$50.0' in section
    assert '75.0/100' in section

def test_generate_digest():
    """Test full digest generation."""
    digest = generate_digest()
    
    assert 'ENIS Daily Digest' in digest
    assert 'Summary' in digest
    assert 'Total Analyzed:' in digest

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
