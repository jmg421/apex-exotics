#!/usr/bin/env python3
"""Futures Market Scanner - CME contracts with pattern detection"""
import json
import requests
from datetime import datetime
import numpy as np

# Popular CME futures contracts
FUTURES_SYMBOLS = [
    'ES',   # E-mini S&P 500
    'NQ',   # E-mini Nasdaq
    'YM',   # E-mini Dow
    'RTY',  # E-mini Russell 2000
    'GC',   # Gold
    'SI',   # Silver
    'CL',   # Crude Oil
    'NG',   # Natural Gas
    'ZB',   # 30-Year Treasury Bond
    'ZN',   # 10-Year Treasury Note
]

def generate_futures_data(symbols):
    """Generate synthetic futures data (replace with real CME feed)"""
    np.random.seed(int(datetime.now().timestamp()) % 1000)
    
    quotes = []
    for symbol in symbols:
        # Realistic futures pricing
        if symbol in ['ES', 'NQ', 'YM', 'RTY']:
            base = {'ES': 5000, 'NQ': 17000, 'YM': 38000, 'RTY': 2000}[symbol]
        elif symbol in ['GC', 'SI']:
            base = {'GC': 2000, 'SI': 25}[symbol]
        elif symbol in ['CL', 'NG']:
            base = {'CL': 75, 'NG': 3}[symbol]
        else:
            base = 120
        
        change = np.random.normal(0, 0.5)  # Futures are less volatile intraday
        if np.random.random() < 0.15:  # 15% chance of big move
            change = np.random.choice([-1, 1]) * np.random.uniform(1, 3)
        
        price = base * (1 + change/100)
        volume = int(np.random.lognormal(12, 1))
        
        quotes.append({
            'symbol': symbol,
            'price': round(price, 2),
            'change': round(base * change/100, 2),
            'change_percent': round(change, 2),
            'volume': volume,
            'prev_close': round(base, 2),
            'timestamp': datetime.now().isoformat()
        })
    
    return quotes

def calculate_bracket_orders(entry_price, direction='long', stop_loss_dollars=10):
    """Calculate bracket order levels"""
    if direction == 'long':
        stop = entry_price - stop_loss_dollars
        targets = [
            entry_price + 10,  # Target 1: +$10
            entry_price + 20,  # Target 2: +$20
            entry_price + 30,  # Target 3: +$30
        ]
    else:  # short
        stop = entry_price + stop_loss_dollars
        targets = [
            entry_price - 10,
            entry_price - 20,
            entry_price - 30,
        ]
    
    return {
        'entry': entry_price,
        'stop_loss': stop,
        'targets': targets,
        'risk': stop_loss_dollars,
        'reward': [10, 20, 30],
        'risk_reward': [1.0, 2.0, 3.0]
    }

if __name__ == '__main__':
    print(f"📊 FUTURES MARKET SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    print("="*60)
    print("⚠️  Using synthetic data (replace with CME feed)")
    print("="*60)
    print()
    
    quotes = generate_futures_data(FUTURES_SYMBOLS)
    
    print("📈 FUTURES QUOTES:")
    for q in quotes:
        print(f"  {q['symbol']:6} ${q['price']:8.2f} {q['change']:+7.2f} ({q['change_percent']:+5.2f}%) | Vol: {q['volume']:,}")
    
    # Save snapshot
    snapshot = {
        'timestamp': datetime.now().isoformat(),
        'market': 'CME_FUTURES',
        'synthetic': True,
        'quotes': quotes
    }
    
    with open('data/futures_snapshot.json', 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    print()
    print(f"✅ Captured {len(quotes)} futures contracts")
    print(f"💾 Saved to data/futures_snapshot.json")
    
    # Show bracket order example
    print("\n" + "="*60)
    print("🎯 BRACKET ORDER EXAMPLE (3 contracts)")
    print("="*60)
    
    # Use ES as example
    es_quote = next(q for q in quotes if q['symbol'] == 'ES')
    entry = es_quote['price']
    
    bracket = calculate_bracket_orders(entry, direction='long', stop_loss_dollars=10)
    
    print(f"\nEntry: ${entry:.2f}")
    print(f"Stop Loss: ${bracket['stop_loss']:.2f} (-${bracket['risk']})")
    print(f"\nProfit Targets:")
    print(f"  Contract 1: ${bracket['targets'][0]:.2f} (+$10) - Exit 1/3")
    print(f"  Contract 2: ${bracket['targets'][1]:.2f} (+$20) - Exit 1/3")
    print(f"  Contract 3: ${bracket['targets'][2]:.2f} (+$30) - Exit 1/3")
    print(f"\nRisk/Reward: Risk $10 to make $60 total (6:1)")
