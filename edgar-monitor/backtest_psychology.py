#!/usr/bin/env python3
"""
Backtest trading psychology rules on historical trades
Compare performance with vs without psychology enforcement
"""
import json
from trading_psychology import validate_trade, ConsistencyMetrics


def load_historical_trades():
    """Load all available historical trades"""
    trades = []
    
    # Load scalping trades
    try:
        with open('data/scalping_trades.json') as f:
            scalping = json.load(f)
            for t in scalping.get('trades', []):
                trades.append({
                    'symbol': t['contract'],
                    'direction': t['side'],
                    'entry_price': t['entry_price'],
                    'exit_price': t['exit_price'],
                    'shares': t['contracts'],
                    'pnl': t['pnl'],
                    'entry_signal': 'SCALP',
                    'outcome': 'WIN' if t['pnl'] > 0 else 'LOSS'
                })
    except FileNotFoundError:
        pass
    
    # Load paper trades
    try:
        with open('data/paper_trades.json') as f:
            paper = json.load(f)
            for t in paper:
                if t['action'] == 'BUY':
                    trades.append({
                        'symbol': t['ticker'],
                        'direction': 'LONG',
                        'entry_price': t['price'],
                        'shares': t['shares'],
                        'entry_signal': 'FUNDAMENTAL',
                        'outcome': 'OPEN'
                    })
    except FileNotFoundError:
        pass
    
    return trades


def add_stops_to_trades(trades):
    """Add realistic stop losses to historical trades"""
    for t in trades:
        if 'stop_loss' not in t:
            # Use 2% stop for longs, 2% stop for shorts
            if t['direction'] == 'LONG':
                t['stop_loss'] = t['entry_price'] * 0.98
            else:
                t['stop_loss'] = t['entry_price'] * 1.02
    return trades


def backtest_with_psychology(trades, starting_balance=10000):
    """
    Replay trades through psychology validation
    Track what would have been filtered out
    """
    balance = starting_balance
    accepted_trades = []
    rejected_trades = []
    recent_trades = []
    
    for trade in trades:
        # Add stop loss if missing
        if 'stop_loss' not in trade:
            if trade['direction'] == 'LONG':
                trade['stop_loss'] = trade['entry_price'] * 0.98
            else:
                trade['stop_loss'] = trade['entry_price'] * 1.02
        
        # Validate with psychology
        can_trade, psych_data = validate_trade(trade, balance, recent_trades)
        
        if can_trade:
            accepted_trades.append({
                **trade,
                'psychology': psych_data
            })
            
            # Update balance
            if 'pnl' in trade:
                balance += trade['pnl']
            
            # Add to recent trades for next validation
            recent_trades.append({
                'entry_time': len(recent_trades) * 3600,  # Mock timestamps
                'exit_time': len(recent_trades) * 3600 + 1800,
                'outcome': trade.get('outcome', 'OPEN'),
                'exit_reason': 'TARGET' if trade.get('pnl', 0) > 0 else 'STOP',
                'position_value': trade['shares'] * trade['entry_price'],
                'followed_plan': True,
                'stop_honored': True
            })
        else:
            rejected_trades.append({
                **trade,
                'rejection_reason': psych_data.get('reason'),
                'violations': psych_data.get('violations', [])
            })
    
    return {
        'accepted': accepted_trades,
        'rejected': rejected_trades,
        'final_balance': balance,
        'starting_balance': starting_balance
    }


def backtest_without_psychology(trades, starting_balance=10000):
    """Baseline: all trades executed"""
    balance = starting_balance
    
    for trade in trades:
        if 'pnl' in trade:
            balance += trade['pnl']
    
    return {
        'final_balance': balance,
        'starting_balance': starting_balance,
        'total_trades': len(trades)
    }


def compare_results(with_psych, without_psych):
    """Compare performance metrics"""
    
    # Calculate returns
    with_return = ((with_psych['final_balance'] - with_psych['starting_balance']) / 
                   with_psych['starting_balance'] * 100)
    without_return = ((without_psych['final_balance'] - without_psych['starting_balance']) / 
                      without_psych['starting_balance'] * 100)
    
    # Calculate metrics
    accepted_count = len(with_psych['accepted'])
    rejected_count = len(with_psych['rejected'])
    total_count = accepted_count + rejected_count
    
    acceptance_rate = (accepted_count / total_count * 100) if total_count > 0 else 0
    
    # Analyze rejected trades
    rejected_pnl = sum(t.get('pnl', 0) for t in with_psych['rejected'])
    
    return {
        'with_psychology': {
            'final_balance': with_psych['final_balance'],
            'return_pct': with_return,
            'trades_executed': accepted_count,
            'trades_rejected': rejected_count,
            'acceptance_rate': acceptance_rate
        },
        'without_psychology': {
            'final_balance': without_psych['final_balance'],
            'return_pct': without_return,
            'trades_executed': total_count
        },
        'impact': {
            'return_difference': with_return - without_return,
            'balance_difference': with_psych['final_balance'] - without_psych['final_balance'],
            'rejected_pnl': rejected_pnl,
            'trades_filtered': rejected_count
        }
    }


def print_report(comparison, with_psych):
    """Print backtest report"""
    print("=" * 70)
    print("TRADING PSYCHOLOGY BACKTEST REPORT")
    print("=" * 70)
    print()
    
    print("WITHOUT PSYCHOLOGY (Baseline):")
    print(f"  Final Balance: ${comparison['without_psychology']['final_balance']:,.2f}")
    print(f"  Return: {comparison['without_psychology']['return_pct']:+.2f}%")
    print(f"  Trades: {comparison['without_psychology']['trades_executed']}")
    print()
    
    print("WITH PSYCHOLOGY (Enforced Rules):")
    print(f"  Final Balance: ${comparison['with_psychology']['final_balance']:,.2f}")
    print(f"  Return: {comparison['with_psychology']['return_pct']:+.2f}%")
    print(f"  Trades Executed: {comparison['with_psychology']['trades_executed']}")
    print(f"  Trades Rejected: {comparison['with_psychology']['trades_rejected']}")
    print(f"  Acceptance Rate: {comparison['with_psychology']['acceptance_rate']:.1f}%")
    print()
    
    print("IMPACT:")
    print(f"  Return Difference: {comparison['impact']['return_difference']:+.2f}%")
    print(f"  Balance Difference: ${comparison['impact']['balance_difference']:+,.2f}")
    print(f"  Rejected P&L: ${comparison['impact']['rejected_pnl']:+,.2f}")
    print(f"  Trades Filtered: {comparison['impact']['trades_filtered']}")
    print()
    
    # Rejection reasons
    if with_psych['rejected']:
        print("REJECTION REASONS:")
        reasons = {}
        for t in with_psych['rejected']:
            reason = t['rejection_reason']
            reasons[reason] = reasons.get(reason, 0) + 1
        
        for reason, count in sorted(reasons.items(), key=lambda x: x[1], reverse=True):
            print(f"  {reason}: {count}x")
        print()
    
    # Sample rejected trades
    if with_psych['rejected']:
        print("SAMPLE REJECTED TRADES:")
        for t in with_psych['rejected'][:5]:
            symbol = t['symbol']
            reason = t['rejection_reason']
            pnl = t.get('pnl', 0)
            print(f"  {symbol} - {reason} - Would have been: ${pnl:+.2f}")
        print()
    
    print("INTERPRETATION:")
    if comparison['impact']['return_difference'] > 0:
        print("  ✓ Psychology rules IMPROVED returns")
        print("  ✓ Filtered out net-negative trades")
    elif comparison['impact']['return_difference'] < -5:
        print("  ✗ Psychology rules TOO STRICT")
        print("  ✗ Filtered out profitable trades")
        print("  → Consider loosening risk limits")
    else:
        print("  ~ Psychology rules had minimal impact on returns")
        print("  ~ But likely reduced risk and drawdowns")
    
    print()
    print("=" * 70)


if __name__ == '__main__':
    print("Loading historical trades...")
    trades = load_historical_trades()
    
    if not trades:
        print("No historical trades found!")
        print("Need data in:")
        print("  - data/scalping_trades.json")
        print("  - data/paper_trades.json")
        exit(1)
    
    print(f"Found {len(trades)} historical trades")
    print()
    
    # Add stops to trades that don't have them
    trades = add_stops_to_trades(trades)
    
    # Run backtests
    print("Running backtest WITHOUT psychology rules...")
    without_psych = backtest_without_psychology(trades)
    
    print("Running backtest WITH psychology rules...")
    with_psych = backtest_with_psychology(trades)
    
    # Compare
    comparison = compare_results(with_psych, without_psych)
    
    # Print report
    print()
    print_report(comparison, with_psych)
    
    # Save results
    with open('data/backtest_results.json', 'w') as f:
        json.dump({
            'comparison': comparison,
            'accepted_trades': with_psych['accepted'],
            'rejected_trades': with_psych['rejected']
        }, f, indent=2)
    
    print("💾 Saved detailed results to data/backtest_results.json")
