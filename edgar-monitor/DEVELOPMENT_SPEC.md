# ENIS Development Spec — What to Build Next
**Date:** 2026-03-13 23:33 ET
**Status:** Spec only. No implementation yet.

---

## 1. Wire Psychology into Autonomous Loop

**Problem:** `autonomous.py` calls Jarvis and saves signals but never calls `validate_trade()`. Trades execute without risk acceptance, rule adherence, or tilt checks.

**Survey link:** #20 (can't act on feelings), #29 (executing unplanned trades)

**Spec:**
- Import `validate_trade` and `TradeJournal` into `autonomous.py`
- Before any trade signal is saved or executed, run `validate_trade(trade_plan, balance, recent_trades)`
- If rejected, log rejection reason to journal and `autonomous_log.txt`
- If TILT state detected, halt all trading for the session
- Log every decision (trade or no-trade) with full psychology context

**Files:** `autonomous.py`

---

## 2. Exit Management System

**Problem:** No systematic exit logic. No trailing stops, no target management, no partial profit-taking.

**Survey link:** #21 (not taking profits), #15 (no profit-taking philosophy)

**Spec:**
- `exit_manager.py` — standalone module
- Three exit modes:
  - **Hard stop:** honor the stop, no exceptions
  - **Trailing stop:** move stop to breakeven after 1R, trail at 1.5R
  - **Scaled exit:** take 1/3 at 1R, 1/3 at 2R, let 1/3 run with trail
- Integrate with `paper_trading.py` — auto-check open positions against exit rules
- Config in `config/exits.json`: default mode, R-multiple targets, trail distance

**Files:** `exit_manager.py`, `config/exits.json`

---

## 3. ProbabilityFramework Implementation

**Problem:** Spec exists in `TRADING_PSYCHOLOGY_SPEC.md` but class was never built. System outputs binary signals, not probability distributions.

**Survey link:** #23 (euphoria-based anticipation instead of neutral expectation)

**Spec:**
- Add `ProbabilityFramework` class to `trading_psychology.py`
- `evaluate_setup(pattern, context)` returns:
  - `win_probability` (0.0–1.0, clamped to 0.45–0.65 realistic range)
  - `edge` (probability minus 0.50)
  - `sample_size` (how many historical instances)
  - `recommendation` (TRADE if >0.55, PASS otherwise)
- Base probabilities from backtest data in `data/backtest_results.json`
- Context adjustments: trend alignment, volume confirmation, support/resistance, news risk
- Wire into `autonomous.py` — reject signals below `min_win_probability` from config

**Files:** `trading_psychology.py`

---

## 4. Psychology Dashboard Panel

**Problem:** `dashboard.py` and `dashboard_live.py` show market data but no psychology state. Can't see tilt, violations, or consistency score.

**Survey link:** #17 (victim mentality), #14 (emotional baggage) — visibility prevents denial

**Spec:**
- Add psychology section to `templates/dashboard.html`:
  - Emotional state indicator (CLEAR / CAUTION / TILT) with color coding
  - Today's consistency score and grade (A–F)
  - Rule adherence percentage
  - Recent violations list
  - Trade count vs. daily limit
- Backend: add `/api/psychology` endpoint to `dashboard.py` returning current state
- Data source: read from `TradeJournal` and run `ConsistencyMetrics` on today's trades

**Files:** `dashboard.py`, `templates/dashboard.html`

---

## 5. Journal Feedback Loop

**Problem:** `TradeJournal` logs trades but nothing reads the journal to improve decisions. No learning mechanism.

**Survey link:** #12 (haphazard start), #8 (belief that knowledge = easier execution — needs to become knowledge = better *process*)

**Spec:**
- `journal_analyzer.py` — reads `data/trade_journal.jsonl`
- Weekly analysis:
  - Most common violations (what rules keep getting broken?)
  - Consistency score trend (improving or degrading?)
  - Win rate by adherence score (do disciplined trades win more?)
  - Time-of-day patterns (when do violations cluster?)
  - Emotional state correlation (do CAUTION trades lose more?)
- Output: `data/journal_analysis.json` + markdown summary
- Feed findings back into `config/psychology.json` adjustments (manual review, not auto)

**Files:** `journal_analyzer.py`

---

## 6. EOD / Weekend Position Management

**Problem:** No automated position management at end of day or before weekends. Spec mentions "no weekend holds" but nothing enforces it.

**Spec:**
- `eod_manager.py` — run via cron at 3:30 PM ET on Fridays, 3:55 PM ET daily
- Friday: warn on all open positions, optionally auto-close
- Daily: generate EOD summary — open positions, unrealized P&L, psychology score for the day
- Cron entries:
  - `55 15 * * 1-5` — daily EOD summary
  - `30 15 * * 5` — Friday position warning
- Output: `data/eod_summary_YYYYMMDD.md`

**Files:** `eod_manager.py`

---

## Priority Order

| # | Item | Effort | Impact | Survey Gaps Addressed |
|---|------|--------|--------|----------------------|
| 1 | Wire psychology into autonomous.py | Small | High | #20, #29 |
| 2 | Exit management | Medium | High | #15, #21 |
| 3 | ProbabilityFramework | Medium | High | #23 |
| 4 | Psychology dashboard panel | Medium | Medium | #14, #17 |
| 5 | Journal feedback loop | Medium | Medium | #8, #12 |
| 6 | EOD/weekend management | Small | Medium | — |

---

## Design Principles

- Process over outcomes. Score adherence, not P&L.
- Neutral expectation. No euphoria, no dread. Just probability.
- Enforce boredom. The system should be boring to run. That's the point (#30).
- Every trade logged. Every rejection logged. No gaps.
- Config-driven. All thresholds in `config/`. No magic numbers in code.
