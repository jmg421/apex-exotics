#!/usr/bin/env python3
"""News Context for Trading Signals - Ask Jarvis about market news"""
import requests
import time
import json
from datetime import datetime

JARVIS_URL = "https://staging.nodes.bio/api/jarvis/generate"
JARVIS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTZmYjFmOTM4OTQ3ZjJhZCIsImVtYWlsIjoiam9obkBub2Rlcy5iaW8iLCJleHAiOjE3NzU0OTg4MjYsImlhdCI6MTc3MjkwNjgyNn0.8NVXoJByiRCHhOaptfTdbIkcjMpOkMQtCqbKPPIwL2w"

def ask_jarvis_news(symbols, models=["grok", "perplexity"]):
    """Ask Jarvis (with Grok/Perplexity) for real-time news context"""
    
    prompt = f"""What's happening in the markets RIGHT NOW that explains these moves?

CURRENT MARKET DATA (as of {datetime.now().strftime('%Y-%m-%d %H:%M ET')}):

FUTURES:
- CL (Crude Oil): +9.11% - MASSIVE MOVE
- NG (Natural Gas): +1.88%
- ES (S&P 500): -1.19%
- NQ (Nasdaq): -1.14%
- GC (Gold): -1.10%

QUESTIONS:
1. Why is crude oil up 9%+ today? What news broke?
2. Is this geopolitical (Middle East, Russia) or supply-related?
3. Are equities down BECAUSE of oil spike (inflation fears)?
4. Is this a tradeable move or news-driven spike that will fade?
5. What's the catalyst timeline - is this just starting or already priced in?

Give me ACTIONABLE context:
- What happened (specific news/events)
- When it happened (timing matters)
- How to trade it (fade the spike or ride momentum?)
- Risk factors (what could reverse this?)

Be specific. I need to decide whether to go LONG CL right now.
"""
    
    headers = {
        "Authorization": f"Bearer {JARVIS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"🤖 Asking Jarvis ({', '.join(models)}) for news context...")
    
    resp = requests.post(JARVIS_URL, headers=headers, 
                        json={"prompt": prompt, "models": models}, timeout=30)
    result = resp.json()
    
    poll_url = f"https://staging.nodes.bio{result['poll_url']}"
    
    print("Waiting for response", end='', flush=True)
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
    print("📰 NEWS CONTEXT ANALYSIS")
    print("="*60)
    print()
    
    # Get news context from Jarvis (Grok + Perplexity have real-time web access)
    response = ask_jarvis_news(['CL', 'ES', 'NG'], models=["grok", "perplexity"])
    
    if response:
        # Display Grok response (real-time Twitter/X data)
        if 'grok' in response:
            print("="*60)
            print("🤖 GROK ANALYSIS (Real-time X/Twitter data)")
            print("="*60)
            print(response['grok'].get('response', 'No response'))
            print()
        
        # Display Perplexity response (real-time web search)
        if 'perplexity' in response:
            print("="*60)
            print("🔍 PERPLEXITY ANALYSIS (Real-time web search)")
            print("="*60)
            print(response['perplexity'].get('response', 'No response'))
            print()
        
        # Save
        news_context = {
            'timestamp': datetime.now().isoformat(),
            'symbols_analyzed': ['CL', 'ES', 'NG'],
            'news_analysis': response
        }
        
        with open('data/news_context.json', 'w') as f:
            json.dump(news_context, f, indent=2)
        
        print("="*60)
        print("💾 Saved to data/news_context.json")
        
        # Quick summary
        print("\n📊 TRADING DECISION:")
        print("="*60)
        
        # Check if responses mention specific catalysts
        all_text = str(response).lower()
        
        if 'geopolitical' in all_text or 'middle east' in all_text or 'opec' in all_text:
            print("⚠️  GEOPOLITICAL CATALYST - High risk, could reverse quickly")
        
        if 'supply' in all_text or 'production' in all_text:
            print("✅ SUPPLY-DRIVEN - More sustainable move")
        
        if 'fade' in all_text or 'spike' in all_text:
            print("🔴 RECOMMENDATION: Wait for pullback or fade the move")
        elif 'momentum' in all_text or 'breakout' in all_text:
            print("🟢 RECOMMENDATION: Ride the momentum with tight stops")
        
    else:
        print("❌ Failed to get news context")
