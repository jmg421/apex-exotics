#!/usr/bin/env python3
"""Live Trading Dashboard with Jarvis Commentary"""
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.jarvis_client import jarvis_ask


def ask_jarvis(prompt):
    """Get Jarvis commentary with synthesis."""
    result = jarvis_ask(prompt, models=["anthropic_claude"])
    if result.get("synthesis"):
        return result["synthesis"].get("unified_answer", "...")
    for m in result.get("models", {}).values():
        if isinstance(m, dict) and m.get("response"):
            return m["response"]
    return "..."

def load_news():
    """Load latest news context"""
    try:
        with open('data/news_context.json', 'r') as f:
            return json.load(f)
    except:
        return None

def load_market_data():
    """Load latest market snapshot"""
    try:
        with open('data/pattern_detection.json', 'r') as f:
            stocks = json.load(f)
        with open('data/futures_analysis.json', 'r') as f:
            futures = json.load(f)
        return stocks, futures
    except:
        return None, None

def display_dashboard():
    """Display live dashboard with Jarvis commentary"""
    os.system('clear')
    
    print("🎯 AUTONOMOUS TRADING DASHBOARD - LIVE")
    print("="*70)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    print("="*70)
    print()
    
    print("📡 Loading market data...")
    stocks, futures = load_market_data()
    news = load_news()
    
    if not stocks or not futures:
        print("⏳ Waiting for market data...")
        return
    
    # Show top movers
    print("📊 MARKET SNAPSHOT")
    print("-"*70)
    
    top_stocks = sorted(stocks['anomalies'], key=lambda x: abs(x['change_percent']), reverse=True)[:5]
    for s in top_stocks:
        emoji = "🟢" if s['change_percent'] > 0 else "🔴"
        print(f"{emoji} {s['symbol']:6s} {s['change_percent']:+6.2f}%  Vol: {s['volume']:>12,}")
    
    print()
    for f in futures['anomalies']:
        emoji = "🟢" if f['change_percent'] > 0 else "🔴"
        print(f"{emoji} {f['symbol']:6s} {f['change_percent']:+6.2f}%  ${f['price']:.2f}")
    
    # Show news headlines
    if news and 'articles' in news:
        print()
        print("📰 LATEST NEWS")
        print("-"*70)
        for article in news['articles'][:3]:
            title = article.get('title', '')[:65]
            print(f"• {title}...")
    
    print()
    print("="*70)
    print("🤖 JARVIS ANALYSIS (querying...)")
    print("-"*70)
    
    # Build prompt for Jarvis
    prompt = f"""You're explaining markets to someone smart but new to trading. Current time: {datetime.now().strftime('%H:%M ET')}.

Market snapshot:
"""
    for s in top_stocks[:3]:
        prompt += f"- {s['symbol']}: {s['change_percent']:+.2f}%\n"
    for f in futures['anomalies']:
        prompt += f"- {f['symbol']}: {f['change_percent']:+.2f}%\n"
    
    if news and 'articles' in news:
        prompt += "\nTop headlines:\n"
        for article in news['articles'][:3]:
            prompt += f"- {article.get('title', '')}\n"
    
    prompt += """
Explain what's happening RIGHT NOW in 2-3 sentences. Use plain English - say "crude oil" not "CL=F", "S&P 500" not "ES=F". Connect the news to the market moves.

Then add: "TRADE IDEA:" followed by either a specific setup in plain terms OR "WAIT - [reason]"."""
    
    try:
        commentary = ask_jarvis(prompt)
    except Exception as e:
        commentary = f"[Jarvis unavailable: {str(e)}]"
    
    # Wrap text to 70 chars
    words = commentary.split()
    line = ""
    for word in words:
        if len(line) + len(word) + 1 <= 70:
            line += word + " "
        else:
            print(line)
            line = word + " "
    if line:
        print(line)
    
    print()
    print("="*70)
    print("⏱️  Refreshing in 5 minutes... (Ctrl+C to exit)")

if __name__ == '__main__':
    try:
        while True:
            display_dashboard()
            time.sleep(300)  # 5 minutes
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard closed")
