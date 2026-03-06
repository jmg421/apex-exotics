#!/usr/bin/env python3
"""
Market cap filter - query company market cap and filter for micro-caps (<$100M).
Uses yfinance (free, no API key needed).
"""

import json
import asyncio
import requests
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
FILINGS_FILE = DATA_DIR / "filings.json"
MARKET_CAP_FILE = DATA_DIR / "market_caps.json"

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

def get_market_cap_yfinance(ticker):
    """Get market cap using yfinance (free, no API key)."""
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        info = stock.info
        return info.get('marketCap')
    except Exception as e:
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

async def filter_micro_caps_async():
    """Filter filings for micro-cap companies using yfinance."""
    filings_db = json.load(open(FILINGS_FILE))
    market_caps = load_market_caps()
    
    micro_caps = []
    checked = 0
    max_checks = 50  # yfinance is free, check more
    
    print(f"Filtering {len(filings_db)} companies for micro-caps...")
    print(f"(Checking up to {max_checks} new companies)")
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
        
        print(f"[{checked+1}/{max_checks}] {filing['company']} ({ticker})...", end=" ")
        
        # Get market cap via yfinance
        cap = get_market_cap_yfinance(ticker)
        market_caps[cik] = {"ticker": ticker, "market_cap": cap}
        checked += 1
        
        if cap and cap < MICRO_CAP_THRESHOLD:
            print(f"✓ ${cap:,}")
            micro_caps.append({**filing, "market_cap": cap, "ticker": ticker})
        elif cap:
            print(f"✗ ${cap:,}")
        else:
            print(f"? No data")
        
        # Small delay
        await asyncio.sleep(0.3)
    
    save_market_caps(market_caps)
    
    print(f"\n{'='*70}")
    print(f"✓ Found {len(micro_caps)} micro-cap filings")
    print(f"{'='*70}")
    for filing in sorted(micro_caps, key=lambda x: x['market_cap']):
        print(f"  • {filing['company'][:45]:45} ({filing.get('ticker', 'N/A'):6}): ${filing['market_cap']:>12,}")
    
    return micro_caps

def filter_micro_caps():
    """Sync wrapper for async function."""
    return asyncio.run(filter_micro_caps_async())

if __name__ == "__main__":
    filter_micro_caps()
