# Jarvis Prompt — MES Futures Trading System & Mindset

## Prompt

I'm building a systematic MES (Micro E-mini S&P 500) futures trading system based on Mark Douglas's principles from "Trading in the Zone." I need a comprehensive framework that covers both the psychological and mechanical aspects. Here's my context:

**The instrument:**
- MES (/MESM6) — $5 per point, currently trading ~6735
- Market is in a high-volatility regime: 80-100 point daily ranges, VIX ~26, S&P down ~20% from January highs
- 230K+ contracts/day volume — extremely liquid, 1-tick spreads

**The system (zone_trader.py):**
- Identifies supply/demand zones on the chart
- Enters when price reaches a zone
- Uses fixed stop losses and scaled profit targets (3 targets at 1:1, 2:1, 3:1)
- Maximum daily loss cap and maximum trades per day
- Pre-trade health check (heartbeat) verifies platform connectivity before any trade

**The problem:**
- Current config uses 5-point stops in an 80-point range — that's noise, not signal
- Need to calibrate stops to actual volatility while maintaining the same dollar risk per trade
- Wider stops (15-20 pts) with fewer contracts (1 instead of 3) = same $75 risk but room to breathe

**Mark Douglas's 7 principles (embedded in the system):**
1. Anything can happen
2. You don't need to know what happens next to make money
3. There is a random distribution between wins and losses for any given set of variables that define an edge
4. An edge is nothing more than an indication of a higher probability of one thing happening over another
5. Every moment in the market is unique
6. The market can do anything at any time
7. You never violate these rules

**What I need from each model:**

1. **Stop calibration methodology**: How should stops be sized relative to current volatility? What's the relationship between ATR (Average True Range), stop distance, and position size? Give me a concrete formula I can implement.

2. **Zone identification in high-volatility regimes**: Do supply/demand zones behave differently when VIX is elevated? Should zone width expand with volatility? How do you filter zones that are likely to hold vs. ones that will get blown through?

3. **The psychology of execution**: How do you actually maintain discipline through a drawdown sequence? Douglas says to think in probabilities over 20+ trades — but what specific mental frameworks or pre-trade routines help a trader stick to the system when they're 0-for-5?

4. **Risk of ruin calculation**: Given a $5,000 starting balance, $75 risk per trade, 5 trades/day max, and $250 daily loss cap — what win rate do I need to survive 100 trading days? What's the probability of ruin at various win rates (40%, 50%, 60%)?

5. **What most systematic traders get wrong**: What are the top 3-5 mistakes that cause mechanical trading systems to fail, even when the edge is real? How do you prevent each one?

Be specific. Use numbers. I'm implementing this in code, not reading a textbook.
