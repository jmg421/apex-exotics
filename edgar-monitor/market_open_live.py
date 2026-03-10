#!/usr/bin/env python3
"""Market Open Scanner - Capture live data at 9:30 AM"""
import json
import requests
from datetime import datetime
import time

def get_quote(ticker):
    """Get live quote from Alpha Vantage (free tier)"""
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': ticker,
        'apikey': 'demo'  # Free demo key
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()
        if 'Global Quote' in data:
            q = data['Global Quote']
            return {
                'symbol': ticker,
                'price': float(q.get('05. price', 0)),
                'change': float(q.get('09. change', 0)),
                'change_percent': q.get('10. change percent', '0%').rstrip('%'),
                'volume': int(q.get('06. volume', 0)),
                'timestamp': datetime.now().isoformat()
            }
    except:
        pass
    return None

def load_watchlist():
    """Load micro-cap tickers"""
    try:
        with open('data/market_caps.json', 'r') as f:
            caps = json.load(f)
            tickers = [v['ticker'] for v in caps.values() 
                      if v.get('ticker') and v.get('market_cap') and v['market_cap'] < 100_000_000]
            return tickers[:10]  # Limit to 10 for free tier
    except:
        return ['AFCG', 'CLRB', 'IBCP']  # Fallback

if __name__ == '__main__':
    print(f"🔴 MARKET OPEN SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    print("="*60)
    
    tickers = load_watchlist()
    print(f"📊 Scanning {len(tickers)} micro-caps: {', '.join(tickers)}")
    print()
    
    quotes = []
    for ticker in tickers:
        print(f"  Fetching {ticker}...", end=' ')
        quote = get_quote(ticker)
        if quote:
            quotes.append(quote)
            print(f"${quote['price']:.2f} ({quote['change_percent']:+}%)")
        else:
            print("❌")
        time.sleep(12)  # Free tier: 5 calls/min
    
    # Save snapshot
    snapshot = {
        'timestamp': datetime.now().isoformat(),
        'market_open': True,
        'quotes': quotes
    }
    
    with open('data/market_open_snapshot.json', 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    print()
    print(f"✅ Captured {len(quotes)} quotes")
    print(f"💾 Saved to data/market_open_snapshot.json")
    
    # Quick analysis
    if quotes:
        print("\n🔥 TOP MOVERS:")
        for q in sorted(quotes, key=lambda x: abs(float(x['change_percent'])), reverse=True)[:5]:
            print(f"  {q['symbol']:6} ${q['price']:7.2f} {float(q['change_percent']):+6.2f}% | Vol: {q['volume']:,}")
