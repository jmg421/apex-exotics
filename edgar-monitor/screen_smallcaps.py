#!/usr/bin/env python3
"""Quick screen of small-caps using yfinance."""

import json
from pathlib import Path
import yfinance as yf

DATA_DIR = Path(__file__).parent / "data"

def screen_smallcaps():
    """Screen small-caps for quality using yfinance."""
    
    # Load market caps
    with open(DATA_DIR / "market_caps.json") as f:
        caps = json.load(f)
    
    # Load filings
    with open(DATA_DIR / "filings.json") as f:
        filings = json.load(f)
    
    # Find small-caps with tickers
    smallcaps = []
    for cik, cap_data in caps.items():
        cap = cap_data.get('market_cap')
        ticker = cap_data.get('ticker')
        
        if cap and 100_000_000 <= cap <= 2_000_000_000 and ticker:
            # Find company name
            for filing in filings.values():
                if filing.get('cik') == cik:
                    smallcaps.append({
                        'cik': cik,
                        'ticker': ticker,
                        'company': filing.get('company'),
                        'market_cap': cap
                    })
                    break
    
    print(f"Screening {len(smallcaps)} small-caps with tickers...")
    print()
    
    quality = []
    
    for i, company in enumerate(smallcaps[:30], 1):  # Limit to 30 to avoid slowness
        ticker = company['ticker']
        print(f"[{i}/30] {ticker:6} {company['company'][:35]:35}...", end=" ", flush=True)
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            revenue = info.get('totalRevenue', 0)
            net_income = info.get('netIncomeToCommon', 0)
            profit_margin = info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0
            debt_to_equity = info.get('debtToEquity', 0)
            
            if revenue > 10_000_000 and net_income > 0 and profit_margin > 5:
                print(f"✓ QUALITY")
                quality.append({
                    **company,
                    'revenue': revenue,
                    'net_income': net_income,
                    'profit_margin': profit_margin,
                    'debt_to_equity': debt_to_equity,
                    'ps_ratio': company['market_cap'] / revenue if revenue else 0
                })
            else:
                print(f"✗ Rev:{revenue/1e6:.0f}M NI:{net_income/1e6:.0f}M Margin:{profit_margin:.1f}%")
        except Exception as e:
            print(f"? Error")
    
    print()
    print("="*80)
    print(f"FOUND {len(quality)} QUALITY SMALL-CAPS")
    print("="*80)
    print()
    
    if quality:
        quality.sort(key=lambda x: x['ps_ratio'])
        
        for i, c in enumerate(quality, 1):
            print(f"{i}. {c['ticker']:6} {c['company'][:40]:40} ${c['market_cap']/1e6:6.1f}M")
            print(f"   Revenue: ${c['revenue']/1e6:6.1f}M | Margin: {c['profit_margin']:5.1f}% | P/S: {c['ps_ratio']:.2f}x")
            print(f"   Debt/Equity: {c['debt_to_equity']:.1f}%")
            print()
    
    return quality

if __name__ == '__main__':
    screen_smallcaps()
