# Trading Psychology Module - "Trading in the Zone" Implementation

## Core Principle
Enforce Mark Douglas's psychological framework in autonomous trading system. Focus on process over outcomes, probability thinking, and emotional discipline.

## Module: `trading_psychology.py`

### 1. Pre-Trade Risk Acceptance

Before any trade entry, system must explicitly "accept" the risk.

```python
class RiskAcceptance:
    def can_accept_risk(self, trade_plan):
        """
        Returns True only if:
        - Max loss is defined
        - Max loss <= account risk limit (e.g., 2% of capital)
        - Stop loss price is calculated
        - Position size fits the risk
        """
        max_loss = trade_plan.entry_price - trade_plan.stop_loss
        position_value = trade_plan.shares * trade_plan.entry_price
        loss_amount = max_loss * trade_plan.shares
        
        # Can we afford to lose this?
        if loss_amount > self.max_risk_per_trade:
            return False, "Risk exceeds limit"
        
        # Is stop loss reasonable? (not too tight, not too wide)
        stop_distance_pct = (max_loss / trade_plan.entry_price) * 100
        if stop_distance_pct < 1 or stop_distance_pct > 5:
            return False, f"Stop distance {stop_distance_pct:.1f}% outside range"
        
        return True, "Risk accepted"
```

### 2. Rule Adherence Tracking

Track whether system follows its own rules, independent of P&L.

```python
class RuleAdherence:
    """
    Tracks: Did we follow the plan?
    Not: Did we make money?
    """
    
    rules = {
        'entry_signal_present': 'Entry only on confirmed pattern',
        'stop_loss_set': 'Stop loss set before entry',
        'position_size_correct': 'Position sized to risk limit',
        'no_revenge_trading': 'No entry within 30min of stop-out',
        'max_daily_trades': 'No more than 5 trades per day',
        'no_weekend_holds': 'Close all positions before Friday 3:30pm',
    }
    
    def check_trade(self, trade):
        """
        Returns adherence score (0-100)
        Logs which rules were broken
        """
        score = 0
        violations = []
        
        for rule_id, rule_desc in self.rules.items():
            if self._check_rule(rule_id, trade):
                score += 1
            else:
                violations.append(rule_desc)
        
        adherence_pct = (score / len(self.rules)) * 100
        
        return {
            'adherence_score': adherence_pct,
            'violations': violations,
            'followed_plan': adherence_pct == 100
        }
```

### 3. Probability Thinking

Output confidence intervals, not predictions.

```python
class ProbabilityFramework:
    """
    Every signal has a probability distribution
    No certainties, only edges
    """
    
    def evaluate_setup(self, pattern, context):
        """
        Returns probability distribution, not binary signal
        """
        # Historical win rate for this pattern
        base_probability = self._get_historical_winrate(pattern)
        
        # Adjust for context
        adjustments = {
            'trend_aligned': +0.15,
            'volume_confirmation': +0.10,
            'support_nearby': +0.08,
            'news_risk': -0.20,
            'choppy_market': -0.12,
        }
        
        adjusted_prob = base_probability
        for factor, adjustment in adjustments.items():
            if context.get(factor):
                adjusted_prob += adjustment
        
        # Clamp to realistic range
        adjusted_prob = max(0.45, min(0.65, adjusted_prob))
        
        return {
            'win_probability': adjusted_prob,
            'edge': adjusted_prob - 0.50,  # Edge over coin flip
            'confidence_level': self._calculate_confidence(pattern, context),
            'sample_size': self._get_sample_size(pattern),
            'recommendation': 'TRADE' if adjusted_prob > 0.55 else 'PASS'
        }
```

### 4. Emotional State Monitor

Detect when system is in "tilt" state (revenge trading, overtrading).

```python
class EmotionalStateMonitor:
    """
    Detects patterns that indicate emotional trading
    Even in autonomous systems, bugs can create "emotional" behavior
    """
    
    def check_state(self, recent_trades):
        """
        Returns: 'CLEAR', 'CAUTION', 'TILT'
        """
        warnings = []
        
        # Revenge trading: Quick re-entry after loss
        if self._detect_revenge_pattern(recent_trades):
            warnings.append('Revenge trading detected')
        
        # Overtrading: Too many trades in short period
        if self._detect_overtrading(recent_trades):
            warnings.append('Overtrading detected')
        
        # Increasing position sizes after losses
        if self._detect_martingale(recent_trades):
            warnings.append('Martingale behavior detected')
        
        # Holding losers too long
        if self._detect_hope_trading(recent_trades):
            warnings.append('Hope trading detected')
        
        if len(warnings) >= 3:
            return 'TILT', warnings
        elif len(warnings) >= 1:
            return 'CAUTION', warnings
        else:
            return 'CLEAR', []
    
    def _detect_revenge_pattern(self, trades):
        """Entry within 30min of stop-out"""
        for i in range(len(trades) - 1):
            if trades[i].outcome == 'LOSS' and trades[i].exit_reason == 'STOP':
                time_to_next = trades[i+1].entry_time - trades[i].exit_time
                if time_to_next < 1800:  # 30 minutes
                    return True
        return False
```

### 5. Consistency Metrics

Separate from P&L - measures process quality.

```python
class ConsistencyMetrics:
    """
    Mark Douglas: "Consistency comes from following your rules"
    Track process, not outcomes
    """
    
    def calculate_consistency_score(self, trades, timeframe='daily'):
        """
        Returns 0-100 score based on:
        - Rule adherence rate
        - Position sizing consistency
        - Stop loss discipline
        - Entry signal quality
        """
        
        metrics = {
            'rule_adherence': self._calc_adherence_rate(trades),
            'position_sizing': self._calc_sizing_consistency(trades),
            'stop_discipline': self._calc_stop_discipline(trades),
            'signal_quality': self._calc_signal_quality(trades),
        }
        
        # Weighted average
        weights = {
            'rule_adherence': 0.40,
            'position_sizing': 0.20,
            'stop_discipline': 0.30,
            'signal_quality': 0.10,
        }
        
        score = sum(metrics[k] * weights[k] for k in metrics)
        
        return {
            'consistency_score': score,
            'breakdown': metrics,
            'grade': self._assign_grade(score)
        }
    
    def _calc_stop_discipline(self, trades):
        """
        Did we honor our stops?
        100 = every stop executed as planned
        0 = moved stops, held losers
        """
        honored = sum(1 for t in trades if t.stop_honored)
        return (honored / len(trades)) * 100 if trades else 0
```

### 6. Trade Journal Integration

Auto-generate journal entries with psychological notes.

```python
class TradeJournal:
    """
    Automatic journaling with focus on psychology
    """
    
    def log_trade(self, trade, psychology_data):
        """
        Logs trade with psychological context
        """
        entry = {
            'timestamp': trade.entry_time,
            'symbol': trade.symbol,
            'direction': trade.direction,
            'entry_price': trade.entry_price,
            'stop_loss': trade.stop_loss,
            'target': trade.target,
            
            # Psychology data
            'risk_accepted': psychology_data['risk_accepted'],
            'rule_adherence': psychology_data['adherence_score'],
            'violations': psychology_data['violations'],
            'emotional_state': psychology_data['emotional_state'],
            'win_probability': psychology_data['win_probability'],
            
            # Post-trade
            'outcome': trade.outcome,
            'pnl': trade.pnl,
            'followed_plan': psychology_data['followed_plan'],
            
            # Notes
            'what_went_right': self._analyze_success(trade),
            'what_went_wrong': self._analyze_failure(trade),
            'lessons': self._extract_lessons(trade),
        }
        
        self._save_entry(entry)
        return entry
```

## Integration with Existing System

### autonomous.py
```python
from trading_psychology import RiskAcceptance, RuleAdherence, EmotionalStateMonitor

# Before entering trade
risk_check = RiskAcceptance()
can_trade, reason = risk_check.can_accept_risk(trade_plan)
if not can_trade:
    log.info(f"Trade rejected: {reason}")
    return

# Check emotional state
emotion_monitor = EmotionalStateMonitor()
state, warnings = emotion_monitor.check_state(recent_trades)
if state == 'TILT':
    log.warning(f"System in TILT state: {warnings}")
    return  # Stop trading

# Execute trade
execute_trade(trade_plan)

# Log adherence
adherence = RuleAdherence()
score = adherence.check_trade(trade_plan)
log.info(f"Rule adherence: {score['adherence_score']}%")
```

### dashboard.py
Add psychology panel:
- Current emotional state (CLEAR/CAUTION/TILT)
- Today's consistency score
- Rule adherence rate
- Recent violations

### Daily Report
```
=== Trading Psychology Report ===
Consistency Score: 87/100 (B+)
Rule Adherence: 95%
Emotional State: CLEAR
Trades Following Plan: 8/10

Violations Today:
- Position size 2.3% (limit: 2.0%) on AAPL trade
- Entry without volume confirmation on TSLA

Strengths:
- Perfect stop discipline (10/10)
- No revenge trading
- Probability thinking maintained
```

## Configuration

```python
# config/psychology.json
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

## Metrics to Track

### Daily
- Consistency score
- Rule adherence rate
- Emotional state
- Trades following plan vs. not

### Weekly
- Average consistency score
- Most common violations
- Improvement trends
- Process vs. outcome correlation

### Monthly
- Consistency score trend
- Rule adherence improvement
- Psychological patterns identified
- System "discipline" rating

## Success Criteria

**NOT:** "Did we make money today?"
**YES:** "Did we follow our rules today?"

A day with 3 losing trades that followed the plan = SUCCESS
A day with 3 winning trades that broke rules = FAILURE

Over time, consistency + edge = profitability

## Implementation Priority

1. **RiskAcceptance** - Critical, prevents catastrophic losses
2. **RuleAdherence** - Core tracking mechanism
3. **EmotionalStateMonitor** - Prevents runaway behavior
4. **ConsistencyMetrics** - Long-term improvement tracking
5. **ProbabilityFramework** - Better decision quality
6. **TradeJournal** - Learning and refinement

## Files to Create

```
edgar-monitor/
├── trading_psychology.py          # Main module
├── config/psychology.json         # Configuration
├── test_trading_psychology.py     # Unit tests
└── psychology_report.py           # Daily report generator
```

## Next Steps

1. Implement RiskAcceptance class
2. Add pre-trade checks to autonomous.py
3. Create psychology dashboard panel
4. Backtest with psychology rules enforced
5. Compare results: with vs. without psychology module
