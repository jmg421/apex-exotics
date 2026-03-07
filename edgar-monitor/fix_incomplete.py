#!/usr/bin/env python3
"""Re-analyze companies with incomplete reports."""

from enis_llm_analyzer import analyze_company_from_enis, save_report
import json
from pathlib import Path
import time

DATA_DIR = Path(__file__).parent / "data"

def fix_incomplete_reports():
    """Re-analyze companies with null/incomplete recommendations."""
    # Load reports
    with open(DATA_DIR / "llm_reports.json") as f:
        reports = json.load(f)
    
    # Find incomplete
    incomplete = []
    for cik, report in reports.items():
        if not report or not isinstance(report, dict) or not report.get('recommendation'):
            incomplete.append(cik)
    
    print(f"Found {len(incomplete)} incomplete reports")
    print()
    
    for i, cik in enumerate(incomplete, 1):
        print(f"[{i}/{len(incomplete)}] Re-analyzing {cik}...")
        
        try:
            result = analyze_company_from_enis(cik)
            save_report(result)
            print(f"  ✓ {result.get('recommendation', 'N/A')}")
            
            if i < len(incomplete):
                time.sleep(2)
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\n✓ Complete")

if __name__ == '__main__':
    fix_incomplete_reports()
