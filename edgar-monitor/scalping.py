#!/usr/bin/env python3
"""Paper trading simulator for futures scalping."""

from pathlib import Path
import json
from datetime import datetime

DATA_DIR = Path(__file__).parent / "data"
SCALPING_FILE = DATA_DIR / "scalping_trades.json"

# Starting with $10k for scalping (separate from main portfolio)
SCALPING_CAPITAL = 10000

def load_scalping_account():
    """Load scalping account state."""
    if SCALPING_FILE.exists():
        with open(SCALPING_FILE) as f:
            return json.load(f)
    
    return {
        "starting_capital": SCALPING_CAPITAL,
        "cash": SCALPING_CAPITAL,
        "position": None,  # {contract, side, entry_price, contracts, entry_time}
        "trades": [],
        "total_pnl": 0
    }

def save_scalping_account(account):
    """Save scalping account state."""
    with open(SCALPING_FILE, 'w') as f:
        json.dump(account, f, indent=2)

def open_position(contract, side, price, contracts=1):
    """Open a futures position (LONG or SHORT)."""
    account = load_scalping_account()
    
    if account['position']:
        print("❌ Already have an open position. Close it first.")
        return
    
    # Futures margin requirement (roughly 10% for ES, NQ)
    margin_per_contract = price * 0.1
    total_margin = margin_per_contract * contracts
    
    if total_margin > account['cash']:
        print(f"❌ Insufficient margin. Need ${total_margin:.2f}, have ${account['cash']:.2f}")
        return
    
    account['position'] = {
        'contract': contract,
        'side': side,
        'entry_price': price,
        'contracts': contracts,
        'entry_time': datetime.now().isoformat(),
        'margin': total_margin
    }
    
    account['cash'] -= total_margin
    save_scalping_account(account)
    
    print(f"\n✅ OPENED {side} POSITION")
    print(f"   Contract: {contract}")
    print(f"   Contracts: {contracts}")
    print(f"   Entry: ${price:.2f}")
    print(f"   Margin: ${total_margin:.2f}")
    print(f"   Cash remaining: ${account['cash']:.2f}")

def close_position(exit_price):
    """Close the open futures position."""
    account = load_scalping_account()
    
    if not account['position']:
        print("❌ No open position to close")
        return
    
    pos = account['position']
    
    # Calculate P&L
    if pos['side'] == 'LONG':
        pnl_per_contract = (exit_price - pos['entry_price']) * 50  # ES/NQ multiplier
    else:  # SHORT
        pnl_per_contract = (pos['entry_price'] - exit_price) * 50
    
    total_pnl = pnl_per_contract * pos['contracts']
    
    # Return margin + P&L
    account['cash'] += pos['margin'] + total_pnl
    account['total_pnl'] += total_pnl
    
    # Record trade
    trade = {
        'contract': pos['contract'],
        'side': pos['side'],
        'entry_price': pos['entry_price'],
        'exit_price': exit_price,
        'contracts': pos['contracts'],
        'pnl': total_pnl,
        'entry_time': pos['entry_time'],
        'exit_time': datetime.now().isoformat()
    }
    
    account['trades'].append(trade)
    account['position'] = None
    save_scalping_account(account)
    
    print(f"\n✅ CLOSED {pos['side']} POSITION")
    print(f"   Entry: ${pos['entry_price']:.2f}")
    print(f"   Exit: ${exit_price:.2f}")
    print(f"   P&L: ${total_pnl:+.2f}")
    print(f"   Cash: ${account['cash']:.2f}")
    print(f"   Total P&L: ${account['total_pnl']:+.2f}")

def show_account():
    """Show current scalping account status."""
    account = load_scalping_account()
    
    print("\n" + "="*80)
    print("FUTURES SCALPING ACCOUNT")
    print("="*80)
    print(f"\nStarting Capital: ${account['starting_capital']:,.2f}")
    print(f"Current Cash: ${account['cash']:,.2f}")
    print(f"Total P&L: ${account['total_pnl']:+,.2f}")
    print(f"Return: {(account['total_pnl'] / account['starting_capital'] * 100):+.2f}%")
    
    if account['position']:
        pos = account['position']
        print(f"\n📊 OPEN POSITION:")
        print(f"   {pos['side']} {pos['contracts']} {pos['contract']} @ ${pos['entry_price']:.2f}")
        print(f"   Margin: ${pos['margin']:.2f}")
        print(f"   Opened: {pos['entry_time'][:19]}")
    else:
        print("\n✓ No open positions")
    
    if account['trades']:
        print(f"\n📈 TRADE HISTORY ({len(account['trades'])} trades):")
        wins = sum(1 for t in account['trades'] if t['pnl'] > 0)
        losses = sum(1 for t in account['trades'] if t['pnl'] < 0)
        win_rate = wins / len(account['trades']) * 100 if account['trades'] else 0
        
        print(f"   Wins: {wins} | Losses: {losses} | Win Rate: {win_rate:.1f}%")
        
        print("\n   Last 5 trades:")
        for trade in account['trades'][-5:]:
            pnl_str = f"${trade['pnl']:+.2f}"
            color = "✅" if trade['pnl'] > 0 else "❌"
            print(f"   {color} {trade['side']} {trade['contract']} @ ${trade['entry_price']:.2f} → ${trade['exit_price']:.2f} = {pnl_str}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        show_account()
        print("\nUsage:")
        print("  python scalping.py long ES 5850 [contracts]   # Open long position")
        print("  python scalping.py short NQ 20500 [contracts]  # Open short position")
        print("  python scalping.py close 5855                  # Close position at price")
        print("  python scalping.py show                        # Show account")
        print("\nContracts: ES (S&P 500), NQ (Nasdaq 100)")
        sys.exit(0)
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'show':
        show_account()
    elif cmd == 'long' or cmd == 'short':
        if len(sys.argv) < 4:
            print("Usage: python scalping.py long/short CONTRACT PRICE [CONTRACTS]")
            sys.exit(1)
        contract = sys.argv[2].upper()
        price = float(sys.argv[3])
        contracts = int(sys.argv[4]) if len(sys.argv) > 4 else 1
        open_position(contract, cmd.upper(), price, contracts)
    elif cmd == 'close':
        if len(sys.argv) < 3:
            print("Usage: python scalping.py close EXIT_PRICE")
            sys.exit(1)
        exit_price = float(sys.argv[2])
        close_position(exit_price)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
