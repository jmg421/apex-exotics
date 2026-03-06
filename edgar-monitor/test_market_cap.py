"""Test market cap fetching - TDD approach."""
import pytest
from market_cap import get_market_cap_yfinance

def test_get_market_cap_for_known_ticker():
    """Test that we can fetch market cap for a known micro-cap."""
    # AFCG is a known micro-cap in our system
    cap = get_market_cap_yfinance("AFCG")
    assert cap is not None
    assert cap > 0
    assert cap < 100_000_000  # Should be micro-cap

def test_get_market_cap_handles_invalid_ticker():
    """Test that invalid tickers return None gracefully."""
    cap = get_market_cap_yfinance("INVALID_TICKER_XYZ123")
    assert cap is None
