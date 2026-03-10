#!/usr/bin/env python3
"""Real Market Data via yfinance - Free, works now"""
import yfinance as yf
import json
from datetime import datetime

def get_quotes_yfinance(symbols):
    """Get real-time quotes from Yahoo Finance"""
    quotes = []
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price
            price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            prev_close = info.get('previousClose', price)
            
            if price > 0:
                change = price - prev_close
                change_pct = (change / prev_close * 100) if prev_close > 0 else 0
                
                quotes.append({
                    'symbol': symbol,
                    'price': round(price, 2),
                    'change': round(change, 2),
                    'change_percent': round(change_pct, 2),
                    'volume': info.get('volume', 0),
                    'prev_close': round(prev_close, 2),
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            print(f"  ⚠️  {symbol}: {e}")
    
    return quotes

def load_watchlist():
    """Load micro-cap tickers"""
    try:
        with open('data/market_caps.json', 'r') as f:
            caps = json.load(f)
            tickers = [v['ticker'] for v in caps.values() 
                      if v.get('ticker') and v.get('market_cap') and v['market_cap'] < 100_000_000]
            return tickers[:20]  # Limit to avoid rate limits
    except:
        return ['AFCG', 'CLRB', 'IBCP']

if __name__ == '__main__':
    print(f"📊 REAL MARKET DATA - yfinance")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    print("="*60)
    
    # Get stocks
    print("\n📈 Fetching micro-cap stocks...")
    tickers = load_watchlist()
    print(f"Scanning {len(tickers)} stocks: {', '.join(tickers[:5])}...")
    
    quotes = get_quotes_yfinance(tickers)
    
    print(f"\n✅ Got {len(quotes)}/{len(tickers)} quotes")
    print()
    
    for q in quotes:
        print(f"  {q['symbol']:6} ${q['price']:7.2f} {q['change']:+6.2f} ({q['change_percent']:+5.2f}%) | Vol: {q['volume']:,}")
    
    # Save
    snapshot = {
        'timestamp': datetime.now().isoformat(),
        'market_open': True,
        'source': 'yfinance',
        'quotes': quotes
    }
    
    with open('data/market_open_snapshot.json', 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    print()
    print(f"💾 Saved to data/market_open_snapshot.json")
    
    # Get futures
    print("\n📈 Fetching CME futures...")
    futures_symbols = ['ES=F', 'NQ=F', 'YM=F', 'RTY=F', 'GC=F', 'SI=F', 'CL=F', 'NG=F']
    futures_quotes = get_quotes_yfinance(futures_symbols)
    
    print(f"\n✅ Got {len(futures_quotes)}/{len(futures_symbols)} futures quotes")
    print()
    
    for q in futures_quotes:
        print(f"  {q['symbol']:8} ${q['price']:8.2f} {q['change']:+7.2f} ({q['change_percent']:+5.2f}%)")
    
    # Save futures
    futures_snapshot = {
        'timestamp': datetime.now().isoformat(),
        'market': 'CME_FUTURES',
        'source': 'yfinance',
        'quotes': futures_quotes
    }
    
    with open('data/futures_snapshot.json', 'w') as f:
        json.dump(futures_snapshot, f, indent=2)
    
    print()
    print(f"💾 Saved to data/futures_snapshot.json")
    print()
    print("="*60)
    print("✅ REAL DATA CAPTURED")
    print("\nNext: Run pattern detection")
    print("  python3 detect_patterns.py")
    print("  python3 futures_patterns.py")
