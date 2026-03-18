#!/usr/bin/env python3
"""Ask Jarvis to analyze pattern detection results"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.jarvis_client import jarvis_ask

if __name__ == '__main__':
    # Load pattern detection results
    with open('data/pattern_detection.json', 'r') as f:
        results = json.load(f)
    
    # Build prompt
    prompt = f"""Analyze these market open patterns from {results['total_stocks']} micro-cap stocks:

ANOMALIES ({len(results['anomalies'])} stocks):
"""
    for a in results['anomalies'][:5]:
        prompt += f"- {a['symbol']}: {a['change_percent']:+.2f}% on {a['volume']:,} volume\n"
    
    prompt += f"\nCLUSTERS ({len(results['clusters'])} patterns):\n"
    for cluster_id, members in results['clusters'].items():
        avg_change = sum(m['change_percent'] for m in members) / len(members)
        avg_volume = sum(m['volume'] for m in members) / len(members)
        symbols = [m['symbol'] for m in members]
        prompt += f"- Cluster {cluster_id}: {len(members)} stocks, {avg_change:+.2f}% avg, {int(avg_volume):,} vol\n"
        prompt += f"  Members: {', '.join(symbols[:5])}\n"
    
    prompt += """
Questions:
1. Which anomalies are most interesting for further investigation?
2. What trading strategies fit each cluster pattern?
3. Any red flags or risks to watch?

Keep it concise and actionable."""
    
    print("🤖 Asking Jarvis...")
    print("="*60)
    
    result = jarvis_ask(prompt, models=["anthropic_claude", "openai_gpt"])
    
    # Show synthesis first
    if result.get("synthesis"):
        print("\n🧠 SYNTHESIS")
        print("-"*60)
        print(result["synthesis"].get("unified_answer", ""))
        print(f"\nConfidence: {result['synthesis'].get('confidence_score', 'N/A')}")
    
    # Show individual model responses
    for model, data in result.get("models", {}).items():
        print(f"\n📊 {model.upper()}")
        print("-"*60)
        if isinstance(data, dict):
            print(data.get('response', data.get('error', 'No response')))
        else:
            print(data)
    
    # Save
    with open('data/jarvis_analysis.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("\n" + "="*60)
    print("💾 Saved to data/jarvis_analysis.json")
