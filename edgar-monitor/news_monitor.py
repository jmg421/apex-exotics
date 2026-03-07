#!/usr/bin/env python3
"""Monitor portfolio holdings for news and SEC filings."""

import feedparser
from pathlib import Path
import json
from datetime import datetime, timedelta
from paper_trading import load_portfolio

DATA_DIR = Path(__file__).parent / "data"
NEWS_FILE = DATA_DIR / "news_alerts.json"

def load_news_history():
    """Load previously seen news to avoid duplicates."""
    if NEWS_FILE.exists():
        with open(NEWS_FILE) as f:
            return json.load(f)
    return {"alerts": [], "last_check": None}

def save_news_history(history):
    """Save news history."""
    with open(NEWS_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def check_sec_filings(ticker):
    """Check for recent SEC filings (8-K = material events)."""
    url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=8-K&dateb=&owner=exclude&count=5&output=atom"
    
    try:
        feed = feedparser.parse(url)
        recent_filings = []
        
        cutoff = datetime.now() - timedelta(days=7)
        
        for entry in feed.entries[:5]:
            filing_date = datetime(*entry.updated_parsed[:6])
            
            if filing_date > cutoff:
                recent_filings.append({
                    'ticker': ticker,
                    'type': '8-K',
                    'date': filing_date.isoformat(),
                    'title': entry.title,
                    'link': entry.link,
                    'summary': 'Material event filing - check for fundamental changes'
                })
        
        return recent_filings
    except Exception as e:
        print(f"Error checking {ticker}: {e}")
        return []

def check_all_holdings():
    """Check all portfolio holdings for news."""
    portfolio = load_portfolio()
    history = load_news_history()
    
    new_alerts = []
    seen_links = {alert['link'] for alert in history['alerts']}
    
    print(f"\nChecking {len(portfolio['positions'])} holdings for news...")
    print("="*80)
    
    for ticker in portfolio['positions'].keys():
        print(f"\n{ticker}:")
        filings = check_sec_filings(ticker)
        
        for filing in filings:
            if filing['link'] not in seen_links:
                new_alerts.append(filing)
                seen_links.add(filing['link'])
                
                print(f"  🚨 NEW: {filing['type']} filed {filing['date'][:10]}")
                print(f"     {filing['title']}")
                print(f"     {filing['link']}")
            else:
                print(f"  ✓ Already seen: {filing['type']} from {filing['date'][:10]}")
    
    if new_alerts:
        print("\n" + "="*80)
        print(f"📰 {len(new_alerts)} NEW ALERTS")
        print("="*80)
        
        for alert in new_alerts:
            print(f"\n{alert['ticker']}: {alert['type']} - {alert['date'][:10]}")
            print(f"  {alert['summary']}")
            print(f"  {alert['link']}")
        
        # Save to history
        history['alerts'].extend(new_alerts)
        history['last_check'] = datetime.now().isoformat()
        save_news_history(history)
    else:
        print("\n✓ No new material events")
    
    print("\n" + "="*80)
    print(f"Last check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total alerts tracked: {len(history['alerts'])}")

if __name__ == '__main__':
    check_all_holdings()
