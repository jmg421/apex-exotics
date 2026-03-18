#!/usr/bin/env python3
"""Futures Pattern Detection + Jarvis Analysis"""
import json
import sys
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.jarvis_client import jarvis_ask

def detect_patterns(quotes):
    """Detect patterns in futures data"""
    features = []
    symbols = []
    
    for q in quotes:
        features.append([
            q['change_percent'],
            np.log1p(q['volume']),
            abs(q['change_percent']),
            q['change_percent'] * np.log1p(q['volume'])
        ])
        symbols.append(q['symbol'])
    
    X = StandardScaler().fit_transform(features)
    labels = DBSCAN(eps=0.8, min_samples=2).fit(X).labels_
    
    anomalies = []
    clusters = {}
    
    for symbol, label, quote in zip(symbols, labels, quotes):
        if label == -1:
            anomalies.append(quote)
        else:
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(quote)
    
    return anomalies, clusters

def ask_jarvis(prompt):
    """Query Jarvis API with synthesis."""
    result = jarvis_ask(prompt, models=["anthropic_claude"])
    if result.get("synthesis"):
        return result["synthesis"].get("unified_answer", "")
    for m in result.get("models", {}).values():
        if isinstance(m, dict) and m.get("response"):
            return m["response"]
    return "Timeout"

if __name__ == '__main__':
    print("🔍 FUTURES PATTERN DETECTION")
    print("="*60)
    
    # Load futures data
    with open('data/futures_snapshot.json', 'r') as f:
        snapshot = json.load(f)
    
    quotes = snapshot['quotes']
    anomalies, clusters = detect_patterns(quotes)
    
    print(f"📊 Analyzed {len(quotes)} futures contracts")
    print(f"🔥 Anomalies: {len(anomalies)}")
    print(f"📈 Clusters: {len(clusters)}")
    print()
    
    # Build prompt for Jarvis
    prompt = f"""CME Futures Market Analysis - {len(quotes)} contracts at market open:

ANOMALIES ({len(anomalies)} contracts):
"""
    for a in anomalies:
        prompt += f"- {a['symbol']}: ${a['price']:.2f} ({a['change_percent']:+.2f}%) | Vol: {a['volume']:,}\n"
    
    prompt += f"\nCLUSTERS ({len(clusters)} patterns):\n"
    for cid, members in clusters.items():
        avg_change = np.mean([m['change_percent'] for m in members])
        symbols = [m['symbol'] for m in members]
        prompt += f"- Cluster {cid}: {', '.join(symbols)} | Avg: {avg_change:+.2f}%\n"
    
    prompt += """
For bracket orders (3 contracts: entry, stop -$10, targets +$10/+$20/+$30):

1. Which futures contracts have the best setup RIGHT NOW?
2. Should I go LONG or SHORT on each?
3. Any correlated moves to watch (e.g., ES/NQ, GC/SI)?
4. Risk management: which to avoid?

Be specific and actionable."""
    
    print("🤖 Asking Jarvis...")
    response = ask_jarvis(prompt)
    
    print("\n" + "="*60)
    print("📊 JARVIS ANALYSIS")
    print("="*60)
    print(response)
    
    # Save
    results = {
        'timestamp': snapshot['timestamp'],
        'anomalies': anomalies,
        'clusters': {str(k): v for k, v in clusters.items()},
        'jarvis_analysis': response
    }
    
    with open('data/futures_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n💾 Saved to data/futures_analysis.json")
