#!/usr/bin/env python3
"""Automated scalping with 1:3 risk:reward ratio."""

from scalping import load_scalping_account, save_scalping_account, open_position, close_position
from datetime import datetime
import sys

# Risk per trade: $250 (5 ES points or 12.5 NQ points)
RISK_AMOUNT = 250

# Risk:Reward ratio 1:3
REWARD_RATIO = 3

def calculate_targets(contract, entry_price, side):
    """Calculate stop loss and profit target based on 1:3 ratio."""
    
    if contract == 'ES':
        # ES: $50 per point, so 5 points = $250 risk
        risk_points = RISK_AMOUNT / 50
        reward_points = risk_points * REWARD_RATIO
    elif contract == 'NQ':
        # NQ: $20 per point, so 12.5 points = $250 risk
        risk_points = RISK_AMOUNT / 20
        reward_points = risk_points * REWARD_RATIO
    else:
        raise ValueError(f"Unknown contract: {contract}")
    
    if side == 'LONG':
        stop_loss = entry_price - risk_points
        profit_target = entry_price + reward_points
    else:  # SHORT
        stop_loss = entry_price + risk_points
        profit_target = entry_price - reward_points
    
    return stop_loss, profit_target

def open_managed_position(contract, side, entry_price, contracts=1):
    """Open position with automatic stop loss and profit target."""
    # ZONE GUARD: All trades must go through zone_trader.py
    print("❌ Direct trading disabled.")
    print("   Use zone_trader.py — the single gateway for all trades.")
    print(f"   python3 zone_trader.py {side.lower()} {entry_price} <signal>")
    return None, None
    
    # Calculate targets
    stop_loss, profit_target = calculate_targets(contract, entry_price, side)
    
    print(f"\n📊 RISK MANAGEMENT:")
    print(f"   Stop Loss: ${stop_loss:.2f} (Risk: ${RISK_AMOUNT * contracts:.2f})")
    print(f"   Profit Target: ${profit_target:.2f} (Reward: ${RISK_AMOUNT * REWARD_RATIO * contracts:.2f})")
    print(f"   Risk:Reward = 1:{REWARD_RATIO}")
    
    # Save targets to account
    account = load_scalping_account()
    if account['position']:
        account['position']['stop_loss'] = stop_loss
        account['position']['profit_target'] = profit_target
        save_scalping_account(account)
    
    return stop_loss, profit_target

def check_position(current_price):
    """Check if stop loss or profit target hit."""
    account = load_scalping_account()
    
    if not account['position']:
        print("❌ No open position")
        return
    
    pos = account['position']
    
    if 'stop_loss' not in pos or 'profit_target' not in pos:
        print("⚠️  Position has no stop loss/target. Use 'trade.py' to open managed positions.")
        return
    
    print(f"\n📊 POSITION STATUS:")
    print(f"   {pos['side']} {pos['contracts']} {pos['contract']} @ ${pos['entry_price']:.2f}")
    print(f"   Current Price: ${current_price:.2f}")
    print(f"   Stop Loss: ${pos['stop_loss']:.2f}")
    print(f"   Profit Target: ${pos['profit_target']:.2f}")
    
    # Calculate current P&L
    if pos['side'] == 'LONG':
        pnl_points = current_price - pos['entry_price']
    else:
        pnl_points = pos['entry_price'] - current_price
    
    multiplier = 50 if pos['contract'] == 'ES' else 20
    current_pnl = pnl_points * multiplier * pos['contracts']
    
    print(f"   Current P&L: ${current_pnl:+.2f}")
    
    # Check if targets hit
    if pos['side'] == 'LONG':
        if current_price <= pos['stop_loss']:
            print(f"\n🛑 STOP LOSS HIT!")
            close_position(pos['stop_loss'])
            return
        elif current_price >= pos['profit_target']:
            print(f"\n🎯 PROFIT TARGET HIT!")
            close_position(pos['profit_target'])
            return
    else:  # SHORT
        if current_price >= pos['stop_loss']:
            print(f"\n🛑 STOP LOSS HIT!")
            close_position(pos['stop_loss'])
            return
        elif current_price <= pos['profit_target']:
            print(f"\n🎯 PROFIT TARGET HIT!")
            close_position(pos['profit_target'])
            return
    
    print(f"\n✓ Position still active")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("\n" + "="*80)
        print("MANAGED SCALPING - 1:3 RISK:REWARD")
        print("="*80)
        print("\nUsage:")
        print("  python trade.py long ES 5850      # Open long with auto stop/target")
        print("  python trade.py short NQ 20500    # Open short with auto stop/target")
        print("  python trade.py check 5855        # Check if stop/target hit")
        print("\nRisk Management:")
        print(f"  Risk per trade: ${RISK_AMOUNT}")
        print(f"  Reward per trade: ${RISK_AMOUNT * REWARD_RATIO}")
        print(f"  Risk:Reward ratio: 1:{REWARD_RATIO}")
        print("\nWith 50% win rate, you make money!")
        sys.exit(0)
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'check':
        if len(sys.argv) < 3:
            print("Usage: python trade.py check CURRENT_PRICE")
            sys.exit(1)
        current_price = float(sys.argv[2])
        check_position(current_price)
    
    elif cmd in ['long', 'short']:
        if len(sys.argv) < 4:
            print("Usage: python trade.py long/short CONTRACT ENTRY_PRICE [CONTRACTS]")
            sys.exit(1)
        
        contract = sys.argv[2].upper()
        entry_price = float(sys.argv[3])
        contracts = int(sys.argv[4]) if len(sys.argv) > 4 else 1
        
        open_managed_position(contract, cmd.upper(), entry_price, contracts)
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
