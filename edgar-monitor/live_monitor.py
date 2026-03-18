#!/usr/bin/env python3
"""
Live Futures Monitor — watches MES, detects setups, gates through psychology.

Usage:
  python live_monitor.py              # Single scan
  python live_monitor.py --watch      # Continuous (30s interval)
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

from heartbeat import get_session, check_quotes, check_health
from trading_psychology import ProbabilityFramework, EmotionalStateMonitor, TradeJournal
from zone_trader import load_config, load_state, reset_daily

DATA_DIR = Path(__file__).parent / "data"


def detect_signal(quotes, prev_quotes=None):
    """
    Simple signal detection from quote data.
    Returns (signal_type, context_dict) or (None, {}).
    """
    if not quotes.get("bid"):
        return None, {}

    last = quotes["last"]
    day_high = quotes.get("day_high", last)
    day_low = quotes.get("day_low", last)
    open_price = quotes.get("open", last)
    prev_close = quotes.get("prev_close", last)

    day_range = day_high - day_low if day_high and day_low else 0
    from_open = last - open_price if open_price else 0
    from_high = day_high - last if day_high else 0
    from_low = last - day_low if day_low else 0

    context = {
        "trend_aligned": from_open > 0 and last > prev_close,  # up trend
        "volume_confirmed": (quotes.get("volume", 0) or 0) > 5000,
        "at_support_resistance": from_low < 2 or from_high < 2,
        "news_risk": False,
    }

    # Pullback in uptrend: price pulled back from high but still above open
    if from_open > 3 and from_high > 3 and from_high < day_range * 0.4:
        return "pullback", context

    # Breakout: new day high
    if from_high <= 0.5 and day_range > 5:
        return "breakout", context

    # Range fade: at extreme of range, mean reversion
    if day_range > 8 and (from_high < 1.5 or from_low < 1.5):
        return "range_fade", context

    # Reversal: dropped below open, now recovering
    if from_open < -3 and prev_quotes and last > prev_quotes.get("last", last):
        return "reversal", context

    return None, context


async def scan_once(session):
    """Single scan: get quotes, detect signal, evaluate probability."""
    config = load_config()
    state = load_state()
    state = reset_daily(state)

    # Get live quotes
    quotes = await check_quotes(session)
    if quotes.get("status") != "CONNECTED":
        print(f"  ⚠️  Quotes: {quotes.get('status', 'UNKNOWN')} — {quotes.get('error', '')}")
        return quotes

    last = quotes["last"]
    bid = quotes["bid"]
    ask = quotes["ask"]
    spread = quotes.get("spread", 0)
    vol = quotes.get("volume", 0)
    day_high = quotes.get("day_high", 0)
    day_low = quotes.get("day_low", 0)
    open_price = quotes.get("open", 0)

    now = datetime.now().strftime("%H:%M:%S")
    from_open = last - open_price if open_price else 0

    print(f"[{now}] MES {last:.2f}  ({from_open:+.2f} from open)  "
          f"range={day_low:.2f}-{day_high:.2f}  vol={vol:,.0f}  spread={spread}")

    # Check open position
    if state.get("position"):
        pos = state["position"]
        side = pos["side"]
        entry = pos["entry_price"]
        pnl_pts = (last - entry) if side == "LONG" else (entry - last)
        pnl_usd = pnl_pts * pos["point_value"] * pos["remaining"]
        print(f"  📊 OPEN: {side} @ {entry:.2f}  P&L: {pnl_pts:+.1f}pts (${pnl_usd:+.2f})  "
              f"stop={pos['stop_price']:.2f}  targets_hit={pos['targets_hit']}")
        return quotes

    # Detect signal
    prev_file = DATA_DIR / "prev_quotes.json"
    prev_quotes = json.loads(prev_file.read_text()) if prev_file.exists() else None

    signal, context = detect_signal(quotes, prev_quotes)

    # Save for next comparison
    DATA_DIR.mkdir(exist_ok=True)
    prev_file.write_text(json.dumps(quotes, default=str))

    if not signal:
        print(f"  — No signal")
        return quotes

    # Probability check
    pf = ProbabilityFramework()
    prob = pf.evaluate_setup(signal, context)

    ctx_flags = [k for k, v in context.items() if v]
    print(f"  🔍 Signal: {signal}  prob={prob['win_probability']:.3f}  "
          f"edge={prob['edge']:+.3f}  ctx={ctx_flags}")

    if prob["recommendation"] == "PASS":
        print(f"  ❌ PASS — below threshold")
        return quotes

    # Emotional state check
    journal = TradeJournal()
    recent = journal.get_recent_trades()
    emo_state, warnings = EmotionalStateMonitor().check_state(recent)

    if emo_state == "TILT":
        print(f"  🛑 TILT — {warnings}")
        return quotes

    # Daily limit
    if len(state["today_trades"]) >= config["max_daily_trades"]:
        print(f"  ⛔ Daily limit reached ({config['max_daily_trades']})")
        return quotes

    # Signal passed all gates
    direction = "LONG" if signal in ("breakout", "pullback") else "SHORT"
    if signal == "range_fade":
        direction = "SHORT" if (last - day_low) > (day_high - last) else "LONG"

    print(f"  ✅ SIGNAL READY: {direction} {config['instrument']} @ {last:.2f} on {signal}")
    print(f"     Emotional state: {emo_state}  |  Trades today: {len(state['today_trades'])}/{config['max_daily_trades']}")

    if config.get("auto_execute"):
        print(f"  🚀 AUTO-EXECUTING...")
        from zone_trader import open_trade
        open_trade(direction, last, signal)
    else:
        print(f"  ⏸️  Auto-execute OFF. Run manually:")
        print(f"     python zone_trader.py {direction.lower()} {last:.2f} {signal}")

    return quotes


async def main():
    session = get_session()
    watch = "--watch" in sys.argv

    print("=" * 60)
    print(f"LIVE FUTURES MONITOR — {load_config()['instrument']}")
    print(f"Mode: {'Continuous (30s)' if watch else 'Single scan'}")
    print(f"Auto-execute: {load_config().get('auto_execute', False)}")
    print("=" * 60)

    if watch:
        while True:
            try:
                await scan_once(session)
            except Exception as e:
                print(f"  ❌ Error: {e}")
            await asyncio.sleep(30)
    else:
        await scan_once(session)


if __name__ == "__main__":
    asyncio.run(main())
