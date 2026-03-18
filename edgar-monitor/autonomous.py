#!/usr/bin/env python3
"""Autonomous Trading System - Unsupervised, no human input needed"""
import json
import sys
import time
from datetime import datetime
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.jarvis_client import jarvis_ask
from trading_psychology import validate_trade, TradeJournal


def ask_jarvis(prompt, models=["anthropic_claude"]):
    """Query Jarvis with synthesis."""
    result = jarvis_ask(prompt, models=models)
    # Return synthesis unified answer, fall back to first model response
    if result.get("synthesis"):
        return result["synthesis"].get("unified_answer", "")
    for m in result.get("models", {}).values():
        if isinstance(m, dict) and m.get("response"):
            return m["response"]
    return None

def autonomous_scan():
    """Run full autonomous scan and decision"""
    
    log = []
    
    def log_action(msg):
        timestamp = datetime.now().strftime('%H:%M:%S')
        log.append(f"[{timestamp}] {msg}")
        print(f"[{timestamp}] {msg}")
    
    log_action("🤖 AUTONOMOUS SYSTEM STARTING")
    log_action("="*60)
    
    # Step 1: Get market data
    log_action("📊 Fetching market data...")
    subprocess.run(['python3', 'market_data_yfinance.py'], 
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log_action("✅ Market data captured")
    
    # Step 2: Detect patterns
    log_action("🔍 Running pattern detection...")
    subprocess.run(['python3', 'detect_patterns.py'], 
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(['python3', 'futures_patterns.py'], 
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log_action("✅ Patterns detected")
    
    # Step 3: Load results
    with open('data/pattern_detection.json', 'r') as f:
        stock_patterns = json.load(f)
    
    with open('data/futures_analysis.json', 'r') as f:
        futures_analysis = json.load(f)
    
    # Step 4: Build autonomous decision prompt
    top_stock_anomalies = sorted(stock_patterns['anomalies'], 
                                 key=lambda x: abs(x['change_percent']), reverse=True)[:3]
    
    futures_anomalies = futures_analysis['anomalies']
    
    prompt = f"""You are an autonomous trading system. Make decisions WITHOUT human input.

CURRENT TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}

MARKET DATA:

Top Stock Anomalies:
"""
    for s in top_stock_anomalies:
        prompt += f"- {s['symbol']}: {s['change_percent']:+.2f}% | Vol: {s['volume']:,}\n"
    
    prompt += "\nFutures Anomalies:\n"
    for f in futures_anomalies:
        prompt += f"- {f['symbol']}: {f['change_percent']:+.2f}% | Price: ${f['price']:.2f}\n"
    
    prompt += """
RISK PARAMETERS:
- Max daily loss: $100
- Max positions: 3
- Capital: $2,000-5,000
- Risk per trade: $10-50

YOUR TASK:
Decide autonomously what to do RIGHT NOW. Output ONLY valid JSON:

{
  "action": "TRADE" or "WAIT" or "MONITOR",
  "symbol": "ticker symbol if trading",
  "direction": "LONG" or "SHORT" if trading,
  "entry": price level,
  "stop": stop loss,
  "target": profit target,
  "size": number of contracts/shares,
  "reasoning": "brief explanation",
  "confidence": 1-10
}

If action is WAIT or MONITOR, set symbol to null.

Rules:
- Don't chase moves >5%
- Wait for pullbacks on geopolitical spikes
- Only trade if confidence >= 7
- Prefer futures over micro-cap stocks (better liquidity)

Make the decision. No human approval needed.
"""
    
    log_action("🤖 Asking Jarvis for autonomous decision...")
    decision_text = ask_jarvis(prompt)
    
    if not decision_text:
        log_action("❌ Jarvis timeout")
        return log
    
    # Parse decision
    try:
        # Extract JSON from response
        import re
        json_match = re.search(r'\{[^}]+\}', decision_text, re.DOTALL)
        if json_match:
            decision = json.loads(json_match.group())
        else:
            decision = {"action": "WAIT", "reasoning": "Could not parse decision"}
    except:
        decision = {"action": "WAIT", "reasoning": "Parse error"}
    
    log_action(f"📊 DECISION: {decision.get('action', 'UNKNOWN')}")
    
    if decision.get('action') == 'TRADE':
        log_action(f"   Symbol: {decision.get('symbol')}")
        log_action(f"   Direction: {decision.get('direction')}")
        log_action(f"   Entry: ${decision.get('entry')}")
        log_action(f"   Stop: ${decision.get('stop')}")
        log_action(f"   Target: ${decision.get('target')}")
        log_action(f"   Confidence: {decision.get('confidence')}/10")
        log_action(f"   Reasoning: {decision.get('reasoning')}")
        
        # ── Psychology gate ──────────────────────────────
        trade_plan = {
            'symbol': decision.get('symbol'),
            'direction': decision.get('direction'),
            'entry_price': decision.get('entry'),
            'stop_loss': decision.get('stop'),
            'shares': decision.get('size', 1),
        }
        
        journal = TradeJournal()
        recent_trades = journal.get_recent_trades()
        
        # Load account balance from risk config
        risk_cfg = json.loads((Path(__file__).parent / 'config' / 'risk_limits.json').read_text())
        account_balance = risk_cfg.get('account_balance', 5000)
        
        can_trade, psych_data = validate_trade(trade_plan, account_balance, recent_trades)
        
        if not can_trade:
            reason = psych_data.get('reason', 'Unknown')
            log_action(f"🚫 REJECTED by psychology gate: {reason}")
            if psych_data.get('violations'):
                for v in psych_data['violations']:
                    log_action(f"   ⚠️  {v}")
            if psych_data.get('warnings'):
                for w in psych_data['warnings']:
                    log_action(f"   ⚠️  {w}")
            
            # Log rejection to journal
            journal.log_trade(
                {**trade_plan, 'outcome': 'REJECTED'},
                {**psych_data, 'rejected': True}
            )
            
            # Halt session on TILT
            if 'TILT' in reason:
                log_action("🛑 TILT STATE — halting all trading for this session")
                with open('data/autonomous_log.txt', 'a') as f:
                    f.write('\n'.join(log) + '\n\n')
                return log
        else:
            log_action(f"✅ Psychology gate PASSED")
            log_action(f"   Adherence: {psych_data.get('adherence_score', 'N/A')}")
            log_action(f"   Emotional state: {psych_data.get('emotional_state', 'N/A')}")
            
            # Log approved trade to journal
            journal.log_trade(trade_plan, psych_data)
            
            # Save trade signal
            with open('data/autonomous_signals.json', 'a') as f:
                signal = {
                    'timestamp': datetime.now().isoformat(),
                    'decision': decision,
                    'psychology': psych_data,
                }
                f.write(json.dumps(signal) + '\n')
            
            log_action("💾 Trade signal saved to data/autonomous_signals.json")
            log_action("⚠️  PAPER TRADING MODE - No real orders executed")
        
    elif decision.get('action') == 'WAIT':
        log_action(f"   Reasoning: {decision.get('reasoning')}")
        log_action("⏸️  No trade - waiting for better setup")
    
    else:
        log_action(f"   Reasoning: {decision.get('reasoning')}")
        log_action("👀 Monitoring - no action needed")
    
    # Save full log
    with open('data/autonomous_log.txt', 'a') as f:
        f.write('\n'.join(log) + '\n\n')
    
    log_action("="*60)
    log_action("✅ Autonomous scan complete")
    
    return log

if __name__ == '__main__':
    print("🤖 AUTONOMOUS TRADING SYSTEM")
    print("="*60)
    print("Running unsupervised - no human input needed")
    print("="*60)
    print()
    
    autonomous_scan()
    
    print()
    print("📁 Outputs:")
    print("  • data/autonomous_signals.json - Trade signals")
    print("  • data/autonomous_log.txt - Full log")
    print()
    print("Run continuously: watch -n 300 python3 autonomous.py")
