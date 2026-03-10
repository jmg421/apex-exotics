#!/usr/bin/env python3
"""DXFeed Real Market Data Connector"""
import sys

# Check if dxfeed is installed
try:
    from dxfeed import Endpoint
    from dxfeed.core import DXFeedPriceLevelBook
except ImportError:
    print("❌ dxfeed package not installed")
    print("\nInstall with:")
    print("  pip install dxfeed")
    print("\nOr try demo without installation:")
    print("  pip install dxfeed && python3 dxfeed_connector.py")
    sys.exit(1)

import json
from datetime import datetime
import time

def get_quotes_dxfeed(symbols, demo=True):
    """Get real-time quotes from DXFeed"""
    
    # Demo endpoint (free, delayed data)
    # Production: requires subscription from dxfeed.com
    endpoint_url = 'demo.dxfeed.com:7300' if demo else 'YOUR_ENDPOINT:PORT'
    
    print(f"Connecting to DXFeed: {endpoint_url}")
    
    try:
        # Create endpoint
        endpoint = Endpoint(endpoint_url)
        
        # Create subscription for quotes
        sub = endpoint.create_subscription('Quote')
        
        # Store results
        quotes = []
        
        # Add symbols
        sub.add_symbols(symbols)
        
        # Wait for data
        print("Waiting for quotes...")
        time.sleep(3)
        
        # Get data
        for symbol in symbols:
            data = sub.get_last_event(symbol)
            if data:
                quotes.append({
                    'symbol': symbol,
                    'bid': data.bid_price if hasattr(data, 'bid_price') else 0,
                    'ask': data.ask_price if hasattr(data, 'ask_price') else 0,
                    'price': (data.bid_price + data.ask_price) / 2 if hasattr(data, 'bid_price') else 0,
                    'timestamp': datetime.now().isoformat()
                })
        
        endpoint.close_connection()
        return quotes
        
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_futures_quotes_dxfeed(symbols, demo=True):
    """Get CME futures quotes from DXFeed"""
    # DXFeed futures format: /ESH26 (ES March 2026)
    futures_symbols = [f"/{s}H26" for s in symbols]
    return get_quotes_dxfeed(futures_symbols, demo)

if __name__ == '__main__':
    print("🔌 DXFeed Real Market Data Test")
    print("="*60)
    
    # Test with demo endpoint (free, delayed)
    print("\n📊 Testing stock quotes...")
    stocks = ['AAPL', 'MSFT', 'TSLA']
    stock_quotes = get_quotes_dxfeed(stocks, demo=True)
    
    if stock_quotes:
        print("✅ Stock quotes:")
        for q in stock_quotes:
            print(f"  {q['symbol']:6} Bid: ${q['bid']:.2f} Ask: ${q['ask']:.2f}")
    else:
        print("❌ No stock quotes received")
    
    print("\n📈 Testing futures quotes...")
    futures = ['ES', 'NQ', 'GC']
    futures_quotes = get_futures_quotes_dxfeed(futures, demo=True)
    
    if futures_quotes:
        print("✅ Futures quotes:")
        for q in futures_quotes:
            print(f"  {q['symbol']:8} Bid: ${q['bid']:.2f} Ask: ${q['ask']:.2f}")
    else:
        print("❌ No futures quotes received")
    
    print("\n" + "="*60)
    print("📝 Notes:")
    print("  • Demo endpoint provides delayed data (15-20 min)")
    print("  • For real-time: Subscribe at dxfeed.com/market-data")
    print("  • CME futures: ~$50-100/mo for retail")
    print("  • Stocks: ~$30-50/mo for real-time")
