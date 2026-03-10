#!/usr/bin/env python3
"""Ask Jarvis to vet the go-live trading plan"""
import requests
import time

JARVIS_URL = "https://staging.nodes.bio/api/jarvis/generate"
JARVIS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTZmYjFmOTM4OTQ3ZjJhZCIsImVtYWlsIjoiam9obkBub2Rlcy5iaW8iLCJleHAiOjE3NzU0OTg4MjYsImlhdCI6MTc3MjkwNjgyNn0.8NVXoJByiRCHhOaptfTdbIkcjMpOkMQtCqbKPPIwL2w"

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

def ask_jarvis(prompt):
    """Query Jarvis API"""
    headers = {
        "Authorization": f"Bearer {JARVIS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    resp = requests.post(JARVIS_URL, headers=headers, 
                        json={"prompt": prompt, "models": ["anthropic", "openai"]}, timeout=30)
    result = resp.json()
    
    poll_url = f"https://staging.nodes.bio{result['poll_url']}"
    
    print("Waiting for Jarvis analysis", end='', flush=True)
    for _ in range(60):
        time.sleep(1)
        print('.', end='', flush=True)
        poll_resp = requests.get(poll_url, headers=headers, timeout=10)
        poll_data = poll_resp.json()
        
        if poll_data['status'] == 'completed':
            print(" Done!\n")
            return poll_data['models']
    
    print(" Timeout!")
    return None

if __name__ == '__main__':
    print("🤖 ASKING JARVIS TO VET THE TRADING PLAN")
    print("="*60)
    print()
    
    response = ask_jarvis(prompt)
    
    if response:
        print("="*60)
        print("📊 ANTHROPIC (CLAUDE) ANALYSIS")
        print("="*60)
        if 'anthropic' in response:
            print(response['anthropic'].get('response', 'No response'))
        
        print("\n" + "="*60)
        print("📊 OPENAI (GPT-4) ANALYSIS")
        print("="*60)
        if 'openai' in response:
            print(response['openai'].get('response', 'No response'))
        
        # Save
        import json
        with open('data/jarvis_plan_review.json', 'w') as f:
            json.dump(response, f, indent=2)
        
        print("\n" + "="*60)
        print("💾 Saved to data/jarvis_plan_review.json")
    else:
        print("❌ Failed to get response from Jarvis")
