#!/usr/bin/env python3
"""
Psychology Report Generator
Daily summary of trading discipline and consistency
"""
from trading_psychology import TradeJournal, ConsistencyMetrics, EmotionalStateMonitor
from datetime import datetime, timedelta


def generate_daily_report():
    """Generate daily psychology report"""
    journal = TradeJournal()
    trades = journal.get_recent_trades(limit=100)
    
    # Filter today's trades
    today_start = datetime.now().replace(hour=0, minute=0, second=0).timestamp()
    today_trades = [t for t in trades if datetime.fromisoformat(t['timestamp']).timestamp() >= today_start]
    
    if not today_trades:
        print("No trades today")
        return
    
    # Calculate metrics
    metrics = ConsistencyMetrics()
    consistency = metrics.calculate_consistency_score(today_trades)
    
    emotion_monitor = EmotionalStateMonitor()
    # Convert to format expected by monitor
    monitor_trades = []
    for t in today_trades:
        monitor_trades.append({
            'entry_time': datetime.fromisoformat(t['timestamp']).timestamp(),
            'exit_time': datetime.fromisoformat(t['timestamp']).timestamp() + 3600,
            'outcome': t.get('outcome', 'OPEN'),
            'position_value': t.get('shares', 0) * t.get('entry_price', 0)
        })
    
    state, warnings = emotion_monitor.check_state(monitor_trades)
    
    # Calculate stats
    total_trades = len(today_trades)
    followed_plan = sum(1 for t in today_trades if t.get('followed_plan'))
    violations_list = []
    for t in today_trades:
        violations_list.extend(t.get('violations', []))
    
    # P&L (for reference, not primary metric)
    total_pnl = sum(t.get('pnl', 0) for t in today_trades if t.get('pnl'))
    
    # Print report
    print("=" * 60)
    print(f"TRADING PSYCHOLOGY REPORT - {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 60)
    print()
    
    print(f"Consistency Score: {consistency['consistency_score']}/100 ({consistency['grade']})")
    print(f"Emotional State: {state}")
    if warnings:
        print(f"Warnings: {', '.join(warnings)}")
    print()
    
    print(f"Trades Today: {total_trades}")
    print(f"Followed Plan: {followed_plan}/{total_trades} ({followed_plan/total_trades*100:.0f}%)")
    print()
    
    print("Breakdown:")
    for metric, value in consistency['breakdown'].items():
        print(f"  {metric.replace('_', ' ').title()}: {value:.1f}%")
    print()
    
    if violations_list:
        print("Violations Today:")
        violation_counts = {}
        for v in violations_list:
            violation_counts[v] = violation_counts.get(v, 0) + 1
        for violation, count in violation_counts.items():
            print(f"  - {violation} ({count}x)")
        print()
    
    print("Recent Trades:")
    for t in today_trades[-5:]:
        symbol = t.get('symbol', 'N/A')
        direction = t.get('direction', 'N/A')
        outcome = t.get('outcome', 'OPEN')
        adherence = t.get('adherence_score', 0)
        pnl = t.get('pnl') or 0
        
        status = '✓' if t.get('followed_plan') else '✗'
        print(f"  {status} {symbol} {direction} - {outcome} - Adherence: {adherence:.0f}% - P&L: ${pnl:.2f}")
    print()
    
    print(f"P&L Today: ${total_pnl:.2f} (reference only)")
    print()
    
    # Key insight
    print("Key Insight:")
    if consistency['consistency_score'] >= 80:
        print("  Excellent discipline today. Keep following the process.")
    elif consistency['consistency_score'] >= 60:
        print("  Good effort. Review violations and tighten discipline.")
    else:
        print("  Process needs work. Focus on rules, not outcomes.")
    
    print()
    print("Remember: Consistency + Edge = Profitability")
    print("=" * 60)


if __name__ == '__main__':
    generate_daily_report()
