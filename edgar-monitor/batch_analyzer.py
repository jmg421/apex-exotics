#!/usr/bin/env python3
"""
Batch analyzer - analyze all ENIS companies.
"""

from enis_llm_analyzer import analyze_company_from_enis, save_report, load_all_reports
import json
from pathlib import Path
import time

DATA_DIR = Path(__file__).parent / "data"

def analyze_all_companies():
    """Analyze all companies in ENIS database."""
    # Load all companies from scores.json
    with open(DATA_DIR / "scores.json") as f:
        companies = json.load(f)
    
    # Load existing reports to skip already analyzed
    existing_reports = load_all_reports()
    
    # Filter to only unanalyzed companies with score >= 40
    to_analyze = [c for c in companies 
                  if c.get('score', 0) >= 40 
                  and c.get('cik') not in existing_reports]
    
    # Sort by score descending
    to_analyze.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    print(f"Found {len(to_analyze)} companies to analyze (score >= 40)")
    print()
    
    results = []
    for i, company in enumerate(to_analyze, 1):
        cik = company['cik']
        ticker = company.get('ticker', 'N/A')
        score = company.get('score', 0)
        
        print(f"[{i}/{len(to_analyze)}] {ticker} ({score}/100) - {company.get('company', 'Unknown')[:40]}...")
        
        try:
            result = analyze_company_from_enis(cik)
            save_report(result)
            results.append(result)
            
            # Rate limit - 2 seconds between API calls
            if i < len(to_analyze):
                time.sleep(2)
            
        except Exception as e:
            print(f"  Error: {e}")
            continue
    
    print(f"\n✓ Analyzed {len(results)}/{len(to_analyze)} companies")
    return results

def filter_actionable(results):
    """Filter for actionable recommendations."""
    actionable = []
    
    for r in results:
        # BUY recommendations with medium+ conviction
        if r.get('recommendation') == 'BUY' and r.get('conviction') in ['HIGH', 'MEDIUM']:
            actionable.append(r)
        
        # SHORT candidates (high risk or explicit SHORT recommendation)
        elif r.get('risk_score', 0) >= 7 or r.get('recommendation') == 'SHORT':
            actionable.append(r)
    
    return actionable

if __name__ == "__main__":
    print("="*60)
    print("ENIS Batch Analyzer")
    print("="*60)
    
    # Analyze all companies
    results = analyze_all_companies()
    
    # Filter actionable
    actionable = filter_actionable(results)
    
    print("\n" + "="*60)
    print(f"Actionable Recommendations: {len(actionable)}")
    print("="*60)
    
    for r in actionable:
        print(f"\n{r['ticker']} - {r.get('company', 'Unknown')}")
        print(f"  Type: {r['analysis_type']}")
        print(f"  Recommendation: {r.get('recommendation', 'N/A')}")
        if 'risk_score' in r:
            print(f"  Risk Score: {r['risk_score']}/10")
        if 'conviction' in r:
            print(f"  Conviction: {r['conviction']}")
