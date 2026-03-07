#!/usr/bin/env python3
"""Weekly portfolio tracking and performance report."""

import json
from pathlib import Path
from datetime import datetime
from paper_trading import load_portfolio, get_current_price, STARTING_CAPITAL
import yfinance as yf

DATA_DIR = Path(__file__).parent / "data"
TRACKING_FILE = DATA_DIR / "portfolio_tracking.json"

def load_tracking():
    """Load historical tracking data."""
    if not TRACKING_FILE.exists():
        return []
    with open(TRACKING_FILE) as f:
        return json.load(f)

def save_tracking(data):
    """Save tracking data."""
    with open(TRACKING_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_sp500_price():
    """Get S&P 500 current price."""
    try:
        spy = yf.Ticker("SPY")
        return spy.info.get('currentPrice', 0)
    except:
        return 0

def track_portfolio():
    """Record current portfolio snapshot."""
    portfolio = load_portfolio()
    tracking = load_tracking()
    
    # Calculate current values
    total_value = portfolio['cash']
    positions_detail = []
    
    for ticker, pos in portfolio['positions'].items():
        current_price = get_current_price(ticker)
        shares = pos['shares']
        avg_price = pos['avg_price']
        cost_basis = shares * avg_price
        current_value = shares * current_price
        pnl = current_value - cost_basis
        pnl_pct = (pnl / cost_basis) * 100 if cost_basis else 0
        
        total_value += current_value
        
        positions_detail.append({
            'ticker': ticker,
            'shares': shares,
            'avg_price': avg_price,
            'current_price': current_price,
            'value': current_value,
            'pnl': pnl,
            'pnl_pct': pnl_pct
        })
    
    # Calculate returns
    total_return = total_value - STARTING_CAPITAL
    total_return_pct = (total_return / STARTING_CAPITAL) * 100
    
    # Get S&P 500 for comparison
    sp500_price = get_sp500_price()
    
    # Create snapshot
    snapshot = {
        'date': datetime.now().isoformat(),
        'total_value': total_value,
        'cash': portfolio['cash'],
        'invested': total_value - portfolio['cash'],
        'total_return': total_return,
        'total_return_pct': total_return_pct,
        'positions': positions_detail,
        'sp500_price': sp500_price
    }
    
    tracking.append(snapshot)
    save_tracking(tracking)
    
    return snapshot

def show_performance():
    """Display performance report."""
    tracking = load_tracking()
    
    if not tracking:
        print("No tracking data yet. Run track_portfolio() first.")
        return
    
    latest = tracking[-1]
    
    print("="*80)
    print("PORTFOLIO PERFORMANCE REPORT")
    print("="*80)
    print()
    
    print(f"Date: {latest['date'][:10]}")
    print(f"Total Value: ${latest['total_value']:,.2f}")
    print(f"Cash: ${latest['cash']:,.2f}")
    print(f"Invested: ${latest['invested']:,.2f}")
    print()
    
    print(f"Total Return: ${latest['total_return']:+,.2f} ({latest['total_return_pct']:+.2f}%)")
    print()
    
    # Position breakdown
    print("POSITIONS:")
    print("-"*80)
    
    for pos in sorted(latest['positions'], key=lambda x: x['value'], reverse=True):
        ticker = pos['ticker']
        value = pos['value']
        pnl = pos['pnl']
        pnl_pct = pos['pnl_pct']
        allocation = (value / latest['total_value']) * 100
        
        print(f"{ticker:6} ${value:10,.2f} ({allocation:5.1f}%) | P&L: ${pnl:+9,.2f} ({pnl_pct:+6.1f}%)")
    
    print()
    
    # Historical comparison
    if len(tracking) > 1:
        first = tracking[0]
        print("HISTORICAL PERFORMANCE:")
        print("-"*80)
        
        days = (datetime.fromisoformat(latest['date']) - datetime.fromisoformat(first['date'])).days
        
        # Portfolio performance
        portfolio_return = latest['total_return_pct']
        
        # S&P 500 performance (if we have data)
        if first.get('sp500_price') and latest.get('sp500_price'):
            sp500_return = ((latest['sp500_price'] - first['sp500_price']) / first['sp500_price']) * 100
            alpha = portfolio_return - sp500_return
            
            print(f"Days Tracked: {days}")
            print(f"Portfolio: {portfolio_return:+.2f}%")
            print(f"S&P 500:   {sp500_return:+.2f}%")
            print(f"Alpha:     {alpha:+.2f}%")
        else:
            print(f"Days Tracked: {days}")
            print(f"Portfolio: {portfolio_return:+.2f}%")
    
    print()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'track':
        snapshot = track_portfolio()
        print(f"✓ Tracked portfolio: ${snapshot['total_value']:,.2f} ({snapshot['total_return_pct']:+.2f}%)")
    else:
        show_performance()
