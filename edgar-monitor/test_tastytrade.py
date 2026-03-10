#!/usr/bin/env python3
"""Tastytrade Real Market Data Connector"""
import requests
import json

def get_tastytrade_token():
    """Get access token"""
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('TASTYTRADE_REFRESH_TOKEN='):
                refresh_token = line.split('=', 1)[1].strip()
            elif line.startswith('TASTYTRADE_CLIENT_SECRET='):
                client_secret = line.split('=', 1)[1].strip()
    
    url = "https://api.cert.tastyworks.com/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_secret": client_secret
    }
    
    resp = requests.post(url, json=data, timeout=10)
    if resp.status_code == 200:
        return resp.json()["access_token"]
    else:
        print(f"Auth failed: {resp.status_code} - {resp.text}")
        return None

def get_quotes(symbols, token):
    """Get real-time quotes from Tastytrade"""
    # Try production API
    urls = [
        "https://api.tastyworks.com/market-data/quotes",
        "https://api.cert.tastyworks.com/market-data/quotes"
    ]
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {"symbols": ",".join(symbols)}
    
    for url in urls:
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            print(f"Trying {url}: {resp.status_code}")
            
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"Response: {resp.text[:200]}")
        except Exception as e:
            print(f"Error: {e}")
    
    return None

def get_futures_quotes(symbols, token):
    """Get futures quotes (different endpoint)"""
    # Tastytrade futures symbols format: /ESH26 (ES March 2026)
    futures_symbols = [f"/{s}H26" for s in symbols]  # H = March contract
    
    return get_quotes(futures_symbols, token)

if __name__ == '__main__':
    print("🔌 Testing Tastytrade Real Data Feed")
    print("="*60)
    
    # Get token
    print("Authenticating...")
    token = get_tastytrade_token()
    
    if not token:
        print("❌ Authentication failed")
        exit(1)
    
    print("✅ Authenticated")
    print()
    
    # Test stock quotes
    print("Testing stock quotes...")
    stock_symbols = ['AAPL', 'MSFT', 'TSLA']
    stock_data = get_quotes(stock_symbols, token)
    
    if stock_data:
        print(f"✅ Got stock data: {json.dumps(stock_data, indent=2)[:500]}")
    else:
        print("❌ Stock quotes failed")
    
    print()
    
    # Test futures quotes
    print("Testing futures quotes...")
    futures_symbols = ['ES', 'NQ', 'GC']
    futures_data = get_futures_quotes(futures_symbols, token)
    
    if futures_data:
        print(f"✅ Got futures data: {json.dumps(futures_data, indent=2)[:500]}")
    else:
        print("❌ Futures quotes failed")
