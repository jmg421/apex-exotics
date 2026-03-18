#!/usr/bin/env python3
"""Ask Jarvis: What should I do RIGHT NOW with the CL oil trade?"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.jarvis_client import jarvis_ask

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

if __name__ == '__main__':
    print("⚡ JARVIS: WHAT'S MY MOVE?")
    print("="*60)
    
    result = jarvis_ask(prompt, models=["anthropic_claude", "openai_gpt"])
    
    # Show synthesis (the unified decision)
    if result.get("synthesis"):
        print("\n🧠 SYNTHESIZED DECISION")
        print("="*60)
        print(result["synthesis"].get("unified_answer", ""))
        print(f"\nConfidence: {result['synthesis'].get('confidence_score', 'N/A')}")
        if result["synthesis"].get("disagreements"):
            print(f"⚠️  Disagreements: {result['synthesis']['disagreements']}")
    
    # Show individual models
    for model, data in result.get("models", {}).items():
        print(f"\n📊 {model.upper()}")
        print("="*60)
        if isinstance(data, dict):
            print(data.get('response', 'No response'))
    
    # Save
    with open('data/jarvis_trading_decision.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("\n💾 Saved to data/jarvis_trading_decision.json")
