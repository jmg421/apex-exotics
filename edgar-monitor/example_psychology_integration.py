#!/usr/bin/env python3
"""
Example: Integrating trading psychology into autonomous trading
"""
from trading_psychology import validate_trade, TradeJournal


def execute_trade_with_psychology(trade_plan, account_balance=10000):
    """
    Example of how to integrate psychology module into trading system
    """
    # Load recent trades
    journal = TradeJournal()
    recent_trades = journal.get_recent_trades(limit=20)
    
    # Convert journal format to monitor format
    monitor_trades = []
    for t in recent_trades:
        from datetime import datetime
        monitor_trades.append({
            'entry_time': datetime.fromisoformat(t['timestamp']).timestamp(),
            'exit_time': datetime.fromisoformat(t['timestamp']).timestamp() + 3600,
            'outcome': t.get('outcome', 'OPEN'),
            'exit_reason': t.get('exit_reason'),
            'position_value': t.get('shares', 0) * t.get('entry_price', 0)
        })
    
    # Validate trade
    can_trade, psychology_data = validate_trade(trade_plan, account_balance, monitor_trades)
    
    if not can_trade:
        print(f"❌ Trade rejected: {psychology_data.get('reason')}")
        if 'violations' in psychology_data:
            print(f"   Violations: {psychology_data['violations']}")
        if 'warnings' in psychology_data:
            print(f"   Warnings: {psychology_data['warnings']}")
        return None
    
    # Trade approved
    print(f"✓ Trade approved: {trade_plan['symbol']}")
    print(f"  Risk: {psychology_data['risk_message']}")
    print(f"  Adherence: {psychology_data['adherence_score']}%")
    print(f"  Emotional State: {psychology_data['emotional_state']}")
    
    # Execute trade (placeholder)
    print(f"  Executing: {trade_plan['direction']} {trade_plan['shares']} shares @ ${trade_plan['entry_price']}")
    print(f"  Stop Loss: ${trade_plan['stop_loss']}")
    
    # Log to journal
    journal.log_trade(trade_plan, psychology_data)
    
    return {
        'status': 'EXECUTED',
        'psychology': psychology_data
    }


if __name__ == '__main__':
    print("=== Trading Psychology Integration Example ===\n")
    
    # Example 1: Good trade
    print("Example 1: Valid trade")
    trade1 = {
        'symbol': 'AAPL',
        'direction': 'LONG',
        'entry_price': 150.0,
        'stop_loss': 147.0,
        'shares': 30,
        'entry_signal': 'HA_DOJI_BULLISH'
    }
    execute_trade_with_psychology(trade1, account_balance=10000)
    print()
    
    # Example 2: Too much risk
    print("Example 2: Excessive risk")
    trade2 = {
        'symbol': 'TSLA',
        'direction': 'LONG',
        'entry_price': 200.0,
        'stop_loss': 195.0,
        'shares': 100,
        'entry_signal': 'BREAKOUT'
    }
    execute_trade_with_psychology(trade2, account_balance=10000)
    print()
    
    # Example 3: Missing stop loss
    print("Example 3: Missing stop loss")
    trade3 = {
        'symbol': 'NVDA',
        'direction': 'LONG',
        'entry_price': 300.0,
        'shares': 20,
        'entry_signal': 'MOMENTUM'
    }
    execute_trade_with_psychology(trade3, account_balance=10000)
    print()
