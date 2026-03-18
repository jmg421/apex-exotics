# Trading Psychology Module

Implementation of Mark Douglas's "Trading in the Zone" principles for autonomous trading.

## Quick Start

```python
from trading_psychology import validate_trade, TradeJournal

# Before executing any trade
trade_plan = {
    'symbol': 'AAPL',
    'direction': 'LONG',
    'entry_price': 150.0,
    'stop_loss': 147.0,
    'shares': 30,
    'entry_signal': 'HA_DOJI_BULLISH'
}

# Validate with psychology checks
journal = TradeJournal()
recent_trades = journal.get_recent_trades(limit=20)

can_trade, psychology_data = validate_trade(
    trade_plan, 
    account_balance=10000, 
    recent_trades=recent_trades
)

if can_trade:
    # Execute trade
    execute(trade_plan)
    # Log to journal
    journal.log_trade(trade_plan, psychology_data)
else:
    print(f"Trade rejected: {psychology_data['reason']}")
```

## Core Modules

### 1. RiskAcceptance
Validates risk before trade entry:
- Max 2% risk per trade (configurable)
- Stop loss required
- Stop distance must be 1-5% (configurable)

### 2. RuleAdherence
Tracks process compliance:
- Entry signal present
- Stop loss defined
- Position sized correctly
- No revenge trading (30min cooldown after stop-out)
- Within daily trade limit (5 trades)

### 3. EmotionalStateMonitor
Detects tilt patterns:
- **CLEAR**: Normal trading
- **CAUTION**: 1-2 warning signs
- **TILT**: 3+ warnings, stop trading

Detects:
- Revenge trading (quick re-entry after loss)
- Overtrading (>3 trades/hour)
- Increasing position sizes after losses

### 4. ConsistencyMetrics
Scores process quality (0-100):
- Rule adherence rate (50% weight)
- Stop discipline (35% weight)
- Position sizing consistency (15% weight)

Grades: A (90+), B (80+), C (70+), D (60+), F (<60)

### 5. TradeJournal
Auto-logs trades with psychological context:
- Risk acceptance status
- Rule adherence score
- Violations
- Emotional state
- Outcome (filled post-trade)

## Daily Report

```bash
python3 psychology_report.py
```

Output:
```
============================================================
TRADING PSYCHOLOGY REPORT - 2026-03-13
============================================================

Consistency Score: 87/100 (B)
Emotional State: CLEAR

Trades Today: 8
Followed Plan: 7/8 (88%)

Breakdown:
  Rule Adherence: 87.5%
  Stop Discipline: 100.0%
  Position Sizing: 95.2%

Violations Today:
  - Position sized correctly (1x)

Recent Trades:
  ✓ AAPL LONG - WIN - Adherence: 100% - P&L: $150.00
  ✓ TSLA SHORT - LOSS - Adherence: 100% - P&L: -$80.00
  ✗ NVDA LONG - WIN - Adherence: 80% - P&L: $200.00

P&L Today: $270.00 (reference only)

Key Insight:
  Good effort. Review violations and tighten discipline.

Remember: Consistency + Edge = Profitability
============================================================
```

## Configuration

Edit `config/psychology.json`:

```json
{
  "max_risk_per_trade_pct": 2.0,
  "max_daily_trades": 5,
  "min_win_probability": 0.55,
  "stop_distance_range": [1.0, 5.0],
  "revenge_trading_cooldown_minutes": 30,
  "tilt_detection_enabled": true,
  "consistency_tracking_enabled": true
}
```

## Integration with Existing Code

### autonomous.py
```python
from trading_psychology import validate_trade, TradeJournal

def trade_decision(signal, account_balance):
    # Build trade plan
    trade_plan = {
        'symbol': signal['symbol'],
        'entry_price': signal['price'],
        'stop_loss': calculate_stop(signal),
        'shares': calculate_position_size(signal, account_balance),
        'entry_signal': signal['pattern'],
        'direction': signal['direction']
    }
    
    # Psychology validation
    journal = TradeJournal()
    recent = journal.get_recent_trades()
    
    can_trade, psych_data = validate_trade(trade_plan, account_balance, recent)
    
    if not can_trade:
        log.warning(f"Trade rejected: {psych_data['reason']}")
        return None
    
    # Execute
    result = execute_trade(trade_plan)
    
    # Log with psychology data
    trade_plan['outcome'] = result['outcome']
    trade_plan['pnl'] = result['pnl']
    journal.log_trade(trade_plan, psych_data)
    
    return result
```

### dashboard.py
Add psychology panel:
```python
from trading_psychology import ConsistencyMetrics, EmotionalStateMonitor

# In dashboard route
journal = TradeJournal()
trades = journal.get_recent_trades()

metrics = ConsistencyMetrics()
consistency = metrics.calculate_consistency_score(trades)

monitor = EmotionalStateMonitor()
state, warnings = monitor.check_state(trades)

return render_template('dashboard.html',
    consistency_score=consistency['consistency_score'],
    grade=consistency['grade'],
    emotional_state=state,
    warnings=warnings
)
```

## Testing

```bash
python3 test_trading_psychology.py
```

All tests should pass:
- RiskAcceptance validation
- RuleAdherence tracking
- EmotionalStateMonitor detection
- ConsistencyMetrics calculation
- TradeJournal logging
- validate_trade integration

## Key Principles

1. **Process over outcomes**: A losing trade that followed the plan = success
2. **Risk acceptance**: No trade without explicit risk validation
3. **Probability thinking**: Every signal has a win probability, not certainty
4. **Consistency**: Track adherence to rules, not just P&L
5. **Emotional discipline**: Detect and prevent tilt behavior

## Files

```
edgar-monitor/
├── trading_psychology.py          # Core module
├── config/psychology.json         # Configuration
├── test_trading_psychology.py     # Tests
├── psychology_report.py           # Daily report
├── example_psychology_integration.py  # Integration example
├── data/trade_journal.jsonl       # Trade log (auto-created)
└── TRADING_PSYCHOLOGY_README.md   # This file
```

## Success Metrics

**NOT measured by:**
- Daily P&L
- Win rate
- Number of winning trades

**Measured by:**
- Consistency score (target: 80+)
- Rule adherence rate (target: 95%+)
- Stop discipline (target: 100%)
- Emotional state (target: CLEAR)

Over time: **Consistency + Edge = Profitability**
