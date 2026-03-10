#!/usr/bin/env python3
"""Unsupervised Pattern Detection - Market Open Anomalies"""
import json
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from datetime import datetime

def load_snapshot():
    """Load market open snapshot"""
    with open('data/market_open_snapshot.json', 'r') as f:
        return json.load(f)

def extract_features(quotes):
    """Extract features for clustering"""
    features = []
    symbols = []
    
    for q in quotes:
        features.append([
            q['change_percent'],           # Price momentum
            np.log1p(q['volume']),         # Log volume (normalize scale)
            abs(q['change_percent']),      # Volatility
            q['change_percent'] * np.log1p(q['volume'])  # Momentum * Volume
        ])
        symbols.append(q['symbol'])
    
    return np.array(features), symbols

def detect_anomalies(quotes):
    """Find anomalous patterns using DBSCAN"""
    X, symbols = extract_features(quotes)
    
    # Normalize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # DBSCAN: eps controls sensitivity, lower = more anomalies
    clustering = DBSCAN(eps=0.7, min_samples=3).fit(X_scaled)
    labels = clustering.labels_
    
    # Group results
    clusters = {}
    anomalies = []
    
    for symbol, label, quote in zip(symbols, labels, quotes):
        if label == -1:
            anomalies.append(quote)
        else:
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(quote)
    
    return anomalies, clusters

if __name__ == '__main__':
    print(f"🔍 UNSUPERVISED PATTERN DETECTION")
    print("="*60)
    
    snapshot = load_snapshot()
    quotes = snapshot['quotes']
    
    print(f"📊 Analyzing {len(quotes)} stocks from market open")
    print(f"⏰ Timestamp: {snapshot['timestamp']}")
    print()
    
    anomalies, clusters = detect_anomalies(quotes)
    
    # Report anomalies
    print(f"🔥 ANOMALIES DETECTED: {len(anomalies)}")
    print("   (Stocks that don't fit any pattern - investigate!)")
    print()
    
    for q in sorted(anomalies, key=lambda x: abs(x['change_percent']), reverse=True):
        print(f"  {q['symbol']:6} ${q['price']:7.2f} {q['change_percent']:+6.2f}% | Vol: {q['volume']:,}")
    
    # Report clusters
    print(f"\n📈 PATTERN CLUSTERS: {len(clusters)}")
    print()
    
    for cluster_id, members in sorted(clusters.items()):
        avg_change = np.mean([m['change_percent'] for m in members])
        avg_volume = np.mean([m['volume'] for m in members])
        
        print(f"  Cluster {cluster_id} ({len(members)} stocks)")
        print(f"    Pattern: {avg_change:+.2f}% avg change | {int(avg_volume):,} avg volume")
        print(f"    Members: {', '.join([m['symbol'] for m in members[:8]])}")
        if len(members) > 8:
            print(f"             ... and {len(members) - 8} more")
        print()
    
    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_stocks': len(quotes),
        'anomalies': anomalies,
        'clusters': {str(k): v for k, v in clusters.items()}
    }
    
    with open('data/pattern_detection.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Saved to data/pattern_detection.json")
