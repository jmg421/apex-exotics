#!/usr/bin/env python3
"""
Test suite for LLM analyzer.
"""

import pytest
from llm_client import call_llm, format_goldman_prompt, parse_recommendation

def test_llm_connection():
    """Verify we can call Claude API."""
    response = call_llm("Test prompt: respond with 'OK'")
    assert response is not None
    assert len(response) > 0
    print(f"\n✓ LLM responded: {response[:100]}")

def test_prompt_formatting():
    """Verify prompts format correctly with company data."""
    company_data = {
        'ticker': 'AFCG',
        'market_cap': 50000000,
        'revenue': 0,
        'net_margin': 0
    }
    prompt = format_goldman_prompt(company_data)
    
    assert 'AFCG' in prompt
    assert '50,000,000' in prompt or '$50' in prompt
    assert 'Goldman Sachs' in prompt
    print(f"\n✓ Prompt formatted correctly")

def test_response_parsing():
    """Verify we can extract recommendation from LLM response."""
    mock_response = """
    Based on analysis, this is a HOLD with MEDIUM conviction.
    Price target: $8.50
    """
    result = parse_recommendation(mock_response)
    
    assert result['recommendation'] == 'HOLD'
    assert result['conviction'] == 'MEDIUM'
    assert result['price_target'] == 8.50
    print(f"\n✓ Parsed: {result}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
