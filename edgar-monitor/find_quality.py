#!/usr/bin/env python3
"""Find quality small-caps: $100M-$2B market cap with actual businesses."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def find_quality_smallcaps():
    """Look for companies with $100M-$2B cap that have revenue and profitability."""
    
    # Load market caps
    with open(DATA_DIR / "market_caps.json") as f:
        caps = json.load(f)
    
    # Load financials
    with open(DATA_DIR / "financials.json") as f:
        fins = json.load(f)
    
    # Load filings for company names
    with open(DATA_DIR / "filings.json") as f:
        filings = json.load(f)
    
    quality_candidates = []
    
    for cik, cap_data in caps.items():
        cap = cap_data.get('market_cap')
        ticker = cap_data.get('ticker')
        
        # Filter: $100M - $2B market cap
        if not cap or cap < 100_000_000 or cap > 2_000_000_000:
            continue
        
        # Get financials
        fin = fins.get(cik, {})
        revenue = fin.get('revenue') or 0
        net_income = fin.get('net_income') or 0
        net_margin = fin.get('net_margin') or 0
        debt_to_assets = fin.get('debt_to_assets') or 0
        
        # Quality filters:
        # 1. Has revenue (actual business)
        # 2. Profitable (net income > 0)
        # 3. Reasonable debt (<50%)
        # 4. Decent margin (>5%)
        
        if revenue > 10_000_000 and net_income > 0 and debt_to_assets < 50 and net_margin > 5:
            # Find company name
            company_name = None
            for filing in filings.values():
                if filing.get('cik') == cik:
                    company_name = filing.get('company')
                    break
            
            quality_candidates.append({
                'cik': cik,
                'ticker': ticker,
                'company': company_name,
                'market_cap': cap,
                'revenue': revenue,
                'net_income': net_income,
                'net_margin': net_margin,
                'debt_to_assets': debt_to_assets,
                'ps_ratio': cap / revenue if revenue else 0
            })
    
    # Sort by P/S ratio (cheapest first)
    quality_candidates.sort(key=lambda x: x['ps_ratio'])
    
    print("="*80)
    print("QUALITY SMALL-CAPS: $100M-$2B Market Cap")
    print("Filters: Revenue >$10M, Profitable, Debt <50%, Margin >5%")
    print("="*80)
    print()
    
    if not quality_candidates:
        print("❌ No quality small-caps found in current dataset")
        print()
        print("Suggestions:")
        print("  1. Expand market cap range (currently checking 408 companies)")
        print("  2. Relax quality filters")
        print("  3. Scrape more companies from SEC")
        return []
    
    print(f"Found {len(quality_candidates)} quality candidates:")
    print()
    
    for i, c in enumerate(quality_candidates[:20], 1):
        ticker = c['ticker'] or 'N/A'
        company = (c['company'] or 'Unknown')[:40]
        cap = c['market_cap']
        rev = c['revenue']
        margin = c['net_margin']
        ps = c['ps_ratio']
        
        print(f"{i:2}. {ticker:6} {company:40} ${cap/1e6:6.1f}M")
        print(f"    Revenue: ${rev/1e6:6.1f}M | Margin: {margin:5.1f}% | P/S: {ps:.2f}x")
        print()
    
    return quality_candidates

if __name__ == '__main__':
    find_quality_smallcaps()
