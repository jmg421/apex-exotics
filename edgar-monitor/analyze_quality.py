#!/usr/bin/env python3
"""Analyze quality small-caps found by screener."""

import json
from pathlib import Path
from goldman_analyzer import goldman_analysis
import time

DATA_DIR = Path(__file__).parent / "data"

# Quality companies from screen
QUALITY_COMPANIES = [
    {'ticker': 'TASK', 'company': 'TaskUs, Inc.', 'market_cap': 1017200000, 'revenue': 1183500000, 'margin': 8.6, 'ps': 0.86},
    {'ticker': 'CNDHF', 'company': 'CONDUIT HOLDINGS LTD', 'market_cap': 628900000, 'revenue': 820300000, 'margin': 14.2, 'ps': 0.77},
    {'ticker': 'GRNT', 'company': 'Granite Ridge Resources, Inc.', 'market_cap': 666100000, 'revenue': 427900000, 'margin': 5.7, 'ps': 1.56},
    {'ticker': 'PLPC', 'company': 'PREFORMED LINE PRODUCTS CO', 'market_cap': 1209600000, 'revenue': 669300000, 'margin': 5.3, 'ps': 1.81},
    {'ticker': 'FMNB', 'company': 'FARMERS NATIONAL BANC CORP', 'market_cap': 464100000, 'revenue': 181500000, 'margin': 30.1, 'ps': 2.56},
    {'ticker': 'SPFI', 'company': 'SOUTH PLAINS FINANCIAL, INC.', 'market_cap': 657800000, 'revenue': 206700000, 'margin': 28.3, 'ps': 3.18},
    {'ticker': 'IBCP', 'company': 'INDEPENDENT BANK CORP', 'market_cap': 700600000, 'revenue': 219500000, 'margin': 31.2, 'ps': 3.19},
    {'ticker': 'SD', 'company': 'SANDRIDGE ENERGY INC', 'market_cap': 650300000, 'revenue': 156400000, 'margin': 44.9, 'ps': 4.16},
    {'ticker': 'TOETF', 'company': 'TOSEI CORP', 'market_cap': 1097200000, 'revenue': 94688000000, 'margin': 15.6, 'ps': 0.01},
]

def analyze_quality_companies():
    """Analyze quality small-caps using Goldman-style analysis."""
    
    print("="*80)
    print("ANALYZING 9 QUALITY SMALL-CAPS")
    print("="*80)
    print()
    
    results = []
    
    for i, company in enumerate(QUALITY_COMPANIES, 1):
        ticker = company['ticker']
        name = company['company']
        
        print(f"[{i}/9] {ticker:6} {name[:40]:40}...")
        
        # Build company data for analyzer
        company_data = {
            'ticker': ticker,
            'company': name,
            'market_cap': company['market_cap'],
            'metrics': {
                'revenue': company['revenue'],
                'net_margin': company['margin'],
                'debt_to_assets': 0,  # Not available from quick screen
                'cash': 0,
                'net_income': company['revenue'] * company['margin'] / 100
            },
            'enis_score': 70.0,  # Assume decent quality
            'financial_score': 70
        }
        
        try:
            result = goldman_analysis(company_data)
            result['ticker'] = ticker
            result['company'] = name
            result['market_cap'] = company['market_cap']
            result['ps_ratio'] = company['ps']
            
            rec = result.get('recommendation', 'N/A')
            conv = result.get('conviction', 'N/A')
            print(f"  ✓ {rec} / {conv}")
            
            results.append(result)
            
            if i < len(QUALITY_COMPANIES):
                time.sleep(2)
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Save results
    output_file = DATA_DIR / "quality_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print()
    print(f"✓ Analyzed {len(results)}/9 companies")
    print(f"✓ Saved to {output_file}")
    print()
    
    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    
    buys = [r for r in results if r.get('recommendation') == 'BUY']
    holds = [r for r in results if r.get('recommendation') == 'HOLD']
    avoids = [r for r in results if r.get('recommendation') == 'AVOID']
    
    print(f"BUY:   {len(buys)}")
    print(f"HOLD:  {len(holds)}")
    print(f"AVOID: {len(avoids)}")
    print()
    
    if buys:
        print("🟢 BUY Recommendations:")
        for r in buys:
            print(f"  • {r['ticker']:6} {r['company'][:40]:40} P/S: {r['ps_ratio']:.2f}x")
    
    return results

if __name__ == '__main__':
    analyze_quality_companies()
