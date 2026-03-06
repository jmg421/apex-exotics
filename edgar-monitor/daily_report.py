"""Daily report generator: summarizes trading activity."""
import json
from datetime import date, datetime, timedelta
from risk_manager import RiskManager

def generate_daily_report():
    """Generate daily trading report."""
    rm = RiskManager()
    today = date.today()
    
    # Get today's trades
    today_str = today.isoformat()
    today_entries = [t for t in rm.trades if t.get('entry_date', '').startswith(today_str)]
    today_exits = [t for t in rm.trades if t.get('exit_date', '').startswith(today_str)]
    
    # Calculate stats
    stats = rm.get_stats()
    daily_pnl = rm.get_daily_pnl()
    
    # Open positions
    open_positions = [t for t in rm.trades if t['status'] == 'open']
    
    # Generate report
    report = f"""
# Daily Trading Report - {today.strftime('%B %d, %Y')}

## Summary
- **Signals Found:** {len(today_entries)} actionable
- **Orders Placed:** {len(today_entries)}
- **Positions Closed:** {len(today_exits)}
- **Open Positions:** {len(open_positions)}
- **Daily P&L:** ${daily_pnl:.2f}

## Overall Statistics
- **Total Trades:** {stats['total_trades']}
- **Total P&L:** ${stats['total_pnl']:.2f}
- **Win Rate:** {stats['win_rate']:.1%}
- **Average Win:** ${stats.get('avg_win', 0):.2f}
- **Average Loss:** ${stats.get('avg_loss', 0):.2f}
- **Largest Win:** ${stats.get('largest_win', 0):.2f}
- **Largest Loss:** ${stats.get('largest_loss', 0):.2f}

## Today's Entries
"""
    
    if today_entries:
        for trade in today_entries:
            report += f"\n### {trade['symbol']}\n"
            report += f"- Entry: ${trade['entry_price']:.2f}\n"
            report += f"- Quantity: {trade['quantity']}\n"
            report += f"- Stop: ${trade['entry_price'] - trade['stop_loss']:.2f}\n"
            report += f"- Targets: {trade['targets']}\n"
            report += f"- Order ID: {trade['order_id']}\n"
    else:
        report += "\nNo entries today.\n"
    
    report += "\n## Today's Exits\n"
    
    if today_exits:
        for trade in today_exits:
            pnl = trade.get('pnl', 0)
            report += f"\n### {trade['symbol']}\n"
            report += f"- Entry: ${trade['entry_price']:.2f}\n"
            report += f"- Exit: ${trade.get('exit_price', 0):.2f}\n"
            report += f"- P&L: ${pnl:.2f} ({'+' if pnl > 0 else ''}{(pnl / (trade['entry_price'] * trade['quantity'])) * 100:.1f}%)\n"
    else:
        report += "\nNo exits today.\n"
    
    report += "\n## Open Positions\n"
    
    if open_positions:
        for trade in open_positions:
            report += f"\n### {trade['symbol']}\n"
            report += f"- Entry: ${trade['entry_price']:.2f} ({trade['entry_date'][:10]})\n"
            report += f"- Quantity: {trade['quantity']}\n"
            report += f"- Stop: ${trade['entry_price'] - trade['stop_loss']:.2f}\n"
    else:
        report += "\nNo open positions.\n"
    
    report += "\n---\n"
    report += f"*Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    
    return report

def save_report():
    """Generate and save daily report."""
    report = generate_daily_report()
    filename = f"data/trading_report_{date.today().isoformat()}.md"
    
    with open(filename, 'w') as f:
        f.write(report)
    
    print(f"📊 Report saved to {filename}")
    print(report)
    
    return filename

if __name__ == "__main__":
    save_report()
