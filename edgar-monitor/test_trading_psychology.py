#!/usr/bin/env python3
"""
Test trading psychology module
"""
import time
from trading_psychology import (
    RiskAcceptance, RuleAdherence, EmotionalStateMonitor,
    ConsistencyMetrics, TradeJournal, validate_trade
)


def test_risk_acceptance():
    print("Testing RiskAcceptance...")
    risk = RiskAcceptance()
    
    # Good trade
    trade = {
        'symbol': 'AAPL',
        'entry_price': 100.0,
        'stop_loss': 98.0,
        'shares': 50
    }
    can_trade, msg = risk.can_accept_risk(trade, account_balance=10000)
    print(f"  Good trade: {can_trade} - {msg}")
    assert can_trade, "Should accept reasonable risk"
    
    # Too much risk
    trade['shares'] = 500
    can_trade, msg = risk.can_accept_risk(trade, account_balance=10000)
    print(f"  High risk: {can_trade} - {msg}")
    assert not can_trade, "Should reject excessive risk"
    
    print("  ✓ RiskAcceptance working\n")


def test_rule_adherence():
    print("Testing RuleAdherence...")
    rules = RuleAdherence()
    
    # Perfect trade
    trade = {
        'symbol': 'AAPL',
        'entry_price': 100.0,
        'stop_loss': 98.0,
        'shares': 50,
        'entry_signal': 'HA_DOJI_BULLISH'
    }
    result = rules.check_trade(trade, recent_trades=[], account_balance=10000)
    print(f"  Perfect trade: {result['adherence_score']}% - {result['violations']}")
    assert result['followed_plan'], "Should pass all rules"
    
    # Missing stop loss
    trade_bad = {
        'symbol': 'AAPL',
        'entry_price': 100.0,
        'shares': 50,
        'entry_signal': 'HA_DOJI_BULLISH'
    }
    result = rules.check_trade(trade_bad, recent_trades=[], account_balance=10000)
    print(f"  No stop loss: {result['adherence_score']}% - {result['violations']}")
    assert not result['followed_plan'], "Should fail without stop loss"
    
    print("  ✓ RuleAdherence working\n")


def test_emotional_state():
    print("Testing EmotionalStateMonitor...")
    monitor = EmotionalStateMonitor()
    
    # Clean trading
    trades = [
        {'entry_time': time.time() - 7200, 'exit_time': time.time() - 7000, 'outcome': 'WIN'},
        {'entry_time': time.time() - 3600, 'exit_time': time.time() - 3400, 'outcome': 'WIN'},
    ]
    state, warnings = monitor.check_state(trades)
    print(f"  Clean trading: {state} - {warnings}")
    assert state == 'CLEAR', "Should be clear"
    
    # Revenge trading
    trades_revenge = [
        {'entry_time': time.time() - 1000, 'exit_time': time.time() - 900, 'outcome': 'LOSS'},
        {'entry_time': time.time() - 600, 'exit_time': time.time() - 500, 'outcome': 'LOSS'},
    ]
    state, warnings = monitor.check_state(trades_revenge)
    print(f"  Revenge trading: {state} - {warnings}")
    assert state in ['CAUTION', 'TILT'], "Should detect revenge trading"
    
    print("  ✓ EmotionalStateMonitor working\n")


def test_consistency_metrics():
    print("Testing ConsistencyMetrics...")
    metrics = ConsistencyMetrics()
    
    # Consistent trading
    trades = [
        {'followed_plan': True, 'stop_honored': True, 'position_value': 1000},
        {'followed_plan': True, 'stop_honored': True, 'position_value': 1050},
        {'followed_plan': True, 'stop_honored': True, 'position_value': 980},
    ]
    result = metrics.calculate_consistency_score(trades)
    print(f"  Consistent: {result['consistency_score']} ({result['grade']})")
    print(f"    Breakdown: {result['breakdown']}")
    assert result['consistency_score'] > 80, "Should score high"
    
    # Inconsistent trading
    trades_bad = [
        {'followed_plan': False, 'stop_honored': False, 'position_value': 1000},
        {'followed_plan': True, 'stop_honored': False, 'position_value': 5000},
        {'followed_plan': False, 'stop_honored': True, 'position_value': 500},
    ]
    result = metrics.calculate_consistency_score(trades_bad)
    print(f"  Inconsistent: {result['consistency_score']} ({result['grade']})")
    assert result['consistency_score'] < 60, "Should score low"
    
    print("  ✓ ConsistencyMetrics working\n")


def test_trade_journal():
    print("Testing TradeJournal...")
    journal = TradeJournal(journal_path='data/test_journal.jsonl')
    
    trade = {
        'symbol': 'AAPL',
        'direction': 'LONG',
        'entry_price': 100.0,
        'stop_loss': 98.0,
        'shares': 50,
        'outcome': 'WIN',
        'pnl': 150.0
    }
    
    psychology_data = {
        'risk_accepted': True,
        'adherence_score': 100,
        'violations': [],
        'emotional_state': 'CLEAR',
        'followed_plan': True
    }
    
    entry = journal.log_trade(trade, psychology_data)
    print(f"  Logged: {entry['symbol']} - {entry['adherence_score']}%")
    
    recent = journal.get_recent_trades(limit=1)
    assert len(recent) == 1, "Should retrieve logged trade"
    print(f"  Retrieved: {recent[0]['symbol']}")
    
    print("  ✓ TradeJournal working\n")


def test_validate_trade():
    print("Testing validate_trade (main function)...")
    
    # Good trade
    trade = {
        'symbol': 'AAPL',
        'entry_price': 100.0,
        'stop_loss': 98.0,
        'shares': 50,
        'entry_signal': 'HA_DOJI_BULLISH'
    }
    
    can_trade, data = validate_trade(trade, account_balance=10000, recent_trades=[])
    print(f"  Valid trade: {can_trade}")
    print(f"    {data}")
    assert can_trade, "Should accept valid trade"
    
    # Excessive risk
    trade_risky = {
        'symbol': 'AAPL',
        'entry_price': 100.0,
        'stop_loss': 98.0,
        'shares': 500,
        'entry_signal': 'HA_DOJI_BULLISH'
    }
    
    can_trade, data = validate_trade(trade_risky, account_balance=10000, recent_trades=[])
    print(f"  Risky trade: {can_trade}")
    print(f"    {data}")
    assert not can_trade, "Should reject risky trade"
    
    print("  ✓ validate_trade working\n")


if __name__ == '__main__':
    print("=== Trading Psychology Module Tests ===\n")
    
    test_risk_acceptance()
    test_rule_adherence()
    test_emotional_state()
    test_consistency_metrics()
    test_trade_journal()
    test_validate_trade()
    
    print("=== All Tests Passed ✓ ===")
