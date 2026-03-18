#!/usr/bin/env python3
"""Ask Jarvis to vet the go-live trading plan"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.jarvis_client import jarvis_ask

prompt = """I'm about to go live with a systematic trading system. Vet this plan and tell me what I'm missing:

## THE SYSTEM

**Pattern Detection:**
- DBSCAN clustering on 27 micro-cap stocks + 10 CME futures
- Scans every 5 minutes during market hours (9:30 AM - 4:00 PM)
- Identifies anomalies (stocks/futures behaving differently from clusters)
- Multi-model AI analysis (Claude + GPT-4) for trade recommendations

**Trading Strategy:**
- Futures: 3-contract bracket orders (entry, stop -$10, targets +$10/+$20/+$30)
- Stocks: Swing trades on momentum anomalies (5-10% targets, 1-3 day holds)
- Risk: $10 per futures trade, 2% account risk per stock trade

**Risk Management:**
- Max daily loss: $100
- Max positions: 3 concurrent
- Max risk per trade: $10 (futures) or 2% account (stocks)
- Auto-stop if daily loss hit

**Capital:**
- Starting with $2,000-5,000
- Futures margin: $500/contract × 3 = $1,500
- Stock positions: $500-1,000 each

**Data Sources:**
- Yahoo Finance (free, rate-limited) OR Polygon.io ($29/mo)
- CME WebSocket API (~$50/mo for futures)
- Execution via Tastytrade API

**Costs:**
- Data: $0-80/mo
- Commissions: ~$50-100/mo
- Total overhead: ~$150/mo max

## MY QUESTIONS

1. **What am I missing?** What risks or failure modes am I not seeing?
2. **Is $2,000-5,000 enough capital?** Or am I undercapitalized?
3. **Risk management holes?** Are my limits too tight or too loose?
4. **Data quality concerns?** Yahoo Finance vs paid feeds - does it matter for 5-min scans?
5. **Execution risks?** What can go wrong between signal and order fill?
6. **Realistic expectations?** If I target $200-500/mo profit, am I delusional?
7. **What should I test first?** Paper trade for 30 days or start small with real money?
8. **Red flags?** Any part of this plan that screams "bad idea"?

Be brutally honest. I want to know what will break before it breaks.
"""

if __name__ == '__main__':
    print("🤖 ASKING JARVIS TO VET THE TRADING PLAN")
    print("="*60)
    
    result = jarvis_ask(prompt, models=["anthropic_claude", "openai_gpt"])
    
    if result.get("synthesis"):
        print("\n🧠 SYNTHESIZED REVIEW")
        print("="*60)
        print(result["synthesis"].get("unified_answer", ""))
        print(f"\nConfidence: {result['synthesis'].get('confidence_score', 'N/A')}")
    
    for model, data in result.get("models", {}).items():
        print(f"\n📊 {model.upper()}")
        print("="*60)
        if isinstance(data, dict):
            print(data.get('response', 'No response'))
    
    with open('data/jarvis_plan_review.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("\n💾 Saved to data/jarvis_plan_review.json")
