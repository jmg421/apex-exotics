#!/usr/bin/env python3
"""News Context for Trading Signals - Ask Jarvis about market news"""
import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.jarvis_client import jarvis_ask


def ask_jarvis_news(symbols, models=["xai_grok", "perplexity"]):
    """Ask Jarvis (with Grok/Perplexity) for real-time news context. Returns full result with synthesis."""
    
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
    
    print(f"🤖 Asking Jarvis ({', '.join(models)}) for news context...")
    result = jarvis_ask(prompt, models=models)
    return result

if __name__ == '__main__':
    print("📰 NEWS CONTEXT ANALYSIS")
    print("="*60)
    print()
    
    # Get news context from Jarvis (Grok + Perplexity have real-time web access)
    result = ask_jarvis_news(['CL', 'ES', 'NG'], models=["xai_grok", "perplexity"])
    
    if result and result.get("models"):
        models = result["models"]
        
        for name, data in models.items():
            print("="*60)
            print(f"🤖 {name.upper()}")
            print("="*60)
            if isinstance(data, dict):
                print(data.get('response', 'No response'))
            print()
        
        # Show synthesis
        if result.get("synthesis"):
            print("="*60)
            print("🧠 SYNTHESIS")
            print("="*60)
            print(result["synthesis"].get("unified_answer", ""))
            print(f"\nConfidence: {result['synthesis'].get('confidence_score', 'N/A')}")
        
        # Save
        news_context = {
            'timestamp': datetime.now().isoformat(),
            'symbols_analyzed': ['CL', 'ES', 'NG'],
            'models': models,
            'synthesis': result.get("synthesis"),
        }
        
        with open('data/news_context.json', 'w') as f:
            json.dump(news_context, f, indent=2)
        
        print("\n💾 Saved to data/news_context.json")
    else:
        print("❌ Failed to get news context")
