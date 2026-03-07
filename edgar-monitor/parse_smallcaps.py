#!/usr/bin/env python3
"""Parse financials for small-cap companies ($100M-$2B)."""

import json
from pathlib import Path
from financials import parse_company_financials, save_financials

DATA_DIR = Path(__file__).parent / "data"

def parse_smallcap_financials():
    """Parse financials for companies in $100M-$2B range."""
    
    # Load market caps
    with open(DATA_DIR / "market_caps.json") as f:
        caps = json.load(f)
    
    # Load filings
    with open(DATA_DIR / "filings.json") as f:
        filings = json.load(f)
    
    # Load existing financials
    try:
        with open(DATA_DIR / "financials.json") as f:
            existing_fins = json.load(f)
    except FileNotFoundError:
        existing_fins = {}
    
    # Find small-caps without financials
    to_parse = []
    for cik, cap_data in caps.items():
        cap = cap_data.get('market_cap')
        
        # Filter: $100M - $2B, not already parsed
        if cap and 100_000_000 <= cap <= 2_000_000_000 and cik not in existing_fins:
            # Find company name
            for filing in filings.values():
                if filing.get('cik') == cik:
                    to_parse.append({
                        'cik': cik,
                        'company': filing.get('company'),
                        'ticker': cap_data.get('ticker'),
                        'market_cap': cap
                    })
                    break
    
    print(f"Found {len(to_parse)} small-caps to parse")
    print(f"Parsing first 30 to avoid rate limits...")
    print()
    
    parsed = 0
    for i, company in enumerate(to_parse[:30], 1):
        cik = company['cik']
        name = company['company']
        ticker = company['ticker'] or 'N/A'
        
        print(f"[{i}/30] {name} ({ticker})...", end=" ")
        
        try:
            fin_data = parse_company_financials(cik, name)
            if fin_data:
                existing_fins[cik] = fin_data
                parsed += 1
                
                rev = fin_data.get('revenue', 0)
                margin = fin_data.get('net_margin', 0)
                print(f"✓ Rev: ${rev/1e6:.1f}M, Margin: {margin:.1f}%")
            else:
                print("? No data")
        except Exception as e:
            print(f"✗ {e}")
    
    # Save
    save_financials(existing_fins)
    print(f"\n✓ Parsed {parsed}/30 companies")

if __name__ == '__main__':
    parse_smallcap_financials()
