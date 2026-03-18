# MES Fundamentals — What You're Actually Trading

## The Instrument

**MES** = **M**icro **E**-mini **S**&P 500

- A futures contract that derives its value from the S&P 500 index
- The S&P 500 is a weighted average of 500 large US stocks — you can't buy it directly
- Futures (and ETFs like SPY) are how you trade it

### The Sizing Chain

Same underlying, different dollar exposure per point:

| Contract | Symbol | Multiplier | 1 point = |
|---|---|---|---|
| Full S&P 500 | /SP | $250 | $250 |
| E-mini S&P 500 | /ES | $50 | $50 |
| Micro E-mini S&P 500 | /MES | $5 | $5 |

- **E-mini** = "electronic mini" — 1/5th of the full contract, first to trade on screens instead of the pit
- **Micro** = 1/10th of the E-mini, 1/50th of the full contract. Launched 2019 for smaller accounts.

### Symbol Breakdown

`/MESM6` means:
- `/` — futures namespace (TastyTrade/thinkorswim convention)
- `MES` — Micro E-mini S&P
- `M` — June (month code)
- `6` — 2026

### Futures Month Codes

```
F = Jan    G = Feb    H = Mar
J = Apr    K = May    M = Jun
N = Jul    Q = Aug    U = Sep
V = Oct    X = Nov    Z = Dec
```

Letters like I, O, P, R, S, T, W, Y are skipped to avoid confusion (I/1, O/0, etc.).

Equity index futures (ES, MES) only list quarterly months: **H M U Z** (Mar, Jun, Sep, Dec).

The front-month contract is where all the liquidity sits. In March 2026, that's the June (M) contract.

## Key Numbers (as of March 16, 2026)

From live REST API query:

| Field | Value | Meaning |
|---|---|---|
| bid / ask | 6735.25 / 6735.50 | 1-tick spread = very liquid |
| bid_size / ask_size | 10 / 13 | Contracts on each side of the book |
| open | 6661.25 | Sunday 6 PM ET open |
| prev_close | 6685.75 | Friday settlement |
| day_high | 6740.75 | Session high |
| day_low | 6658.00 | Session low |
| volume | 230,710 | Contracts traded (before 8 AM!) |
| high_limit / low_limit | 7149.75 / 6221.25 | Exchange circuit breakers (~±7%) |

### What This Tells You

- **1-tick spread**: Market is liquid, healthy, tradeable
- **82-point intraday range**: At $5/pt, that's $410/contract from low to high
- **230K volume before 8 AM**: Massive participation — fear drives volume
- **Circuit breakers at ±7%**: Exchange expects big moves

## Volatility Context

- S&P 500 topped at 7097 (Jan 28, 2026), now ~6735 — down ~5% from top, was down 20% at the lows
- Daily ranges: 80-100 points (vs 20-30 in calm markets)
- Implied volatility: ~0.257 (roughly VIX 26)

### VIX — The Fear Gauge

Calculated from S&P 500 option prices. Represents expected volatility over 30 days.

- Under 15 = calm, complacent
- 15-20 = normal
- 20-30 = nervous, elevated
- 30+ = panic (COVID hit 82)

VIX of 26 ≈ ±1.6% daily moves expected ≈ ±108 points on MES.

Not a direction prediction — just magnitude. High VIX = expensive options = people buying protection = fear.

## Why This Matters for the System

The zone_trader.py config has 5-point stops. In an 80-point range, that's noise. The market will stop you out repeatedly before your thesis even has a chance to play out.

**The fix**: Wider stops (15-20 pts), fewer contracts (1 instead of 3), same dollar risk per trade.

- 3 contracts × 5pt stop × $5 = $75 risk per trade
- 1 contract × 15pt stop × $5 = $75 risk per trade

Same risk, but the trade has room to breathe.

## TastyTrade / thinkorswim

Same founders. Tom Sosnoff and Scott Sheridan built thinkorswim, sold to TD Ameritrade (2009), then started tastytrade. TD Ameritrade was later acquired by Schwab. That's why both platforms use the `/` prefix for futures symbols.

## Data Access (Current State)

| What | Status |
|---|---|
| REST API (accounts, instruments, market data) | ✅ Works |
| `/market-data/by-type` (live quotes) | ✅ Works — bid/ask/last/volume/OHLC |
| `/market-metrics` (IV, greeks) | ✅ Works |
| DXLinkStreamer (real-time websocket) | ❌ Blocked — account needs funding |
| Trading | ❌ Blocked — futures not approved, account unfunded |

---

*Last updated: March 16, 2026*
