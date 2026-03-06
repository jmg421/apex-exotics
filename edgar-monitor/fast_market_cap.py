#!/usr/bin/env python3
"""
Fast market cap checker using yfinance (free, unlimited).
"""

import json
import yfinance as yf
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent / 'data'
FILINGS_FILE = DATA_DIR / 'filings.json'
MARKET_CAPS_FILE = DATA_DIR / 'market_caps.json'
MICRO_CAP_THRESHOLD = 100_000_000  # $100M

def load_filings():
    """Load filings database."""
    with open(FILINGS_FILE) as f:
        return json.load(f)

def load_market_caps():
    """Load existing market cap data."""
    if MARKET_CAPS_FILE.exists():
        with open(MARKET_CAPS_FILE) as f:
            return json.load(f)
    return {}

def save_market_caps(caps):
    """Save market cap data."""
    with open(MARKET_CAPS_FILE, 'w') as f:
        json.dump(caps, f, indent=2)

def get_ticker_from_cik(cik):
    """Get ticker from CIK using SEC mapping."""
    import requests
    
    url = 'https://www.sec.gov/files/company_tickers.json'
    headers = {'User-Agent': 'ENIS research@apexexotics.com'}
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        tickers = resp.json()
        
        for idx, company in tickers.items():
            if str(company['cik_str']).zfill(10) == cik:
                return company.get('ticker', '')
    except:
        pass
    
    return None

def check_market_cap_yfinance(ticker):
    """Get market cap using yfinance."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info.get('marketCap', None)
    except:
        return None

def batch_check_all():
    """Check market caps for all companies."""
    filings = load_filings()
    caps = load_market_caps()
    
    print(f"Checking {len(filings)} companies...")
    print()
    
    # Get CIK to ticker mapping once
    print("Loading SEC ticker mapping...")
    import requests
    url = 'https://www.sec.gov/files/company_tickers.json'
    headers = {'User-Agent': 'ENIS research@apexexotics.com'}
    resp = requests.get(url, headers=headers, timeout=10)
    sec_tickers = resp.json()
    
    cik_to_ticker = {}
    for idx, company in sec_tickers.items():
        cik = str(company['cik_str']).zfill(10)
        ticker = company.get('ticker', '')
        cik_to_ticker[cik] = ticker
    
    print(f"✓ Loaded {len(cik_to_ticker)} ticker mappings")
    print()
    
    # Check each company
    checked = 0
    micro_caps = []
    
    for key, filing in filings.items():
        cik = filing.get('cik')
        company = filing.get('company', 'Unknown')
        
        # Skip if already checked
        if cik in caps:
            cap = caps[cik].get('market_cap')
            if cap and cap < MICRO_CAP_THRESHOLD:
                micro_caps.append({**filing, 'market_cap': cap})
            continue
        
        # Get ticker
        ticker = cik_to_ticker.get(cik) or filing.get('ticker')
        if not ticker:
            caps[cik] = {'ticker': None, 'market_cap': None}
            continue
        
        # Check market cap
        print(f"[{checked+1}] {company} ({ticker})...", end=' ', flush=True)
        cap = check_market_cap_yfinance(ticker)
        
        caps[cik] = {'ticker': ticker, 'market_cap': cap}
        checked += 1
        
        if cap:
            if cap < MICRO_CAP_THRESHOLD:
                print(f"${cap:,} ✓ MICRO-CAP")
                micro_caps.append({**filing, 'market_cap': cap, 'ticker': ticker})
            else:
                print(f"${cap:,}")
        else:
            print("No data")
        
        # Save every 10
        if checked % 10 == 0:
            save_market_caps(caps)
    
    save_market_caps(caps)
    
    print()
    print("="*60)
    print(f"✓ Found {len(micro_caps)} micro-cap companies (<$100M)")
    print("="*60)
    
    # Sort by market cap
    micro_caps.sort(key=lambda x: x.get('market_cap', 0))
    
    for filing in micro_caps:
        company = filing.get('company', 'Unknown')
        ticker = filing.get('ticker', 'N/A')
        cap = filing.get('market_cap', 0)
        print(f"  {ticker:6} ${cap:>12,}  {company}")
    
    return micro_caps

if __name__ == '__main__':
    print("="*60)
    print("ENIS Fast Market Cap Checker (yfinance)")
    print("="*60)
    print()
    
    micro_caps = batch_check_all()
    
    print()
    print(f"Next: Run financials.py to analyze these {len(micro_caps)} companies")
