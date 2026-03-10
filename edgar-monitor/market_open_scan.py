#!/usr/bin/env python3
"""Market Open Scanner - Capture live data at 9:30 AM"""
import json
import requests
from datetime import datetime
import os

def get_tastytrade_token():
    """Get access token from refresh token"""
    # Read from .env
    refresh_token = None
    client_secret = None
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('TASTYTRADE_REFRESH_TOKEN='):
                refresh_token = line.split('=', 1)[1].strip()
            elif line.startswith('TASTYTRADE_CLIENT_SECRET='):
                client_secret = line.split('=', 1)[1].strip()
    
    url = "https://api.cert.tastyworks.com/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_secret": client_secret
    }
    resp = requests.post(url, json=data)
    return resp.json()["access_token"]

def get_market_data(symbols, token):
    """Fetch live quotes for symbols"""
    url = "https://api.cert.tastyworks.com/market-data/quotes"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"symbols": ",".join(symbols)}
    
    resp = requests.get(url, headers=headers, params=params)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:200]}")
    
    if resp.status_code != 200:
        return {"items": []}
    
    return resp.json()

def load_watchlist():
    """Load micro-cap tickers from EDGAR data"""
    try:
        with open('data/market_caps.json', 'r') as f:
            caps = json.load(f)
            # Get tickers with market cap < $100M
            tickers = [v['ticker'] for v in caps.values() 
                      if v.get('ticker') and v.get('market_cap') and v['market_cap'] < 100_000_000]
            return tickers[:50]
    except Exception as e:
        print(f"Error loading watchlist: {e}")
        return []

if __name__ == '__main__':
    print(f"🔴 MARKET OPEN SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Get watchlist
    tickers = load_watchlist()
    if not tickers:
        print("❌ No watchlist found. Run feed_parser.py first.")
        exit(1)
    
    print(f"📊 Scanning {len(tickers)} micro-caps...")
    
    # Get live data
    token = get_tastytrade_token()
    data = get_market_data(tickers, token)
    
    # Save snapshot
    snapshot = {
        'timestamp': datetime.now().isoformat(),
        'market_open': True,
        'quotes': data
    }
    
    with open('data/market_open_snapshot.json', 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    print(f"✅ Captured {len(data.get('items', []))} quotes")
    print(f"💾 Saved to data/market_open_snapshot.json")
    
    # Quick analysis
    items = data.get('items', [])
    if items:
        print("\n🔥 TOP MOVERS (Pre-market):")
        for item in sorted(items, key=lambda x: abs(x.get('change-percent', 0)), reverse=True)[:5]:
            symbol = item.get('symbol', 'N/A')
            price = item.get('last', 0)
            change = item.get('change-percent', 0)
            volume = item.get('volume', 0)
            print(f"  {symbol:6} ${price:7.2f} {change:+6.2%} | Vol: {volume:,}")
