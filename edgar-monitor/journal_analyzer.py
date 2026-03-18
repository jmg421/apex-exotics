"""
Journal Analyzer — reads trade journal, finds patterns in behavior.

Outputs: data/journal_analysis.json + markdown summary.
Run weekly or on-demand.
"""

import json
from collections import Counter
from datetime import datetime
from pathlib import Path

JOURNAL_PATH = Path(__file__).parent / "data" / "trade_journal.jsonl"
OUTPUT_JSON = Path(__file__).parent / "data" / "journal_analysis.json"
OUTPUT_MD = Path(__file__).parent / "data" / "journal_analysis.md"


def load_journal():
    if not JOURNAL_PATH.exists():
        return []
    trades = []
    for line in JOURNAL_PATH.read_text().splitlines():
        if line.strip():
            trades.append(json.loads(line))
    return trades


def analyze(trades):
    if not trades:
        return {"error": "No trades in journal"}

    # Most common violations
    all_violations = []
    for t in trades:
        all_violations.extend(t.get("violations", []))
    violation_counts = Counter(all_violations).most_common(10)

    # Win rate by adherence
    adhered = [t for t in trades if t.get("followed_plan")]
    deviated = [t for t in trades if not t.get("followed_plan")]
    def win_rate(group):
        wins = [t for t in group if t.get("outcome") == "WIN"]
        return round(len(wins) / len(group) * 100, 1) if group else 0

    # Time-of-day patterns
    hour_violations = Counter()
    for t in trades:
        if t.get("violations") and t.get("timestamp"):
            try:
                h = datetime.fromisoformat(t["timestamp"]).hour
                hour_violations[h] += len(t["violations"])
            except (ValueError, TypeError):
                pass

    # Emotional state correlation
    state_outcomes = {}
    for t in trades:
        state = t.get("emotional_state", "UNKNOWN")
        outcome = t.get("outcome")
        if outcome:
            state_outcomes.setdefault(state, []).append(outcome)

    state_win_rates = {}
    for state, outcomes in state_outcomes.items():
        wins = sum(1 for o in outcomes if o == "WIN")
        state_win_rates[state] = round(wins / len(outcomes) * 100, 1) if outcomes else 0

    return {
        "total_trades": len(trades),
        "top_violations": violation_counts,
        "win_rate_adhered": win_rate(adhered),
        "win_rate_deviated": win_rate(deviated),
        "adhered_count": len(adhered),
        "deviated_count": len(deviated),
        "violation_hours": dict(hour_violations.most_common()),
        "state_win_rates": state_win_rates,
        "generated_at": datetime.now().isoformat(),
    }


def to_markdown(analysis):
    lines = [
        f"# Journal Analysis — {analysis['generated_at'][:10]}",
        f"\nTotal trades: {analysis['total_trades']}",
        f"\n## Win Rate: Discipline vs Deviation",
        f"- Followed plan ({analysis['adhered_count']} trades): **{analysis['win_rate_adhered']}%**",
        f"- Deviated ({analysis['deviated_count']} trades): **{analysis['win_rate_deviated']}%**",
        f"\n## Top Violations",
    ]
    for v, count in analysis["top_violations"]:
        lines.append(f"- {v}: {count}x")

    if analysis["violation_hours"]:
        lines.append("\n## Violation Hours (ET)")
        for hour, count in sorted(analysis["violation_hours"].items()):
            lines.append(f"- {hour}:00 — {count} violations")

    if analysis["state_win_rates"]:
        lines.append("\n## Win Rate by Emotional State")
        for state, wr in analysis["state_win_rates"].items():
            lines.append(f"- {state}: {wr}%")

    return "\n".join(lines)


if __name__ == "__main__":
    trades = load_journal()
    analysis = analyze(trades)

    OUTPUT_JSON.write_text(json.dumps(analysis, indent=2))
    md = to_markdown(analysis)
    OUTPUT_MD.write_text(md)

    print(md)
    print(f"\n💾 Saved to {OUTPUT_JSON} and {OUTPUT_MD}")
