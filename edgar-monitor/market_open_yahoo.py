#!/usr/bin/env python3
"""Market Open Scanner - Yahoo Finance (no API key needed)"""
import json
import requests
from datetime import datetime

def get_quote(ticker):
    """Get live quote from Yahoo Finance"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    params = {'interval': '1m', 'range': '1d'}
    
    try:
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()
        
        result = data['chart']['result'][0]
        meta = result['meta']
        
        return {
            'symbol': ticker,
            'price': meta.get('regularMarketPrice', 0),
            'prev_close': meta.get('previousClose', 0),
            'change': meta.get('regularMarketPrice', 0) - meta.get('previousClose', 0),
            'change_percent': ((meta.get('regularMarketPrice', 0) / meta.get('previousClose', 1)) - 1) * 100,
            'volume': meta.get('regularMarketVolume', 0),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return None

def load_watchlist():
    """Load micro-cap tickers"""
    try:
        with open('data/market_caps.json', 'r') as f:
            caps = json.load(f)
            tickers = [v['ticker'] for v in caps.values() 
                      if v.get('ticker') and v.get('market_cap') and v['market_cap'] < 100_000_000]
            return tickers[:20]
    except (FileNotFoundError, json.JSONDecodeError, OSError, KeyError):
        return ['AFCG', 'CLRB', 'IBCP']

if __name__ == '__main__':
    print(f"🔴 MARKET OPEN SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    print("="*60)
    
    tickers = load_watchlist()
    print(f"📊 Scanning {len(tickers)} micro-caps...")
    print()
    
    quotes = []
    for ticker in tickers:
        quote = get_quote(ticker)
        if quote:
            quotes.append(quote)
            print(f"  {quote['symbol']:6} ${quote['price']:7.2f} {quote['change']:+6.2f} ({quote['change_percent']:+5.2f}%) | Vol: {quote['volume']:,}")
    
    # Save snapshot
    snapshot = {
        'timestamp': datetime.now().isoformat(),
        'market_open': True,
        'quotes': quotes
    }
    
    with open('data/market_open_snapshot.json', 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    print()
    print(f"✅ Captured {len(quotes)}/{len(tickers)} quotes")
    print(f"💾 Saved to data/market_open_snapshot.json")
    
    # Quick analysis
    if quotes:
        print("\n🔥 TOP MOVERS (by % change):")
        for q in sorted(quotes, key=lambda x: abs(x['change_percent']), reverse=True)[:5]:
            print(f"  {q['symbol']:6} ${q['price']:7.2f} {q['change_percent']:+6.2f}% | Vol: {q['volume']:,}")
