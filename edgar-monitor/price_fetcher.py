#!/usr/bin/env python3
"""
Price data fetcher using Alpha Vantage API.
Free tier: 5 calls/min, 500 calls/day.
"""

import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime, timedelta

# Get API key from environment or use demo key
ALPHA_VANTAGE_KEY = os.environ.get('ALPHA_VANTAGE_KEY', 'demo')
BASE_URL = 'https://www.alphavantage.co/query'

def get_ticker_from_cik(cik):
    """Get ticker from CIK (load from ENIS data)."""
    scores_file = Path(__file__).parent / 'data' / 'enis_scores.json'
    if not scores_file.exists():
        return None
    
    with open(scores_file) as f:
        scores = json.load(f)
        for company in scores:
            if company.get('cik') == cik:
                return company.get('ticker')
    return None

def fetch_daily_prices(ticker, outputsize='compact'):
    """
    Fetch daily price data from Alpha Vantage.
    
    Args:
        ticker: Stock ticker symbol
        outputsize: 'compact' (100 days) or 'full' (20+ years)
    
    Returns:
        Dict of {date: close_price}
    """
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': ticker,
        'apikey': ALPHA_VANTAGE_KEY,
        'outputsize': outputsize
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        data = response.json()
        
        if 'Error Message' in data:
            print(f"Error fetching {ticker}: {data['Error Message']}")
            return None
        
        if 'Note' in data:
            print(f"Rate limit hit: {data['Note']}")
            return None
        
        time_series = data.get('Time Series (Daily)', {})
        
        # Convert to simple dict
        prices = {}
        for date, values in time_series.items():
            prices[date] = float(values['4. close'])
        
        return prices
    
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

def fetch_and_cache_prices(tickers, cache_file='data/price_cache.json'):
    """
    Fetch prices for multiple tickers with caching.
    Rate limited to 5 calls/min.
    """
    cache_path = Path(__file__).parent / cache_file
    
    # Load existing cache
    cache = {}
    if cache_path.exists():
        with open(cache_path) as f:
            cache = json.load(f)
    
    updated = False
    
    for ticker in tickers:
        # Skip if cached and recent
        if ticker in cache:
            cache_date = cache[ticker].get('fetched_at', '')
            try:
                cached = datetime.fromisoformat(cache_date)
                if datetime.now() - cached < timedelta(hours=1):
                    print(f"Using cached data for {ticker}")
                    continue
            except (ValueError, TypeError):
                pass
        
        print(f"Fetching {ticker}...")
        prices = fetch_daily_prices(ticker)
        
        if prices:
            cache[ticker] = {
                'prices': prices,
                'fetched_at': datetime.now().isoformat()
            }
            updated = True
            
            # Rate limit: 5 calls/min = 12 seconds between calls
            time.sleep(12)
    
    # Save cache
    if updated:
        cache_path.parent.mkdir(exist_ok=True)
        with open(cache_path, 'w') as f:
            json.dump(cache, f, indent=2)
        print(f"\n✓ Price cache updated: {cache_path}")
    
    return cache

def get_price_on_date(ticker, date, cache):
    """Get price for ticker on specific date from cache."""
    if ticker not in cache:
        return None
    
    prices = cache[ticker].get('prices', {})
    
    # Try exact date
    if date in prices:
        return prices[date]
    
    # Try nearby dates (market might be closed)
    try:
        target = datetime.fromisoformat(date)
        for i in range(1, 5):  # Check up to 4 days ahead
            check_date = (target + timedelta(days=i)).strftime('%Y-%m-%d')
            if check_date in prices:
                return prices[check_date]
    except (ValueError, KeyError, TypeError):
        pass
    
    return None

if __name__ == '__main__':
    # Test with ENIS companies
    print("Fetching prices for ENIS companies...")
    print("="*60)
    
    # Load tickers from ENIS data
    scores_file = Path(__file__).parent / 'data' / 'enis_scores.json'
    if scores_file.exists():
        with open(scores_file) as f:
            scores = json.load(f)
            tickers = [c['ticker'] for c in scores if c.get('ticker')]
        
        print(f"Found {len(tickers)} tickers: {', '.join(tickers)}")
        print()
        
        cache = fetch_and_cache_prices(tickers)
        
        print("\nPrice data summary:")
        for ticker in tickers:
            if ticker in cache:
                num_days = len(cache[ticker].get('prices', {}))
                print(f"  {ticker}: {num_days} days of data")
    else:
        print("No ENIS data found. Run ENIS pipeline first.")
