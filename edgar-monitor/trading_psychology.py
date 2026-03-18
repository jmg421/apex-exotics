"""
Trading Psychology Module
Based on Mark Douglas's "Trading in the Zone"
Enforces discipline, probability thinking, and risk acceptance
"""
import json
import time
from datetime import datetime, timedelta
from pathlib import Path


class RiskAcceptance:
    """Pre-trade risk validation - no trade without explicit acceptance"""
    
    def __init__(self, config_path='config/psychology.json'):
        self.config = self._load_config(config_path)
        self.max_risk_pct = self.config.get('max_risk_per_trade_pct', 2.0)
        self.stop_range = self.config.get('stop_distance_range', [1.0, 5.0])
    
    def _load_config(self, path):
        try:
            with open(path) as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def can_accept_risk(self, trade_plan, account_balance):
        """
        Returns (bool, str): (can_trade, reason)
        """
        # Validate required fields
        required = ['entry_price', 'stop_loss', 'shares', 'symbol']
        for field in required:
            if field not in trade_plan:
                return False, f"Missing required field: {field}"
        
        entry = trade_plan['entry_price']
        stop = trade_plan['stop_loss']
        shares = trade_plan['shares']
        symbol = trade_plan['symbol']
        
        # Use higher risk limit for futures
        max_risk = self.config.get('max_risk_futures_pct', self.max_risk_pct) \
                   if symbol in ['ES', 'NQ', 'YM', 'RTY'] else self.max_risk_pct
        
        # Calculate risk
        risk_per_share = abs(entry - stop)
        total_risk = risk_per_share * shares
        risk_pct = (total_risk / account_balance) * 100
        
        # Check risk limit
        if risk_pct > max_risk:
            return False, f"Risk {risk_pct:.2f}% exceeds limit {max_risk}%"
        
        # Check stop distance
        stop_distance_pct = (risk_per_share / entry) * 100
        if stop_distance_pct < self.stop_range[0]:
            return False, f"Stop too tight: {stop_distance_pct:.2f}%"
        if stop_distance_pct > self.stop_range[1]:
            return False, f"Stop too wide: {stop_distance_pct:.2f}%"
        
        # Risk accepted
        return True, f"Risk accepted: ${total_risk:.2f} ({risk_pct:.2f}%)"


class RuleAdherence:
    """Track whether system follows its own rules"""
    
    RULES = {
        'has_entry_signal': 'Entry signal present',
        'has_stop_loss': 'Stop loss defined',
        'position_sized': 'Position sized correctly',
        'no_revenge': 'No revenge trading',
        'within_daily_limit': 'Within daily trade limit',
    }
    
    def __init__(self, config_path='config/psychology.json'):
        self.config = self._load_config(config_path)
        self.max_daily_trades = self.config.get('max_daily_trades', 5)
        self.revenge_cooldown = self.config.get('revenge_trading_cooldown_minutes', 30)
        self.max_risk_pct = self.config.get('max_risk_per_trade_pct', 2.0)
    
    def _load_config(self, path):
        try:
            with open(path) as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def check_trade(self, trade_plan, recent_trades, account_balance):
        """
        Returns dict with adherence score and violations
        """
        violations = []
        checks = {
            'has_entry_signal': 'entry_signal' in trade_plan and trade_plan['entry_signal'],
            'has_stop_loss': 'stop_loss' in trade_plan,
            'position_sized': self._check_position_size(trade_plan, account_balance),
            'no_revenge': not self._is_revenge_trade(trade_plan, recent_trades),
            'within_daily_limit': self._check_daily_limit(recent_trades),
        }
        
        for rule_id, passed in checks.items():
            if not passed:
                violations.append(self.RULES[rule_id])
        
        passed_count = sum(1 for v in checks.values() if v)
        adherence_score = (passed_count / len(checks)) * 100
        
        return {
            'adherence_score': adherence_score,
            'violations': violations,
            'followed_plan': len(violations) == 0,
            'checks': checks
        }
    
    def _check_position_size(self, trade_plan, account_balance):
        """Position should not exceed risk limit"""
        if 'shares' not in trade_plan or 'entry_price' not in trade_plan:
            return False
        if 'stop_loss' not in trade_plan:
            return True  # Can't validate without stop
        
        # Check actual risk, not position size
        risk_per_share = abs(trade_plan['entry_price'] - trade_plan['stop_loss'])
        total_risk = risk_per_share * trade_plan['shares']
        risk_pct = (total_risk / account_balance) * 100
        
        # Use higher limit for futures
        symbol = trade_plan.get('symbol', '')
        max_risk = self.config.get('max_risk_futures_pct', self.max_risk_pct) \
                   if symbol in ['ES', 'NQ', 'YM', 'RTY'] else self.max_risk_pct
        
        return risk_pct <= max_risk
    
    def _is_revenge_trade(self, trade_plan, recent_trades):
        """Check if entering too soon after stop-out"""
        if not recent_trades:
            return False
        
        last_trade = recent_trades[-1]
        if last_trade.get('outcome') != 'LOSS' or last_trade.get('exit_reason') != 'STOP':
            return False
        
        last_exit = last_trade.get('exit_time', 0)
        now = time.time()
        minutes_since = (now - last_exit) / 60
        
        return minutes_since < self.revenge_cooldown
    
    def _check_daily_limit(self, recent_trades):
        """Check if within daily trade limit"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0).timestamp()
        today_trades = [t for t in recent_trades if t.get('entry_time', 0) >= today_start]
        return len(today_trades) < self.max_daily_trades


class EmotionalStateMonitor:
    """Detect tilt patterns in trading behavior"""
    
    def check_state(self, recent_trades):
        """
        Returns: ('CLEAR'|'CAUTION'|'TILT', [warnings])
        """
        if not recent_trades or len(recent_trades) < 2:
            return 'CLEAR', []
        
        warnings = []
        
        if self._detect_revenge_pattern(recent_trades):
            warnings.append('Revenge trading detected')
        
        if self._detect_overtrading(recent_trades):
            warnings.append('Overtrading detected')
        
        if self._detect_increasing_risk(recent_trades):
            warnings.append('Increasing position sizes after losses')
        
        if len(warnings) >= 3:
            return 'TILT', warnings
        elif len(warnings) >= 1:
            return 'CAUTION', warnings
        else:
            return 'CLEAR', []
    
    def _detect_revenge_pattern(self, trades):
        """Quick re-entry after loss"""
        for i in range(len(trades) - 1):
            if trades[i].get('outcome') == 'LOSS':
                time_diff = trades[i+1].get('entry_time', 0) - trades[i].get('exit_time', 0)
                if time_diff < 1800:  # 30 minutes
                    return True
        return False
    
    def _detect_overtrading(self, trades):
        """Too many trades in short period"""
        hour_ago = time.time() - 3600
        recent = [t for t in trades if t.get('entry_time', 0) > hour_ago]
        return len(recent) > 3
    
    def _detect_increasing_risk(self, trades):
        """Position sizes increasing after losses"""
        if len(trades) < 3:
            return False
        
        last_three = trades[-3:]
        losses = [t for t in last_three if t.get('outcome') == 'LOSS']
        
        if len(losses) >= 2:
            # Check if position sizes are increasing
            sizes = [t.get('position_value', 0) for t in last_three]
            return sizes[-1] > sizes[0] * 1.2  # 20% increase
        
        return False


class ConsistencyMetrics:
    """Measure process quality, not outcomes"""
    
    def calculate_consistency_score(self, trades):
        """
        Returns 0-100 score based on process adherence
        """
        if not trades:
            return {'consistency_score': 0, 'breakdown': {}, 'grade': 'N/A'}
        
        metrics = {
            'rule_adherence': self._calc_adherence_rate(trades),
            'stop_discipline': self._calc_stop_discipline(trades),
            'position_sizing': self._calc_sizing_consistency(trades),
        }
        
        weights = {
            'rule_adherence': 0.50,
            'stop_discipline': 0.35,
            'position_sizing': 0.15,
        }
        
        score = sum(metrics[k] * weights[k] for k in metrics)
        
        return {
            'consistency_score': round(score, 1),
            'breakdown': metrics,
            'grade': self._assign_grade(score)
        }
    
    def _calc_adherence_rate(self, trades):
        """Percentage of trades that followed all rules"""
        followed = sum(1 for t in trades if t.get('followed_plan', False))
        return (followed / len(trades)) * 100
    
    def _calc_stop_discipline(self, trades):
        """Percentage of stops honored"""
        with_stops = [t for t in trades if 'stop_honored' in t]
        if not with_stops:
            return 100
        honored = sum(1 for t in with_stops if t['stop_honored'])
        return (honored / len(with_stops)) * 100
    
    def _calc_sizing_consistency(self, trades):
        """How consistent are position sizes"""
        sizes = [t.get('position_value', 0) for t in trades if 'position_value' in t]
        if len(sizes) < 2:
            return 100
        
        avg = sum(sizes) / len(sizes)
        variance = sum((s - avg) ** 2 for s in sizes) / len(sizes)
        std_dev = variance ** 0.5
        cv = (std_dev / avg) if avg > 0 else 0  # Coefficient of variation
        
        # Lower CV = more consistent = higher score
        consistency = max(0, 100 - (cv * 100))
        return consistency
    
    def _assign_grade(self, score):
        if score >= 90: return 'A'
        if score >= 80: return 'B'
        if score >= 70: return 'C'
        if score >= 60: return 'D'
        return 'F'


class TradeJournal:
    """Automatic trade journaling with psychological context"""
    
    def __init__(self, journal_path='data/trade_journal.jsonl'):
        self.journal_path = Path(journal_path)
        self.journal_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log_trade(self, trade, psychology_data):
        """Log trade with psychological context"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'symbol': trade.get('symbol'),
            'direction': trade.get('direction'),
            'entry_price': trade.get('entry_price'),
            'stop_loss': trade.get('stop_loss'),
            'shares': trade.get('shares'),
            
            # Psychology
            'risk_accepted': psychology_data.get('risk_accepted'),
            'adherence_score': psychology_data.get('adherence_score'),
            'violations': psychology_data.get('violations', []),
            'emotional_state': psychology_data.get('emotional_state'),
            'followed_plan': psychology_data.get('followed_plan'),
            
            # Outcome (filled later)
            'outcome': trade.get('outcome'),
            'pnl': trade.get('pnl'),
            'exit_price': trade.get('exit_price'),
            'exit_reason': trade.get('exit_reason'),
        }
        
        # Append to journal
        with open(self.journal_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        return entry
    
    def get_recent_trades(self, limit=20):
        """Load recent trades from journal"""
        if not self.journal_path.exists():
            return []
        
        trades = []
        with open(self.journal_path) as f:
            for line in f:
                trades.append(json.loads(line))
        
        return trades[-limit:]


class ProbabilityFramework:
    """
    Evaluate setups as probability distributions, not binary signals.
    Douglas Ch. 8: neutral expectation, no euphoria, no dread.
    """

    # Base win rates by pattern (conservative defaults)
    DEFAULT_BASE_RATES = {
        "breakout": 0.52, "pullback": 0.55, "reversal": 0.48,
        "momentum": 0.50, "mean_reversion": 0.53, "default": 0.50,
    }

    CONTEXT_ADJUSTMENTS = {
        "trend_aligned": 0.03,
        "volume_confirmed": 0.02,
        "at_support_resistance": 0.02,
        "news_risk": -0.04,
    }

    def __init__(self, backtest_path="data/backtest_results.json", config_path="config/psychology.json"):
        self.base_rates = dict(self.DEFAULT_BASE_RATES)
        self.min_prob = 0.45
        self.max_prob = 0.65

        # Override with backtest data if available
        bt = Path(backtest_path)
        if bt.exists():
            try:
                data = json.loads(bt.read_text())
                for pattern, stats in data.items():
                    if isinstance(stats, dict) and stats.get("sample_size", 0) >= 30:
                        self.base_rates[pattern] = stats["win_rate"]
            except (json.JSONDecodeError, TypeError):
                pass

        cfg_path = Path(config_path)
        if cfg_path.exists():
            cfg = json.loads(cfg_path.read_text())
            self.min_win_prob = cfg.get("min_win_probability", 0.55)
        else:
            self.min_win_prob = 0.55

    def evaluate_setup(self, pattern, context=None):
        """
        Returns dict with win_probability, edge, sample_size, recommendation.
        context: dict of boolean flags like {"trend_aligned": True, "news_risk": True}
        """
        context = context or {}
        base = self.base_rates.get(pattern, self.base_rates["default"])

        adjustment = sum(
            self.CONTEXT_ADJUSTMENTS[k] for k, v in context.items()
            if v and k in self.CONTEXT_ADJUSTMENTS
        )

        prob = max(self.min_prob, min(self.max_prob, base + adjustment))
        edge = prob - 0.50

        return {
            "pattern": pattern,
            "win_probability": round(prob, 3),
            "edge": round(edge, 3),
            "sample_size": self._sample_size(pattern),
            "recommendation": "TRADE" if prob >= self.min_win_prob else "PASS",
        }

    def _sample_size(self, pattern):
        bt = Path("data/backtest_results.json")
        if bt.exists():
            data = json.loads(bt.read_text())
            return data.get(pattern, {}).get("sample_size", 0)
        return 0


def validate_trade(trade_plan, account_balance, recent_trades):
    """
    Main validation function - call before executing any trade
    Returns (can_trade, psychology_data)
    """
    # Risk acceptance
    risk_check = RiskAcceptance()
    can_trade, risk_msg = risk_check.can_accept_risk(trade_plan, account_balance)
    
    if not can_trade:
        return False, {'reason': risk_msg}
    
    # Rule adherence
    adherence = RuleAdherence()
    adherence_data = adherence.check_trade(trade_plan, recent_trades, account_balance)
    
    if not adherence_data['followed_plan']:
        return False, {
            'reason': 'Rule violations',
            'violations': adherence_data['violations']
        }
    
    # Emotional state
    emotion_monitor = EmotionalStateMonitor()
    state, warnings = emotion_monitor.check_state(recent_trades)
    
    if state == 'TILT':
        return False, {
            'reason': 'System in TILT state',
            'warnings': warnings
        }
    
    # All checks passed
    return True, {
        'risk_accepted': True,
        'risk_message': risk_msg,
        'adherence_score': adherence_data['adherence_score'],
        'violations': adherence_data['violations'],
        'emotional_state': state,
        'followed_plan': True
    }
