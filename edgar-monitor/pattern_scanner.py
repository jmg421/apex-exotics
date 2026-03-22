#!/usr/bin/env python3
"""
Market Pattern Scanner - Unsupervised learning for micro-cap anomalies
Finds patterns in price/volume that predict moves before they happen
"""
import json
import numpy as np
from datetime import datetime, timedelta
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from collections import defaultdict
import requests

def fetch_price_history(ticker, days=30):
    """Get price/volume history from Alpha Vantage"""
    # Use free tier - 25 requests/day limit
    api_key = 'demo'  # Replace with real key from alphavantage.co
    
    url = f"https://www.alphavantage.co/query"
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': ticker,
        'apikey': api_key,
        'outputsize': 'compact'
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        if 'Time Series (Daily)' not in data:
            return []
        
        time_series = data['Time Series (Daily)']
        history = []
        
        for date_str in sorted(time_series.keys(), reverse=True)[:days]:
            day_data = time_series[date_str]
            history.append({
                'date': date_str,
                'open': float(day_data['1. open']),
                'high': float(day_data['2. high']),
                'low': float(day_data['3. low']),
                'close': float(day_data['4. close']),
                'volume': int(day_data['5. volume'])
            })
        
        return history
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return []

def extract_features(history):
    """Extract pattern features from price history"""
    if len(history) < 5:
        return None
    
    closes = [h['close'] for h in history]
    volumes = [h['volume'] for h in history]
    
    # Price features
    returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
    volatility = np.std(returns) if returns else 0
    
    # Volume features
    avg_volume = np.mean(volumes)
    volume_spike = volumes[-1] / avg_volume if avg_volume > 0 else 1
    
    # Momentum features
    sma_5 = np.mean(closes[-5:])
    sma_20 = np.mean(closes[-20:]) if len(closes) >= 20 else sma_5
    momentum = (closes[-1] - sma_20) / sma_20 if sma_20 > 0 else 0
    
    # Range features
    recent_high = max(closes[-5:])
    recent_low = min(closes[-5:])
    range_position = (closes[-1] - recent_low) / (recent_high - recent_low) if recent_high > recent_low else 0.5
    
    return {
        'volatility': volatility,
        'volume_spike': volume_spike,
        'momentum': momentum,
        'range_position': range_position,
        'price_change_1d': returns[-1] if returns else 0,
        'price_change_5d': (closes[-1] - closes[-5]) / closes[-5] if len(closes) >= 5 else 0
    }

def scan_patterns(tickers):
    """Scan all tickers and cluster by pattern"""
    print(f"Scanning {len(tickers)} tickers for patterns...")
    
    ticker_features = {}
    feature_matrix = []
    ticker_list = []
    
    for ticker in tickers:
        history = fetch_price_history(ticker)
        if not history:
            continue
        
        features = extract_features(history)
        if not features:
            continue
        
        ticker_features[ticker] = features
        feature_matrix.append([
            features['volatility'],
            features['volume_spike'],
            features['momentum'],
            features['range_position'],
            features['price_change_1d'],
            features['price_change_5d']
        ])
        ticker_list.append(ticker)
    
    if len(feature_matrix) < 3:
        print("Not enough data for clustering")
        return
    
    # Normalize features
    scaler = StandardScaler()
    X = scaler.fit_transform(feature_matrix)
    
    # DBSCAN clustering - finds anomalies (outliers = -1)
    clustering = DBSCAN(eps=0.8, min_samples=2).fit(X)
    labels = clustering.labels_
    
    # Group by cluster
    clusters = defaultdict(list)
    for ticker, label in zip(ticker_list, labels):
        clusters[label].append(ticker)
    
    # Print results
    print("\n" + "="*60)
    print("PATTERN CLUSTERS")
    print("="*60)
    
    # Anomalies (outliers)
    if -1 in clusters:
        print(f"\n🔥 ANOMALIES ({len(clusters[-1])} stocks)")
        print("These don't fit any pattern - potential breakouts:")
        for ticker in clusters[-1]:
            f = ticker_features[ticker]
            print(f"  {ticker:6} | Vol: {f['volume_spike']:.1f}x | Mom: {f['momentum']:+.1%} | Δ1d: {f['price_change_1d']:+.1%}")
    
    # Normal clusters
    for cluster_id in sorted(clusters.keys()):
        if cluster_id == -1:
            continue
        
        members = clusters[cluster_id]
        print(f"\nCluster {cluster_id} ({len(members)} stocks):")
        
        # Calculate cluster characteristics
        avg_features = {
            'volume_spike': np.mean([ticker_features[t]['volume_spike'] for t in members]),
            'momentum': np.mean([ticker_features[t]['momentum'] for t in members]),
            'volatility': np.mean([ticker_features[t]['volatility'] for t in members])
        }
        
        print(f"  Pattern: Vol {avg_features['volume_spike']:.1f}x | Mom {avg_features['momentum']:+.1%} | σ {avg_features['volatility']:.2%}")
        print(f"  Members: {', '.join(members[:10])}")
        if len(members) > 10:
            print(f"           ... and {len(members) - 10} more")

def load_watchlist():
    """Load tickers from EDGAR data"""
    try:
        with open('edgar-monitor/data/companies.json', 'r') as f:
            companies = json.load(f)
            return [c['ticker'] for c in companies if c.get('ticker')]
    except (FileNotFoundError, json.JSONDecodeError, OSError, KeyError):
        # Fallback to demo tickers
        return ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMD', 'INTC', 'META', 'AMZN', 'NFLX']

if __name__ == '__main__':
    tickers = load_watchlist()
    scan_patterns(tickers[:50])  # Start with first 50 to avoid rate limits
