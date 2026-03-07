#!/usr/bin/env python3
"""Paper trading system for ENIS recommendations."""

import json
from pathlib import Path
from datetime import datetime
import yfinance as yf

DATA_DIR = Path(__file__).parent / "data"
PORTFOLIO_FILE = DATA_DIR / "paper_portfolio.json"
TRADES_FILE = DATA_DIR / "paper_trades.json"

STARTING_CAPITAL = 100_000  # $100k paper money

def init_portfolio():
    """Initialize paper trading portfolio."""
    portfolio = {
        'cash': STARTING_CAPITAL,
        'positions': {},
        'created': datetime.now().isoformat(),
        'total_value': STARTING_CAPITAL
    }
    
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(portfolio, f, indent=2)
    
    with open(TRADES_FILE, 'w') as f:
        json.dump([], f, indent=2)
    
    print(f"✓ Initialized paper portfolio with ${STARTING_CAPITAL:,}")
    return portfolio

def load_portfolio():
    """Load current portfolio."""
    if not PORTFOLIO_FILE.exists():
        return init_portfolio()
    
    with open(PORTFOLIO_FILE) as f:
        return json.load(f)

def load_trades():
    """Load trade history."""
    if not TRADES_FILE.exists():
        return []
    
    with open(TRADES_FILE) as f:
        return json.load(f)

def save_portfolio(portfolio):
    """Save portfolio."""
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(portfolio, f, indent=2)

def save_trades(trades):
    """Save trades."""
    with open(TRADES_FILE, 'w') as f:
        json.dump(trades, f, indent=2)

def get_current_price(ticker):
    """Get current stock price."""
    try:
        stock = yf.Ticker(ticker)
        return stock.info.get('currentPrice', 0)
    except:
        return 0

def buy(ticker, shares, reason=""):
    """Execute paper buy order."""
    portfolio = load_portfolio()
    trades = load_trades()
    
    price = get_current_price(ticker)
    if not price:
        print(f"✗ Could not get price for {ticker}")
        return False
    
    cost = price * shares
    
    if cost > portfolio['cash']:
        print(f"✗ Insufficient funds: ${cost:,.2f} needed, ${portfolio['cash']:,.2f} available")
        return False
    
    # Execute trade
    portfolio['cash'] -= cost
    
    if ticker in portfolio['positions']:
        # Add to existing position
        pos = portfolio['positions'][ticker]
        total_shares = pos['shares'] + shares
        avg_price = ((pos['shares'] * pos['avg_price']) + (shares * price)) / total_shares
        pos['shares'] = total_shares
        pos['avg_price'] = avg_price
    else:
        # New position
        portfolio['positions'][ticker] = {
            'shares': shares,
            'avg_price': price,
            'opened': datetime.now().isoformat()
        }
    
    # Record trade
    trade = {
        'date': datetime.now().isoformat(),
        'action': 'BUY',
        'ticker': ticker,
        'shares': shares,
        'price': price,
        'total': cost,
        'reason': reason
    }
    trades.append(trade)
    
    save_portfolio(portfolio)
    save_trades(trades)
    
    print(f"✓ BUY {shares} {ticker} @ ${price:.2f} = ${cost:,.2f}")
    print(f"  Cash remaining: ${portfolio['cash']:,.2f}")
    
    return True

def sell(ticker, shares, reason=""):
    """Execute paper sell order."""
    portfolio = load_portfolio()
    trades = load_trades()
    
    if ticker not in portfolio['positions']:
        print(f"✗ No position in {ticker}")
        return False
    
    pos = portfolio['positions'][ticker]
    if shares > pos['shares']:
        print(f"✗ Cannot sell {shares} shares, only {pos['shares']} owned")
        return False
    
    price = get_current_price(ticker)
    if not price:
        print(f"✗ Could not get price for {ticker}")
        return False
    
    # Execute trade
    proceeds = price * shares
    portfolio['cash'] += proceeds
    
    # Update position
    pos['shares'] -= shares
    if pos['shares'] == 0:
        del portfolio['positions'][ticker]
    
    # Record trade
    pnl = (price - pos['avg_price']) * shares
    trade = {
        'date': datetime.now().isoformat(),
        'action': 'SELL',
        'ticker': ticker,
        'shares': shares,
        'price': price,
        'total': proceeds,
        'pnl': pnl,
        'reason': reason
    }
    trades.append(trade)
    
    save_portfolio(portfolio)
    save_trades(trades)
    
    print(f"✓ SELL {shares} {ticker} @ ${price:.2f} = ${proceeds:,.2f}")
    print(f"  P&L: ${pnl:+,.2f} ({(pnl/(pos['avg_price']*shares))*100:+.1f}%)")
    print(f"  Cash: ${portfolio['cash']:,.2f}")
    
    return True

def show_portfolio():
    """Display current portfolio."""
    portfolio = load_portfolio()
    
    print("="*80)
    print("PAPER TRADING PORTFOLIO")
    print("="*80)
    print()
    
    print(f"Cash: ${portfolio['cash']:,.2f}")
    print()
    
    if not portfolio['positions']:
        print("No positions")
        print()
        print(f"Total Value: ${portfolio['cash']:,.2f}")
        return
    
    print("POSITIONS:")
    print("-"*80)
    
    total_value = portfolio['cash']
    
    for ticker, pos in portfolio['positions'].items():
        current_price = get_current_price(ticker)
        shares = pos['shares']
        avg_price = pos['avg_price']
        cost_basis = shares * avg_price
        current_value = shares * current_price
        pnl = current_value - cost_basis
        pnl_pct = (pnl / cost_basis) * 100 if cost_basis else 0
        
        total_value += current_value
        
        print(f"{ticker:6} {shares:6.0f} shares @ ${avg_price:7.2f} avg")
        print(f"       Current: ${current_price:7.2f} | Value: ${current_value:10,.2f}")
        print(f"       P&L: ${pnl:+10,.2f} ({pnl_pct:+6.1f}%)")
        print()
    
    print("-"*80)
    print(f"Total Value: ${total_value:,.2f}")
    
    total_return = total_value - STARTING_CAPITAL
    total_return_pct = (total_return / STARTING_CAPITAL) * 100
    print(f"Total Return: ${total_return:+,.2f} ({total_return_pct:+.1f}%)")
    print()

def show_trades():
    """Display trade history."""
    trades = load_trades()
    
    if not trades:
        print("No trades yet")
        return
    
    print("="*80)
    print("TRADE HISTORY")
    print("="*80)
    print()
    
    for trade in trades:
        action = trade['action']
        ticker = trade['ticker']
        shares = trade['shares']
        price = trade['price']
        total = trade['total']
        date = trade['date'][:10]
        
        print(f"{date} {action:4} {shares:4.0f} {ticker:6} @ ${price:7.2f} = ${total:10,.2f}")
        
        if 'pnl' in trade:
            pnl = trade['pnl']
            print(f"         P&L: ${pnl:+10,.2f}")
        
        if trade.get('reason'):
            print(f"         Reason: {trade['reason']}")
        print()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        show_portfolio()
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command == 'init':
        init_portfolio()
    
    elif command == 'buy':
        if len(sys.argv) < 4:
            print("Usage: python paper_trading.py buy TICKER SHARES [REASON]")
            sys.exit(1)
        ticker = sys.argv[2].upper()
        shares = int(sys.argv[3])
        reason = ' '.join(sys.argv[4:]) if len(sys.argv) > 4 else ""
        buy(ticker, shares, reason)
    
    elif command == 'sell':
        if len(sys.argv) < 4:
            print("Usage: python paper_trading.py sell TICKER SHARES [REASON]")
            sys.exit(1)
        ticker = sys.argv[2].upper()
        shares = int(sys.argv[3])
        reason = ' '.join(sys.argv[4:]) if len(sys.argv) > 4 else ""
        sell(ticker, shares, reason)
    
    elif command == 'portfolio':
        show_portfolio()
    
    elif command == 'trades':
        show_trades()
    
    else:
        print("Commands: init, buy, sell, portfolio, trades")
