#!/usr/bin/env python3
"""
Tests for validation framework.
"""

import pytest
from validation import (
    calculate_return,
    calculate_hit_rate,
    calculate_alpha,
    analyze_prompt_effectiveness
)

def test_calculate_return():
    """Test return calculation."""
    prices = {
        '0001234567': {
            '2026-01-01': 100.0,
            '2026-02-01': 110.0,
            '2026-03-01': 90.0
        }
    }
    
    # Positive return
    ret = calculate_return('0001234567', '2026-01-01', '2026-02-01', prices)
    assert ret == 0.1  # 10% gain
    
    # Negative return
    ret = calculate_return('0001234567', '2026-02-01', '2026-03-01', prices)
    assert abs(ret - (-0.1818)) < 0.001  # ~18% loss
    
    # Missing data
    ret = calculate_return('0009999999', '2026-01-01', '2026-02-01', prices)
    assert ret is None

def test_calculate_hit_rate():
    """Test hit rate calculation."""
    reports = {
        '0001234567': {
            'recommendation': 'BUY',
            'conviction': 'HIGH',
            'analysis_date': '2026-01-01'
        },
        '0009876543': {
            'recommendation': 'SHORT',
            'conviction': 'MEDIUM',
            'analysis_date': '2026-01-01'
        }
    }
    
    prices = {
        '0001234567': {
            '2026-01-01': 100.0,
            '2026-01-31': 110.0  # BUY was correct
        },
        '0009876543': {
            '2026-01-01': 50.0,
            '2026-01-31': 45.0  # SHORT was correct
        }
    }
    
    results = calculate_hit_rate(reports, prices)
    
    assert results['total'] == 2
    assert results['correct'] == 2
    assert results['hit_rate'] == 1.0  # 100% hit rate

def test_calculate_alpha():
    """Test alpha calculation."""
    reports = {
        '0001234567': {
            'recommendation': 'BUY',
            'analysis_date': '2026-01-01'
        }
    }
    
    prices = {
        '0001234567': {
            '2026-01-01': 100.0,
            '2026-01-31': 110.0  # 10% return
        }
    }
    
    alpha = calculate_alpha(reports, prices, sp500_return=0.08)
    
    assert alpha is not None
    assert alpha['portfolio_return'] == 0.1
    assert alpha['num_positions'] == 1
    assert alpha['alpha'] > 0  # Outperformed S&P 500

def test_analyze_prompt_effectiveness():
    """Test prompt effectiveness analysis."""
    reports = {
        '0001234567': {
            'analysis_type': 'goldman_sachs',
            'recommendation': 'BUY',
            'conviction': 'HIGH'
        },
        '0009876543': {
            'analysis_type': 'goldman_sachs',
            'recommendation': 'AVOID',
            'conviction': 'HIGH'
        },
        '0005555555': {
            'analysis_type': 'bridgewater',
            'recommendation': 'SHORT',
            'conviction': 'MEDIUM'
        }
    }
    
    stats = analyze_prompt_effectiveness(reports)
    
    assert 'goldman_sachs' in stats
    assert stats['goldman_sachs']['count'] == 2
    assert stats['goldman_sachs']['avg_conviction'] == 3.0
    
    assert 'bridgewater' in stats
    assert stats['bridgewater']['count'] == 1
    assert stats['bridgewater']['avg_conviction'] == 2.0

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
