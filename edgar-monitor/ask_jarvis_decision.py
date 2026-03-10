#!/usr/bin/env python3
"""Ask Jarvis: What should I do RIGHT NOW with the CL oil trade?"""
import requests
import time
import json

JARVIS_URL = "https://staging.nodes.bio/api/jarvis/generate"
JARVIS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTZmYjFmOTM4OTQ3ZjJhZCIsImVtYWlsIjoiam9obkBub2Rlcy5iaW8iLCJleHAiOjE3NzU0OTg4MjYsImlhdCI6MTc3MjkwNjgyNn0.8NVXoJByiRCHhOaptfTdbIkcjMpOkMQtCqbKPPIwL2w"

prompt = """I need a decision RIGHT NOW. It's 9:53 AM ET on Monday, March 9, 2026.

## THE SITUATION

**Crude Oil (CL) is up +9.11% at $99.18**

**Why:**
- Strait of Hormuz disruptions (US-Iran tensions)
- Short squeeze started March 6
- OPEC+ cuts (3.66M bpd)
- Analysts warn $100+ if tensions persist

**My System Says:**
- Pattern detection flagged CL as top anomaly
- Futures analysis recommended LONG
- News context says: "Geopolitical catalyst, high risk, wait for pullback"

**My Capital:**
- $2,000-5,000 available
- Can trade 1-2 CL contracts
- Max risk: $100/day

**My Options:**
1. **Go LONG now** at $99.18 (chase the momentum)
2. **Wait for pullback** to $95-96 (better entry)
3. **Fade the spike** (short with tight stop)
4. **Sit out** (too risky, wait for next setup)

## MY QUESTION

**What should I do RIGHT NOW?**

Give me ONE clear action:
- If LONG: Exact entry, stop, targets
- If WAIT: What price level to watch
- If SHORT: Entry and stop
- If SIT OUT: Why and what to watch instead

Be specific. I'm about to place an order. What's the move?
"""

def ask_jarvis(prompt):
    headers = {
        "Authorization": f"Bearer {JARVIS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    resp = requests.post(JARVIS_URL, headers=headers, 
                        json={"prompt": prompt, "models": ["anthropic", "openai"]}, timeout=30)
    result = resp.json()
    
    poll_url = f"https://staging.nodes.bio{result['poll_url']}"
    
    print("🤖 Asking Jarvis for trading decision", end='', flush=True)
    for _ in range(60):
        time.sleep(1)
        print('.', end='', flush=True)
        poll_resp = requests.get(poll_url, headers=headers, timeout=10)
        poll_data = poll_resp.json()
        
        if poll_data['status'] == 'completed':
            print(" Done!\n")
            return poll_data['models']
    
    return None

if __name__ == '__main__':
    print("⚡ JARVIS: WHAT'S MY MOVE?")
    print("="*60)
    print("Time: 9:53 AM ET")
    print("CL (Crude Oil): $99.18 (+9.11%)")
    print("="*60)
    print()
    
    response = ask_jarvis(prompt)
    
    if response:
        print("="*60)
        print("📊 CLAUDE'S DECISION")
        print("="*60)
        if 'anthropic' in response:
            print(response['anthropic'].get('response', 'No response'))
        
        print("\n" + "="*60)
        print("📊 GPT-4'S DECISION")
        print("="*60)
        if 'openai' in response:
            print(response['openai'].get('response', 'No response'))
        
        # Save
        with open('data/jarvis_trading_decision.json', 'w') as f:
            json.dump(response, f, indent=2)
        
        print("\n" + "="*60)
        print("💾 Saved to data/jarvis_trading_decision.json")
