"""
EOD Manager — end-of-day and weekend position management.

Cron:
  55 15 * * 1-5  cd /Users/apple/apex-exotics/edgar-monitor && python3 eod_manager.py
  30 15 * * 5    cd /Users/apple/apex-exotics/edgar-monitor && python3 eod_manager.py --friday
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from paper_trading import load_portfolio, get_current_price
from trading_psychology import TradeJournal, ConsistencyMetrics

DATA_DIR = Path(__file__).parent / "data"


def eod_summary():
    """Generate end-of-day summary."""
    portfolio = load_portfolio()
    journal = TradeJournal()
    today = datetime.now().strftime("%Y-%m-%d")
    todays_trades = [t for t in journal.get_recent_trades() if t.get("timestamp", "").startswith(today)]

    # Consistency
    consistency = ConsistencyMetrics().calculate_consistency_score(todays_trades)

    # Open positions
    positions = []
    total_unrealized = 0
    for ticker, pos in portfolio.get("positions", {}).items():
        try:
            current = get_current_price(ticker)
        except Exception:
            current = pos["avg_price"]
        pnl = (current - pos["avg_price"]) * pos["shares"]
        total_unrealized += pnl
        positions.append({"ticker": ticker, "shares": pos["shares"], "pnl": round(pnl, 2)})

    summary = {
        "date": today,
        "trades_today": len(todays_trades),
        "consistency_score": consistency["consistency_score"],
        "consistency_grade": consistency["grade"],
        "open_positions": positions,
        "unrealized_pnl": round(total_unrealized, 2),
        "cash": portfolio.get("cash", 0),
    }

    # Write markdown
    md = f"# EOD Summary — {today}\n\n"
    md += f"Trades: {summary['trades_today']} | Consistency: {summary['consistency_score']} ({summary['consistency_grade']})\n"
    md += f"Unrealized P&L: ${summary['unrealized_pnl']:.2f} | Cash: ${summary['cash']:.2f}\n"

    if positions:
        md += "\n## Open Positions\n"
        for p in positions:
            md += f"- {p['ticker']}: {p['shares']} shares, P&L ${p['pnl']:.2f}\n"

    out_path = DATA_DIR / f"eod_summary_{today}.md"
    out_path.write_text(md)
    print(md)
    print(f"💾 {out_path}")
    return summary


def friday_warning():
    """Warn about open positions before weekend."""
    portfolio = load_portfolio()
    positions = portfolio.get("positions", {})

    if not positions:
        print("✅ No open positions — clean into the weekend.")
        return

    print("🚨 FRIDAY WARNING — Open positions going into weekend:")
    for ticker, pos in positions.items():
        print(f"   {ticker}: {pos['shares']} shares @ ${pos['avg_price']:.2f}")
    print("\nConsider closing before 4:00 PM ET.")


if __name__ == "__main__":
    if "--friday" in sys.argv:
        friday_warning()
    eod_summary()
