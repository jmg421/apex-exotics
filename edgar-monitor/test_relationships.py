#!/usr/bin/env python3
"""
Test suite for ENIS relationship extractor.
Run with: pytest test_relationships.py -v
"""

import pytest
from relationships import extract_relationships

def test_extract_customer_with_percentage():
    """Test extraction of customer with revenue percentage."""
    text = "Approximately 45% of our total revenue came from Apple Inc. during the fiscal year."
    
    result = extract_relationships(text)
    
    assert len(result['customers']) == 1
    assert result['customers'][0]['name'] == 'Apple Inc'
    assert result['customers'][0]['percentage'] == 45

def test_extract_major_customer():
    """Test extraction of major customer without percentage."""
    text = "Our major customers include Microsoft Corporation and Amazon Web Services."
    
    result = extract_relationships(text)
    
    assert len(result['customers']) >= 1
    assert any('Microsoft' in c['name'] for c in result['customers'])

def test_extract_supplier():
    """Test extraction of supplier relationships."""
    text = "Our primary suppliers include Intel Corporation and Samsung Electronics."
    
    result = extract_relationships(text)
    
    assert len(result['suppliers']) >= 1
    assert any('Intel' in s['name'] for s in result['suppliers'])

def test_extract_partnership():
    """Test extraction of partnership relationships."""
    text = "We entered into a strategic partnership with Google LLC to develop new technologies."
    
    result = extract_relationships(text)
    
    assert len(result['partners']) >= 1
    assert any('Google' in p['name'] for p in result['partners'])

def test_ignore_small_customers():
    """Test that customers <10% revenue are ignored."""
    text = "We received 5% of revenue from Small Company Inc."
    
    result = extract_relationships(text)
    
    assert len(result['customers']) == 0

def test_deduplication():
    """Test that duplicate relationships are removed."""
    text = """
    Our major customer is Apple Inc.
    Apple Inc. accounted for 30% of revenue.
    We have a partnership with Apple Inc.
    """
    
    result = extract_relationships(text)
    
    # Should only have one Apple entry per category
    apple_customers = [c for c in result['customers'] if 'Apple' in c['name']]
    assert len(apple_customers) == 1

def test_empty_text():
    """Test handling of empty text."""
    result = extract_relationships("")
    
    assert result['customers'] == []
    assert result['suppliers'] == []
    assert result['partners'] == []

def test_no_relationships():
    """Test text with no relationship mentions."""
    text = "This is a filing with no customer or supplier information."
    
    result = extract_relationships(text)
    
    assert result['customers'] == []
    assert result['suppliers'] == []
    assert result['partners'] == []

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
