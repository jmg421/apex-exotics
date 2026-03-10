#!/usr/bin/env python3
"""Futures Pattern Detection + Jarvis Analysis"""
import json
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import requests
import time

JARVIS_URL = "https://staging.nodes.bio/api/jarvis/generate"
JARVIS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTZmYjFmOTM4OTQ3ZjJhZCIsImVtYWlsIjoiam9obkBub2Rlcy5iaW8iLCJleHAiOjE3NzU0OTg4MjYsImlhdCI6MTc3MjkwNjgyNn0.8NVXoJByiRCHhOaptfTdbIkcjMpOkMQtCqbKPPIwL2w"

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
    """Query Jarvis API"""
    headers = {
        "Authorization": f"Bearer {JARVIS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    resp = requests.post(JARVIS_URL, headers=headers, 
                        json={"prompt": prompt, "models": ["anthropic"]}, timeout=30)
    result = resp.json()
    
    poll_url = f"https://staging.nodes.bio{result['poll_url']}"
    
    for _ in range(30):
        time.sleep(1)
        poll_resp = requests.get(poll_url, headers=headers, timeout=10)
        poll_data = poll_resp.json()
        
        if poll_data['status'] == 'completed':
            return poll_data['models']['anthropic']
    
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
