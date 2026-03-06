#!/usr/bin/env python3
"""
Test suite for ENIS scorer.
"""

import pytest
from enis_scorer import calculate_enis_score

def test_enis_score_financial_only():
    """Test ENIS score with only financial component."""
    financial_score = 100
    network_metrics = {
        'systemic_importance': 0,
        'network_value': 0,
        'contagion_risk': 0
    }
    
    score = calculate_enis_score(financial_score, network_metrics)
    
    assert score == 60.0  # 100 * 0.6

def test_enis_score_combined():
    """Test ENIS score with both components."""
    financial_score = 50
    network_metrics = {
        'systemic_importance': 2.0,
        'network_value': 5.0,
        'contagion_risk': 1.0
    }
    
    score = calculate_enis_score(financial_score, network_metrics)
    
    assert score > 30  # Should be > financial component alone
    assert score <= 100

def test_enis_score_high_risk():
    """Test ENIS score with high contagion risk."""
    financial_score = 80
    network_metrics = {
        'systemic_importance': 1.0,
        'network_value': 1.0,
        'contagion_risk': 10.0  # High risk
    }
    
    score = calculate_enis_score(financial_score, network_metrics)
    
    # High risk should reduce network component
    assert score < 80

def test_enis_score_bounds():
    """Test ENIS score stays within 0-100."""
    financial_score = 100
    network_metrics = {
        'systemic_importance': 100.0,
        'network_value': 100.0,
        'contagion_risk': 0
    }
    
    score = calculate_enis_score(financial_score, network_metrics)
    
    assert 0 <= score <= 100

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
