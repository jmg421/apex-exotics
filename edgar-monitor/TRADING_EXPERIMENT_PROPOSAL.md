# Active Trading Experiment — Technical Summary & Capital Request

**Date:** March 15, 2026
**Author:** System documentation for family financial review
**Status:** Paper trading complete, requesting capital allocation for live pilot

---

## Executive Summary

I've built and tested an automated trading system over the past two weeks that enforces
strict risk management rules on every trade. The system trades a single futures instrument
(Micro E-mini S&P 500) with fixed position sizes and predefined maximum losses. Before
committing real capital, I'm requesting a review of the approach, the risk parameters, and
the capital requirements.

**Capital requested:** $5,000
**Maximum possible loss per trade:** $75
**Maximum possible loss per day:** $250
**Maximum possible loss before system review:** $750 (10-trade losing streak)
**Instrument:** MES (Micro E-mini S&P 500 futures, CME Group)

---

## What Was Built

### 1. EDGAR Network Intelligence System (ENIS)

A screening system that analyzes SEC filings (10-K annual reports) for micro-cap companies.
This is the research layer — it identifies potential investment opportunities by:

- Parsing public SEC EDGAR filings automatically
- Filtering for micro-cap companies (under $100M market cap)
- Extracting financial metrics from standardized XBRL data
- Scoring companies on profitability, debt levels, cash position, and revenue
- Mapping company relationships (customers, suppliers, partners) into a network graph
- Applying patented network analysis (Moment Generating Function) to assess systemic risk

This system has been tested on live SEC data and successfully identified and scored
real companies. It runs as a batch pipeline and produces daily research digests.

### 2. Trading Execution System ("Zone Trader")

A separate system that handles trade execution with enforced psychological discipline.
This is based on Mark Douglas's "Trading in the Zone" framework, which emphasizes
process consistency over outcome prediction.

The zone trader is a single command-line gateway. Every trade must pass through it.
All other execution paths in the codebase have been disabled.

**What it enforces on every trade:**

1. **Signal required** — Cannot enter a trade without naming a specific pattern
   (breakout, pullback, reversal, or range fade). No "gut feel" trades.

2. **Fixed position size** — Always 3 Micro E-mini contracts. Never more, never less.
   No increasing size after wins. No doubling down after losses.

3. **Predefined risk** — Every trade risks exactly $75. Stop loss is set at entry
   and cannot be moved further away. The math: 3 contracts × 5 points × $5/point.

4. **Risk acceptance gate** — System calculates whether the trade fits within daily
   loss limits and account risk percentage. If it doesn't fit, the trade is rejected
   automatically. No override.

5. **Scaled profit taking** — When the trade goes in our favor, the system closes
   1 contract at +5 points ($25), 1 at +10 points ($50), and 1 at +15 points ($75).
   After the first target, the stop loss moves to breakeven (no-loss position).

6. **Emotional state monitoring** — System tracks recent trade history and detects:
   - Revenge trading (re-entering too quickly after a loss)
   - Overtrading (more than 3 trades per hour)
   - Increasing position sizes after losses (martingale behavior)
   If these patterns are detected, the system blocks further trading for the day.

7. **Daily trade limit** — Maximum 5 trades per day. After 5, the system shuts down
   regardless of P&L.

8. **Consistency scoring** — Every trade is logged with a psychological profile.
   The system scores process quality (did I follow the rules?) separately from
   outcomes (did I make money?). A losing trade that followed the rules scores
   higher than a winning trade that broke them.

---

## Risk Analysis

### Worst-Case Scenarios

| Scenario | Loss | % of $5,000 | System Response |
|----------|------|-------------|-----------------|
| Single trade stopped out | $75 | 1.5% | Normal operation |
| Maximum daily loss (3-4 stops) | $250 | 5.0% | System blocks further trading |
| Bad week (5 trading days, max loss each) | $1,250 | 25.0% | Manual review triggered |
| 10-trade losing streak | $750 | 15.0% | Statistically expected to occur |
| 20-trade losing streak | $1,500 | 30.0% | Extremely unlikely but possible |

### What Cannot Happen

- **Cannot lose more than $75 on a single trade.** Stop loss is set at entry and
  the system enforces it mechanically.
- **Cannot lose more than $250 in a single day.** Daily loss limit triggers automatic
  shutdown.
- **Cannot increase position size after losses.** Fixed at 3 contracts always.
  The martingale detector blocks increasing risk.
- **Cannot trade without a defined signal.** The system rejects trades without
  a named entry pattern.
- **Cannot trade while emotionally compromised.** Tilt detection shuts down
  the system if behavioral patterns indicate emotional trading.

### What Can Happen

- **Sustained losing period.** Even with a genuine edge, 5-10 consecutive losses
  are statistically normal. The system is sized to survive this.
- **Slippage in fast markets.** Stop losses may fill at worse prices than expected
  during high volatility. Realistic additional risk: $10-25 per trade.
- **Extended drawdown.** A 20-30% drawdown from peak is possible and would take
  weeks to recover from at this position size.

### Break-Even Math

With the 1:3 risk-reward scale-out structure:
- If all 3 targets hit: +$150 profit (2:1 reward vs $75 risk)
- If 2 targets hit, stopped at breakeven on last: +$75
- If 1 target hit, stopped at breakeven on remaining: +$25
- If stopped out: -$75

**Required win rate to break even: approximately 35-40%.** This means 6-7 out of
every 10 trades can lose and the system still makes money, provided winners hit
their targets.

---

## The Instrument: Micro E-mini S&P 500 (MES)

- **Exchange:** CME Group (Chicago Mercantile Exchange)
- **What it tracks:** S&P 500 index
- **Contract value:** $5 per index point (at S&P 5850, one contract = $29,250 notional)
- **Margin requirement:** ~$400-$1,400 per contract depending on broker and time of day
- **Trading hours:** Sunday 6 PM to Friday 5 PM ET (nearly 24 hours)
- **Liquidity:** One of the most liquid futures contracts in the world
- **Why this instrument:** Tight spreads, no slippage concern, well-understood behavior,
  small enough contract size for a $5,000 account

This is not a penny stock or cryptocurrency. The S&P 500 is the benchmark index for
the US equity market. The micro contract was specifically designed by CME for smaller
accounts.

---

## Broker: Tastytrade

- **Regulated by:** FINRA, NFC, SEC
- **Account protection:** SIPC coverage
- **Futures commission:** ~$1.25 per contract per side ($7.50 round-trip for 3 contracts)
- **Current status:** Sandbox (paper trading) account configured and tested
- **To go live:** Open funded account, update one configuration line

---

## What This Is Not

- **Not day trading stocks.** Futures have different margin rules (no PDT rule).
- **Not options trading.** Defined risk on every trade, no Greeks to manage.
- **Not algorithmic/high-frequency trading.** Trades are manually initiated based on
  chart patterns. The system enforces discipline, it doesn't generate signals.
- **Not leveraged to the hilt.** Using 3 micro contracts on a $5,000 account is
  conservative. Maximum notional exposure is ~$87,750 but actual risk per trade is $75.
- **Not a get-rich-quick scheme.** At $75 risk per trade, even excellent performance
  produces modest returns. The goal is to prove the process works before scaling.

---

## Timeline & Milestones

### Phase 1: Paper Trading Validation (Current — Complete)
- Built and tested all system components
- Executed simulated trades with full psychology enforcement
- Verified all bypass paths are blocked

### Phase 2: Sandbox Live Data (This Week)
- Trade against real MES prices in tastytrade sandbox
- No real money at risk
- Goal: 20 consecutive trades following all rules
- Success metric: Consistency score ≥ 80/100, not P&L

### Phase 3: Live Pilot (After Phase 2 Complete)
- Fund tastytrade account with $5,000
- Trade 3 MES contracts per the zone trader rules
- 30-day evaluation period
- Weekly review of consistency score and P&L

### Decision Points

- **After 20 sandbox trades:** Go/no-go on live capital based on consistency score
- **After 30 days live:** Continue, adjust, or stop based on:
  - Consistency score (target: ≥ 80/100)
  - Drawdown (stop if account drops below $3,500 / 30% loss)
  - Rule violations (stop if more than 2 violations in a week)
- **After 90 days live:** Full review — is this worth continuing at larger size?

---

## The Ask

Withdraw $5,000 from passive investment accounts to fund a tastytrade futures account
for a 90-day active trading pilot. This represents the minimum viable amount to trade
3 Micro E-mini S&P 500 contracts within the risk parameters described above.

**If the experiment fails completely** (maximum realistic loss): -$1,500 to -$2,500
over 90 days, at which point the system's drawdown limit triggers automatic shutdown.

**If the experiment succeeds:** Proof that the system and process work, with data to
support a decision about whether to continue or scale.

The $5,000 should be considered risk capital — money we can afford to lose entirely
without impacting family financial goals, emergency fund, or passive investment strategy.
