#!/usr/bin/env python3
"""Sync scores.json to enis_scores.json format for LLM analysis."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def sync_scores():
    """Convert scores.json to enis_scores.json format."""
    # Load scores
    with open(DATA_DIR / "scores.json") as f:
        scores = json.load(f)
    
    # Load financials for additional data
    with open(DATA_DIR / "financials.json") as f:
        financials = json.load(f)
    
    enis_scores = []
    
    for company in scores:
        cik = company['cik']
        
        # Get financial data
        fin = financials.get(cik, {})
        
        # Build ENIS format
        enis_company = {
            "cik": cik,
            "company": company.get('company', 'Unknown'),
            "ticker": company.get('ticker', 'N/A'),
            "market_cap": company.get('market_cap', 0),
            "score": company.get('score', 0),
            "reasons": company.get('reasons', []),
            "metrics": {
                "revenue": fin.get('revenue'),
                "net_margin": fin.get('net_margin'),
                "debt_to_assets": fin.get('debt_to_assets'),
                "cash": fin.get('cash'),
                "net_income": fin.get('net_income')
            },
            "financial_score": company.get('score', 0),  # Use score as financial_score
            "network_metrics": {
                "systemic_importance": 0.0,
                "contagion_risk": 0.0,
                "network_value": 0,
                "variance": 0.0
            },
            "mgf": {
                "G0": 1.0,
                "G1": 0.0,
                "G2": 0.0
            },
            "enis_score": company.get('score', 0) * 0.6  # Approximate ENIS score
        }
        
        enis_scores.append(enis_company)
    
    # Save
    with open(DATA_DIR / "enis_scores.json", 'w') as f:
        json.dump(enis_scores, f, indent=2)
    
    print(f"✓ Synced {len(enis_scores)} companies to enis_scores.json")
    return enis_scores

if __name__ == '__main__':
    sync_scores()
