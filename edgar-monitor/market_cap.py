#!/usr/bin/env python3
"""
Market cap filter - query company market cap and filter for micro-caps (<$100M).
Uses Alpha Vantage OVERVIEW API.
"""

import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(__file__).parent / "data"
FILINGS_FILE = DATA_DIR / "filings.json"
MARKET_CAP_FILE = DATA_DIR / "market_caps.json"

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"

MICRO_CAP_THRESHOLD = 100_000_000  # $100M

def get_ticker_from_cik(cik):
    """Map CIK to ticker symbol via SEC company tickers JSON."""
    # SEC provides a free mapping file
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {"User-Agent": "EDGAR Monitor research@apexexotics.com"}
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        
        # Find matching CIK
        cik_int = int(cik) if cik else None
        for entry in data.values():
            if entry.get("cik_str") == cik_int:
                return entry.get("ticker")
    except Exception as e:
        print(f"  ! Error mapping CIK {cik}: {e}")
    return None

def get_market_cap(ticker):
    """Query Alpha Vantage for company market cap."""
    if not API_KEY:
        print("  ! ALPHA_VANTAGE_API_KEY not set in .env")
        return None
    
    params = {
        "function": "OVERVIEW",
        "symbol": ticker,
        "apikey": API_KEY
    }
    
    try:
        resp = requests.get(ALPHA_VANTAGE_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        # Check for API errors
        if "Error Message" in data or "Note" in data:
            return None
        
        market_cap = data.get("MarketCapitalization")
        return int(market_cap) if market_cap else None
    except Exception as e:
        print(f"  ! Error fetching market cap for {ticker}: {e}")
        return None

def load_market_caps():
    """Load cached market cap data."""
    if not MARKET_CAP_FILE.exists():
        return {}
    with open(MARKET_CAP_FILE) as f:
        return json.load(f)

def save_market_caps(caps):
    """Save market cap cache."""
    DATA_DIR.mkdir(exist_ok=True)
    with open(MARKET_CAP_FILE, "w") as f:
        json.dump(caps, f, indent=2)

def filter_micro_caps():
    """Filter filings for micro-cap companies."""
    filings_db = json.load(open(FILINGS_FILE))
    market_caps = load_market_caps()
    
    micro_caps = []
    checked = 0
    max_checks = 10  # Limit to avoid rate limits
    
    print(f"Filtering {len(filings_db)} companies for micro-caps...")
    print(f"(Limiting to {max_checks} new checks to avoid rate limits)")
    print()
    
    for key, filing in filings_db.items():
        cik = filing.get("cik")
        
        # Skip if already checked
        if cik in market_caps:
            cap = market_caps[cik].get("market_cap")
            if cap and cap < MICRO_CAP_THRESHOLD:
                micro_caps.append({**filing, "market_cap": cap})
            continue
        
        # Stop if we've checked enough new ones
        if checked >= max_checks:
            continue
        
        # Map CIK to ticker
        ticker = get_ticker_from_cik(cik)
        if not ticker:
            market_caps[cik] = {"ticker": None, "market_cap": None}
            continue
        
        print(f"Checking {filing['company']} ({ticker})...")
        
        # Get market cap
        cap = get_market_cap(ticker)
        market_caps[cik] = {"ticker": ticker, "market_cap": cap}
        checked += 1
        
        if cap and cap < MICRO_CAP_THRESHOLD:
            print(f"  ✓ Micro-cap: ${cap:,}")
            micro_caps.append({**filing, "market_cap": cap, "ticker": ticker})
        elif cap:
            print(f"  ✗ Too large: ${cap:,}")
        
        # Rate limit: Alpha Vantage free tier = 25 requests/day, 5/min
        time.sleep(12)  # ~5 requests/minute
    
    save_market_caps(market_caps)
    
    print(f"\n✓ Found {len(micro_caps)} micro-cap filings")
    for filing in micro_caps:
        print(f"  • {filing['company']} ({filing.get('ticker', 'N/A')}): ${filing['market_cap']:,}")
    
    return micro_caps

if __name__ == "__main__":
    filter_micro_caps()
