#!/usr/bin/env python3
"""
Chart Trainer — Learn to read charts through annotated reps.

Modes:
  python chart_trainer.py learn        # Annotated chart walkthrough
  python chart_trainer.py quiz         # Predict what happens next
  python chart_trainer.py progress     # Track your accuracy

Same philosophy as sports-monitor basketball IQ trainer:
  Show pattern → annotate → quiz → track improvement.
"""

import json
import random
import sys
from datetime import datetime
from pathlib import Path

import yfinance as yf

DATA_DIR = Path(__file__).parent / "data"
PROGRESS_PATH = DATA_DIR / "chart_progress.json"


# ── Core chart analysis ──────────────────────────────────────────────

def get_candles(symbol="ES=F", period="5d", interval="15m"):
    """Fetch candle data."""
    df = yf.download(symbol, period=period, interval=interval, progress=False)
    candles = []
    for idx, row in df.iterrows():
        candles.append({
            "time": idx.strftime("%m/%d %H:%M"),
            "open": float(row[("Open", symbol)]),
            "high": float(row[("High", symbol)]),
            "low": float(row[("Low", symbol)]),
            "close": float(row[("Close", symbol)]),
            "volume": int(row[("Volume", symbol)]),
        })
    return candles


def find_pivots(candles, lookback=3):
    """Find swing highs and swing lows."""
    pivots = []
    for i in range(lookback, len(candles) - lookback):
        high = candles[i]["high"]
        low = candles[i]["low"]

        is_swing_high = all(high >= candles[i + j]["high"] for j in range(-lookback, lookback + 1) if j != 0)
        is_swing_low = all(low <= candles[i + j]["low"] for j in range(-lookback, lookback + 1) if j != 0)

        if is_swing_high:
            pivots.append({"type": "HIGH", "price": high, "index": i, "time": candles[i]["time"]})
        if is_swing_low:
            pivots.append({"type": "LOW", "price": low, "index": i, "time": candles[i]["time"]})
    return pivots


def detect_trend(pivots):
    """Determine trend from pivot sequence."""
    highs = [p for p in pivots if p["type"] == "HIGH"]
    lows = [p for p in pivots if p["type"] == "LOW"]

    if len(highs) >= 2 and len(lows) >= 2:
        higher_highs = highs[-1]["price"] > highs[-2]["price"]
        higher_lows = lows[-1]["price"] > lows[-2]["price"]
        lower_highs = highs[-1]["price"] < highs[-2]["price"]
        lower_lows = lows[-1]["price"] < lows[-2]["price"]

        if higher_highs and higher_lows:
            return "UPTREND"
        elif lower_highs and lower_lows:
            return "DOWNTREND"
    return "RANGE"


def find_support_resistance(pivots):
    """Find key S/R levels from pivot clusters.

    Clusters all pivots within a tolerance, ranks by touch count,
    then classifies as support (mostly lows) or resistance (mostly highs).
    Returns (support_list, resistance_list) where each item is:
      {"price": float, "touches": int, "times": [str, ...]}
    """
    if not pivots:
        return [], []

    prices = sorted(pivots, key=lambda p: p["price"])
    price_range = prices[-1]["price"] - prices[0]["price"]
    tolerance = max(3, price_range * 0.01)

    clusters = []
    used = set()
    for i, p in enumerate(prices):
        if i in used:
            continue
        cluster = [p]
        used.add(i)
        for j, q in enumerate(prices):
            if j not in used and abs(q["price"] - p["price"]) < tolerance:
                cluster.append(q)
                used.add(j)
        avg_price = round(sum(c["price"] for c in cluster) / len(cluster), 2)
        lows = sum(1 for c in cluster if c["type"] == "LOW")
        highs = sum(1 for c in cluster if c["type"] == "HIGH")
        clusters.append({
            "price": avg_price,
            "touches": len(cluster),
            "type": "support" if lows >= highs else "resistance",
            "times": [c["time"] for c in cluster],
        })

    clusters.sort(key=lambda c: -c["touches"])
    top = clusters[:4]

    support = sorted([c for c in top if c["type"] == "support"], key=lambda c: c["price"])
    resistance = sorted([c for c in top if c["type"] == "resistance"], key=lambda c: c["price"])

    return support[:2], resistance[:2]


def find_patterns(candles):
    """Detect common chart patterns in recent candles."""
    patterns = []
    if len(candles) < 10:
        return patterns

    recent = candles[-10:]

    # Double bottom: two lows at similar level with a high between
    lows = [(i, c["low"]) for i, c in enumerate(recent)]
    lows_sorted = sorted(lows, key=lambda x: x[1])
    if len(lows_sorted) >= 2:
        l1, l2 = lows_sorted[0], lows_sorted[1]
        if abs(l1[1] - l2[1]) < 2 and abs(l1[0] - l2[0]) >= 3:
            patterns.append({"name": "DOUBLE_BOTTOM", "level": round((l1[1] + l2[1]) / 2, 2),
                             "meaning": "Buyers defending this level twice → potential reversal up"})

    # Double top
    highs = [(i, c["high"]) for i, c in enumerate(recent)]
    highs_sorted = sorted(highs, key=lambda x: -x[1])
    if len(highs_sorted) >= 2:
        h1, h2 = highs_sorted[0], highs_sorted[1]
        if abs(h1[1] - h2[1]) < 2 and abs(h1[0] - h2[0]) >= 3:
            patterns.append({"name": "DOUBLE_TOP", "level": round((h1[1] + h2[1]) / 2, 2),
                             "meaning": "Sellers rejecting this level twice → potential reversal down"})

    # Inside bar: bar completely within prior bar's range
    for i in range(1, len(recent)):
        if recent[i]["high"] < recent[i-1]["high"] and recent[i]["low"] > recent[i-1]["low"]:
            patterns.append({"name": "INSIDE_BAR", "time": recent[i]["time"],
                             "meaning": "Compression → expect expansion (breakout in either direction)"})
            break  # just report most recent

    # Doji: open ≈ close with wicks
    last = recent[-1]
    body = abs(last["close"] - last["open"])
    wick = last["high"] - last["low"]
    if wick > 0 and body / wick < 0.15:
        patterns.append({"name": "DOJI", "time": last["time"],
                         "meaning": "Indecision — neither buyers nor sellers won this bar"})

    return patterns


def render_mini_chart(candles, width=60):
    """ASCII mini-chart of recent price action."""
    if not candles:
        return ""
    prices = [c["close"] for c in candles]
    hi, lo = max(prices), min(prices)
    rng = hi - lo or 1
    height = 15

    rows = [["  "] * width for _ in range(height)]
    for i, p in enumerate(prices[-width:]):
        y = int((p - lo) / rng * (height - 1))
        y = max(0, min(height - 1, y))
        rows[height - 1 - y][i] = "██"

    lines = []
    for r, row in enumerate(rows):
        price_label = f"{lo + (height - 1 - r) / (height - 1) * rng:8.2f} │"
        lines.append(price_label + "".join(row))

    lines.append(" " * 9 + "└" + "─" * (width * 2))
    return "\n".join(lines)


# ── Lesson content ───────────────────────────────────────────────────

CONCEPTS = [
    {
        "name": "Candlestick Basics",
        "lesson": """A candlestick shows 4 prices for one time period:
  OPEN  — where price started
  HIGH  — highest price reached
  LOW   — lowest price reached
  CLOSE — where price ended

If CLOSE > OPEN → bullish (green/white) — buyers won
If CLOSE < OPEN → bearish (red/black) — sellers won

The body = distance between open and close (the thick part)
The wicks = distance from body to high/low (the thin lines)

Long wick = price went there but got rejected
Small body = indecision
Big body = conviction""",
    },
    {
        "name": "Support & Resistance",
        "lesson": """SUPPORT = price level where buyers step in (floor)
RESISTANCE = price level where sellers step in (ceiling)

How to spot them:
  - Look for prices that bounce off the same level 2+ times
  - The more touches, the stronger the level
  - Round numbers often act as S/R (5800, 5750, etc.)

Key insight: S/R FLIP
  - When support breaks, it becomes resistance
  - When resistance breaks, it becomes support
  - This is the single most useful concept in charting""",
    },
    {
        "name": "Trend Structure",
        "lesson": """UPTREND = series of Higher Highs + Higher Lows
DOWNTREND = series of Lower Highs + Lower Lows
RANGE = highs and lows at similar levels

How to identify:
  1. Find swing highs (peaks) and swing lows (valleys)
  2. Connect the lows → that's your trendline
  3. If each low is higher than the last → uptrend

The trend is your friend:
  - In uptrend → look for LONG entries on pullbacks to trendline
  - In downtrend → look for SHORT entries on rallies to trendline
  - In range → fade the extremes (buy low, sell high)

Trend BREAKS when:
  - Price makes a lower low in an uptrend
  - Price makes a higher high in a downtrend""",
    },
    {
        "name": "Volume",
        "lesson": """Volume = how many contracts traded in that bar.

Volume CONFIRMS moves:
  - Price up + high volume = real buying (strong move)
  - Price up + low volume = weak rally (likely to fail)
  - Price down + high volume = real selling (strong move)
  - Price down + low volume = weak pullback (likely to bounce)

Volume DIVERGENCE:
  - Price making new highs but volume declining = warning
  - Price making new lows but volume declining = selling exhaustion

At S/R levels:
  - High volume rejection = strong level, expect bounce
  - High volume breakout = level broken, expect continuation""",
    },
    {
        "name": "Common Patterns",
        "lesson": """DOUBLE BOTTOM (W shape)
  - Price hits support, bounces, comes back, bounces again
  - Two lows at same level = buyers defending hard
  - Trade: buy on second bounce, stop below the lows

DOUBLE TOP (M shape)
  - Price hits resistance, drops, comes back, drops again
  - Two highs at same level = sellers defending hard
  - Trade: sell on second rejection, stop above the highs

INSIDE BAR
  - Bar completely within prior bar's range
  - Means: compression, coiling, about to move
  - Trade: buy break above or sell break below

DOJI
  - Open ≈ Close, with wicks both directions
  - Means: indecision, tug of war
  - After a trend move, doji = potential reversal""",
    },
]


# ── Modes ────────────────────────────────────────────────────────────

def learn_mode():
    """Walk through concepts with live chart annotations."""
    print("\n" + "=" * 60)
    print("CHART TRAINER — Learn Mode")
    print("=" * 60)

    candles = get_candles()
    pivots = find_pivots(candles)
    trend = detect_trend(pivots)
    support, resistance = find_support_resistance(pivots)
    patterns = find_patterns(candles)

    # Show chart
    print("\n📊 Current ES (S&P 500 Futures) — 15min candles:\n")
    print(render_mini_chart(candles))

    last = candles[-1]
    print(f"\n  Last: {last['close']:.2f}  |  Range: {candles[-1]['low']:.2f}-{candles[-1]['high']:.2f}")
    print(f"  Trend: {trend}")
    if support:
        print(f"  Support: {', '.join(str(s['price']) for s in support)}")
    if resistance:
        print(f"  Resistance: {', '.join(str(r['price']) for r in resistance)}")

    if patterns:
        print(f"\n  Patterns detected:")
        for p in patterns:
            print(f"    {p['name']}: {p.get('meaning', '')}")

    # Teach concepts
    for i, concept in enumerate(CONCEPTS):
        print(f"\n{'─' * 60}")
        print(f"LESSON {i + 1}: {concept['name']}")
        print(f"{'─' * 60}")
        print(concept["lesson"])
        input("\n  [Press Enter for next lesson] ")

    print("\n✅ Lessons complete. Try: python chart_trainer.py quiz")


def quiz_mode():
    """Show partial chart, ask what happens next."""
    print("\n" + "=" * 60)
    print("CHART TRAINER — Quiz Mode")
    print("=" * 60)

    candles = get_candles(period="5d")
    if len(candles) < 30:
        print("Not enough data for quiz.")
        return

    progress = load_progress()
    correct = 0
    total = 5

    for q in range(total):
        # Pick a random window, show all but last 4 bars
        start = random.randint(0, len(candles) - 25)
        visible = candles[start:start + 20]
        hidden = candles[start + 20:start + 24]

        if not hidden:
            continue

        pivots = find_pivots(visible)
        trend = detect_trend(pivots)
        support, resistance = find_support_resistance(pivots)
        patterns = find_patterns(visible)

        print(f"\n{'─' * 60}")
        print(f"QUESTION {q + 1}/{total}")
        print(f"{'─' * 60}")
        print(render_mini_chart(visible, width=40))

        last_price = visible[-1]["close"]
        print(f"\n  Last price: {last_price:.2f}")
        print(f"  Trend: {trend}")
        if support:
            print(f"  Support: {support[-1]['price']:.2f}")
        if resistance:
            print(f"  Resistance: {resistance[-1]['price']:.2f}")
        if patterns:
            print(f"  Pattern: {patterns[-1]['name']}")

        # What actually happened
        future_close = hidden[-1]["close"]
        actual = "UP" if future_close > last_price else "DOWN"
        move = future_close - last_price

        print(f"\n  In the next hour, price will go:")
        print(f"    1) UP")
        print(f"    2) DOWN")

        answer = input(f"\n  Your prediction (1/2): ").strip()
        predicted = "UP" if answer == "1" else "DOWN"

        if predicted == actual:
            correct += 1
            print(f"  ✅ Correct! Price went {actual} ({move:+.2f} pts)")
        else:
            print(f"  ❌ Wrong. Price went {actual} ({move:+.2f} pts)")

        # Explain why
        if trend == "UPTREND" and actual == "UP":
            print(f"  📖 Trend continuation — in an uptrend, the default is UP")
        elif trend == "DOWNTREND" and actual == "DOWN":
            print(f"  📖 Trend continuation — in a downtrend, the default is DOWN")
        elif patterns and patterns[-1]["name"] == "DOUBLE_BOTTOM" and actual == "UP":
            print(f"  📖 Double bottom reversal — buyers defended support")
        elif patterns and patterns[-1]["name"] == "DOJI":
            print(f"  📖 Doji = indecision. Could go either way. Don't beat yourself up.")
        else:
            print(f"  📖 Markets are uncertain. The goal isn't 100% — it's >50% with good risk management.")

    pct = (correct / total) * 100
    print(f"\n{'=' * 60}")
    print(f"SCORE: {correct}/{total} ({pct:.0f}%)")
    print(f"{'=' * 60}")

    if pct >= 80:
        print("🔥 Strong read. You're seeing the patterns.")
    elif pct >= 60:
        print("👍 Decent. Keep doing reps.")
    else:
        print("📚 Review the lessons. Focus on trend + S/R.")

    # Save progress
    progress["sessions"].append({
        "timestamp": datetime.now().isoformat(),
        "correct": correct,
        "total": total,
        "accuracy": pct,
    })
    save_progress(progress)


def show_progress():
    """Show accuracy over time."""
    progress = load_progress()
    sessions = progress["sessions"]

    if not sessions:
        print("No quiz sessions yet. Run: python chart_trainer.py quiz")
        return

    print(f"\n{'=' * 60}")
    print("CHART TRAINING PROGRESS")
    print(f"{'=' * 60}")

    total_correct = sum(s["correct"] for s in sessions)
    total_qs = sum(s["total"] for s in sessions)
    overall = (total_correct / total_qs * 100) if total_qs else 0

    print(f"\nSessions: {len(sessions)}")
    print(f"Overall: {total_correct}/{total_qs} ({overall:.0f}%)")

    # Last 5 sessions
    print(f"\nRecent sessions:")
    for s in sessions[-5:]:
        dt = s["timestamp"][:16]
        print(f"  {dt}  {s['correct']}/{s['total']} ({s['accuracy']:.0f}%)")

    # Trend
    if len(sessions) >= 3:
        recent = sessions[-3:]
        early = sessions[:3]
        recent_avg = sum(s["accuracy"] for s in recent) / len(recent)
        early_avg = sum(s["accuracy"] for s in early) / len(early)
        delta = recent_avg - early_avg
        if delta > 5:
            print(f"\n📈 Improving: +{delta:.0f}% from first sessions")
        elif delta < -5:
            print(f"\n📉 Declining: {delta:.0f}% from first sessions")
        else:
            print(f"\n➡️  Steady")


def load_progress():
    if PROGRESS_PATH.exists():
        return json.loads(PROGRESS_PATH.read_text())
    return {"sessions": []}


def save_progress(progress):
    DATA_DIR.mkdir(exist_ok=True)
    PROGRESS_PATH.write_text(json.dumps(progress, indent=2))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "learn"

    if cmd == "learn":
        learn_mode()
    elif cmd == "quiz":
        quiz_mode()
    elif cmd == "progress":
        show_progress()
    else:
        print("Usage: python chart_trainer.py [learn|quiz|progress]")
