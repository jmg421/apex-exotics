#!/usr/bin/env python3
"""Autonomous Trading System - Unsupervised, no human input needed"""
import json
import time
import requests
from datetime import datetime
import subprocess

JARVIS_URL = "https://staging.nodes.bio/api/jarvis/generate"
JARVIS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTZmYjFmOTM4OTQ3ZjJhZCIsImVtYWlsIjoiam9obkBub2Rlcy5iaW8iLCJleHAiOjE3NzU0OTg4MjYsImlhdCI6MTc3MjkwNjgyNn0.8NVXoJByiRCHhOaptfTdbIkcjMpOkMQtCqbKPPIwL2w"

def ask_jarvis(prompt, models=["anthropic"]):
    """Query Jarvis"""
    headers = {
        "Authorization": f"Bearer {JARVIS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    resp = requests.post(JARVIS_URL, headers=headers, 
                        json={"prompt": prompt, "models": models}, timeout=30)
    result = resp.json()
    
    poll_url = f"https://staging.nodes.bio{result['poll_url']}"
    
    for _ in range(60):
        time.sleep(1)
        poll_resp = requests.get(poll_url, headers=headers, timeout=10)
        poll_data = poll_resp.json()
        
        if poll_data['status'] == 'completed':
            return poll_data['models'].get('anthropic', {}).get('response', '')
    
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
        
        # Save trade signal
        with open('data/autonomous_signals.json', 'a') as f:
            signal = {
                'timestamp': datetime.now().isoformat(),
                'decision': decision
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
