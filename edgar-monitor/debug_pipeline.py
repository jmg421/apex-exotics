#!/usr/bin/env python3
"""Debug script to show pipeline status."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def show_status():
    print("="*70)
    print("ENIS Pipeline Status")
    print("="*70)
    print()
    
    # Filings
    filings_file = DATA_DIR / "filings.json"
    if filings_file.exists():
        filings = json.load(open(filings_file))
        print(f"📄 Filings Database: {len(filings)} companies")
        
        # Show breakdown by type
        types = {}
        for filing in filings.values():
            ftype = filing.get('filing_type', 'unknown')
            types[ftype] = types.get(ftype, 0) + 1
        for ftype, count in sorted(types.items()):
            print(f"   • {ftype}: {count}")
        print()
    
    # Market caps
    caps_file = DATA_DIR / "market_caps.json"
    if caps_file.exists():
        caps = json.load(open(caps_file))
        print(f"💰 Market Caps Checked: {len(caps)} companies")
        
        # Count micro-caps
        micro_caps = [c for c in caps.values() if c.get('market_cap') and c['market_cap'] < 100_000_000]
        print(f"   • Micro-caps (<$100M): {len(micro_caps)}")
        
        # Count checked but no data
        no_data = [c for c in caps.values() if not c.get('market_cap')]
        print(f"   • No market cap data: {len(no_data)}")
        print()
    
    # Financials
    fin_file = DATA_DIR / "financials.json"
    if fin_file.exists():
        fins = json.load(open(fin_file))
        print(f"📊 Financials Parsed: {len(fins)} companies")
        
        # Count with revenue
        with_revenue = [f for f in fins.values() if (f.get('revenue') or 0) > 0]
        print(f"   • With revenue: {len(with_revenue)}")
        
        # Count profitable
        profitable = [f for f in fins.values() if (f.get('net_income') or 0) > 0]
        print(f"   • Profitable: {len(profitable)}")
        print()
    
    # Scores
    scores_file = DATA_DIR / "scores.json"
    if scores_file.exists():
        scores = json.load(open(scores_file))
        print(f"⭐ ENIS Scores: {len(scores)} companies")
        
        # Show top 5
        if isinstance(scores, dict):
            sorted_scores = sorted(scores.items(), key=lambda x: x[1].get('score', 0), reverse=True)
            print(f"   Top 5:")
            for cik, data in sorted_scores[:5]:
                ticker = data.get('ticker', 'N/A')
                score = data.get('score', 0)
                company = data.get('company', 'Unknown')[:40]
                print(f"   • {ticker:6} {score:3}/100 - {company}")
        else:
            # List format
            sorted_scores = sorted(scores, key=lambda x: x.get('score', 0), reverse=True)
            print(f"   Top 5:")
            for data in sorted_scores[:5]:
                ticker = data.get('ticker', 'N/A')
                score = data.get('score', 0)
                company = data.get('company', 'Unknown')[:40]
                print(f"   • {ticker:6} {score:3}/100 - {company}")
        print()
    
    # LLM reports
    llm_file = DATA_DIR / "llm_reports.json"
    if llm_file.exists():
        reports = json.load(open(llm_file))
        print(f"🤖 LLM Analysis: {len(reports)} companies")
        
        # Count by recommendation
        recs = {}
        for report in reports.values():
            rec = report.get('recommendation', 'unknown')
            recs[rec] = recs.get(rec, 0) + 1
        for rec, count in sorted(recs.items()):
            print(f"   • {rec}: {count}")
        print()
    
    print("="*70)
    print()
    print("Next steps:")
    print("  • Need more market cap data? Add ALPHA_VANTAGE_API_KEY to .env")
    print("  • Run full pipeline: ./run_enis.sh")
    print("  • Analyze top scorers: python batch_analyzer.py")

if __name__ == '__main__':
    show_status()
