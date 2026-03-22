# Cross-System Integrity & Signal Bridge

## Origin

Kennesaw State game-fixing case (DOJ Eastern District PA, Jan 2026):
- 26 charged, 39+ players, 17+ D-I programs
- Point-shaving during 2023-24 season, bribes $10K-$30K
- KSU's leading scorer (Simeon Cottle) suspended; former player (Demond Robinson) also charged
- Both Kennesaw St. (14 seed) and Queens (15 seed) are in our 2026 bracket (West region)

This revealed that our three systems — sports-monitor, march-madness-2026, edgar-monitor — are taps on the same pipeline:

```
Game state → Betting handle → Company revenue → Stock price → SEC filing
     ↑              ↑              ↑                ↑            ↑
 sports-monitor  (implied)    edgar-monitor     edgar-monitor  edgar-monitor
 march-madness
```

## New Modules

### 1. `shared/signal_bridge.py`
Translates live sports events into market signals.

**Inputs:** excitement_engine game events
**Outputs:** ticker watchlists with urgency levels

Signal types:
- `VOLUME_SPIKE` — high-excitement NCAA game → betting company volume
- `UPSET_RISK` — close game late → betting company volatility
- `OVERTIME_PREMIUM` — OT → media + betting revenue upside
- `INTEGRITY_SCANDAL` — DOJ/NCAA action → betting company downside, data company upside
- `MEDIA_DEAL_RISK` — widespread sanctions → conference media deal risk

Ticker universe:
- Betting: DKNG, FLUT, MGM, CZR, PENN, RSI
- Data/integrity: GENI, SRAD
- Media: DIS, WBD, PARA, FOX, CMCSA

### 2. `march-madness-2026/integrity_flags.py`
Flags tournament teams under federal investigation.

**Inputs:** team name from bracket_data.py
**Outputs:** stat reliability score (0.0–1.0), investigation details

Integrated into:
- `bracket_simulator.py` — regresses tainted team AdjEM toward mean
- `run.py` — integrity check runs as first step in pipeline
- `upset_detector.py` — available for future matchup_flags integration

### 3. `edgar-monitor/integrity_filter.py`
Defensive layer for futures trading when market conditions look abnormal.

**Inputs:** current + previous session quotes, stop price
**Outputs:** risk adjustment factor (1.0 = normal, <1.0 = reduce exposure), flags

Detectors:
- `halftime_divergence()` — session opens hard one way, fully reverses (KSU pattern)
- `volume_at_stops()` — unusual volume near stop levels (stop hunt)
- `correlation_break()` — ES/NQ decorrelation (one being pushed artificially)

Integrated into:
- `zone_trader.py` — step 1c in the 7-principle entry gate

## Integration Points

### sports-monitor/excitement_engine.py
- CLI output now emits market signals via signal_bridge when games are live
- `get_excitement_rankings()` return format unchanged (backward compatible)

### march-madness-2026/run.py
- New `--step integrity` option
- `--step all` now runs integrity check first, before fetch
- Pipeline: integrity → fetch → analyze → simulate → picks → injuries

### march-madness-2026/bracket_simulator.py
- `_sim_round()` now applies `stat_reliability()` to AdjEM before win_prob calc
- Teams under investigation get their efficiency regressed toward 0 (average)
- KSU at 0.6 reliability: their AdjEM is multiplied by 0.6 in simulations

### edgar-monitor/zone_trader.py
- New step 1c (Integrity) between Probability (1b) and Risk (2)
- Loads prev_quotes.json and futures_snapshot.json
- Runs `assess_session()` — logs flags but does not block trades (advisory only)
- Future: could reduce contract size when adjustment < 1.0

## Data Flow

```
excitement_engine.py
  → get_excitement_rankings()
  → signal_bridge.sports_event_to_market_signal()
  → market signals (tickers + urgency)

bracket_simulator.py
  → _sim_round()
  → integrity_flags.stat_reliability()
  → adjusted win probabilities

zone_trader.py
  → open_trade()
  → integrity_filter.assess_session()
  → flags + adjustment factor (advisory)
```

## What This Does NOT Do

- Does not try to detect manipulation in real-time (that's SEC/DOJ's job)
- Does not auto-trade on sports signals (observation/logging only)
- Does not block zone_trader entries on integrity flags (advisory only)
- Does not scrape DOJ press releases (INVESTIGATED_TEAMS is manually updated)

## Maintenance

- Update `integrity_flags.INVESTIGATED_TEAMS` when DOJ/NCAA announces new cases
- Update `signal_bridge.SPORTS_BETTING_TICKERS` if new companies go public or get acquired
- Integrity filter thresholds (halftime_divergence=2.5, volume_at_stops=0.3, correlation_break=0.4) should be tuned against historical data

## The Thesis

Manipulation exists in every market where money is at stake. The defense isn't detection — it's survival:
1. Predefine risk (zone_trader: $75/trade)
2. Think in samples (no single trade matters)
3. Step aside when conditions are abnormal (integrity_filter)
4. Trade small (1 MES contract)
5. Accept the tax (some losses are manufactured — build it into expected win rate)

The edge isn't avoiding manipulation. It's watching the full pipeline when everyone else only watches one tap.
