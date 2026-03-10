#!/usr/bin/env python3
"""Market Open Scanner - Generate synthetic data for unsupervised learning demo"""
import json
import numpy as np
from datetime import datetime

def generate_market_open_data(tickers):
    """Generate realistic market open data for micro-caps"""
    np.random.seed(int(datetime.now().timestamp()) % 1000)
    
    quotes = []
    for ticker in tickers:
        # Realistic micro-cap behavior
        base_price = np.random.uniform(1, 50)
        change_pct = np.random.normal(0, 3)  # Mean 0%, StdDev 3%
        volume = int(np.random.lognormal(11, 1.5))  # Log-normal distribution
        
        # Add some anomalies (10% chance of big move)
        if np.random.random() < 0.1:
            change_pct = np.random.choice([-1, 1]) * np.random.uniform(5, 15)
        
        price = base_price * (1 + change_pct/100)
        
        quotes.append({
            'symbol': ticker,
            'price': round(price, 2),
            'change': round(base_price * change_pct/100, 2),
            'change_percent': round(change_pct, 2),
            'volume': volume,
            'prev_close': round(base_price, 2),
            'timestamp': datetime.now().isoformat()
        })
    
    return quotes

def load_watchlist():
    """Load micro-cap tickers"""
    try:
        with open('data/market_caps.json', 'r') as f:
            caps = json.load(f)
            tickers = [v['ticker'] for v in caps.values() 
                      if v.get('ticker') and v.get('market_cap') and v['market_cap'] < 100_000_000]
            return tickers[:30]
    except:
        return ['AFCG', 'CLRB', 'IBCP', 'PMVP', 'AGLY']

if __name__ == '__main__':
    print(f"🔴 MARKET OPEN SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    print("="*60)
    print("⚠️  Using synthetic data (API rate limits)")
    print("    Replace with real feed for production")
    print("="*60)
    print()
    
    tickers = load_watchlist()
    print(f"📊 Scanning {len(tickers)} micro-caps...")
    print()
    
    quotes = generate_market_open_data(tickers)
    
    for q in quotes:
        print(f"  {q['symbol']:6} ${q['price']:7.2f} {q['change']:+6.2f} ({q['change_percent']:+5.2f}%) | Vol: {q['volume']:,}")
    
    # Save snapshot
    snapshot = {
        'timestamp': datetime.now().isoformat(),
        'market_open': True,
        'synthetic': True,
        'quotes': quotes
    }
    
    with open('data/market_open_snapshot.json', 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    print()
    print(f"✅ Captured {len(quotes)} quotes")
    print(f"💾 Saved to data/market_open_snapshot.json")
    
    # Quick analysis
    print("\n🔥 TOP MOVERS (by % change):")
    for q in sorted(quotes, key=lambda x: abs(x['change_percent']), reverse=True)[:5]:
        print(f"  {q['symbol']:6} ${q['price']:7.2f} {q['change_percent']:+6.2f}% | Vol: {q['volume']:,}")
    
    print("\n📈 VOLUME LEADERS:")
    for q in sorted(quotes, key=lambda x: x['volume'], reverse=True)[:5]:
        print(f"  {q['symbol']:6} Vol: {q['volume']:,} | Price: ${q['price']:.2f} ({q['change_percent']:+.2f}%)")
