#!/usr/bin/env python3
"""
Scoring system - rank micro-cap companies by investment attractiveness.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
FINANCIALS_FILE = DATA_DIR / "financials.json"
MARKET_CAP_FILE = DATA_DIR / "market_caps.json"
SCORES_FILE = DATA_DIR / "scores.json"

def calculate_score(company):
    """Score a company based on key financial metrics."""
    score = 0
    reasons = []
    
    # High net margin (>15% = excellent, >10% = good)
    margin = company.get("net_margin")
    if margin:
        if margin > 15:
            score += 30
            reasons.append(f"High margin: {margin:.1f}%")
        elif margin > 10:
            score += 20
            reasons.append(f"Good margin: {margin:.1f}%")
        elif margin > 5:
            score += 10
    
    # Low debt-to-assets (<30% = excellent, <50% = good)
    debt_ratio = company.get("debt_to_assets")
    if debt_ratio is not None:
        if debt_ratio < 30:
            score += 25
            reasons.append(f"Low debt: {debt_ratio:.1f}%")
        elif debt_ratio < 50:
            score += 15
            reasons.append(f"Moderate debt: {debt_ratio:.1f}%")
    
    # Strong cash position (cash > 20% of assets)
    cash = company.get("cash")
    assets = company.get("total_assets")
    if cash and assets:
        cash_ratio = (cash / assets) * 100
        if cash_ratio > 20:
            score += 20
            reasons.append(f"Strong cash: {cash_ratio:.1f}% of assets")
        elif cash_ratio > 10:
            score += 10
    
    # Profitable (net income > 0)
    net_income = company.get("net_income")
    if net_income and net_income > 0:
        score += 15
        reasons.append("Profitable")
    
    # Revenue scale (prefer >$10M annual revenue)
    revenue = company.get("revenue")
    if revenue:
        if revenue > 50_000_000:
            score += 10
            reasons.append(f"Revenue: ${revenue/1e6:.1f}M")
        elif revenue > 10_000_000:
            score += 5
    
    return score, reasons

def score_companies():
    """Score all companies and rank by attractiveness."""
    financials = json.load(open(FINANCIALS_FILE))
    market_caps = json.load(open(MARKET_CAP_FILE))
    
    scored = []
    
    for cik, company in financials.items():
        score, reasons = calculate_score(company)
        
        # Get market cap
        cap_data = market_caps.get(cik, {})
        market_cap = cap_data.get("market_cap")
        ticker = cap_data.get("ticker")
        
        scored.append({
            "cik": cik,
            "company": company["company"],
            "ticker": ticker,
            "market_cap": market_cap,
            "score": score,
            "reasons": reasons,
            "metrics": {
                "revenue": company.get("revenue"),
                "net_margin": company.get("net_margin"),
                "debt_to_assets": company.get("debt_to_assets"),
                "cash": company.get("cash"),
                "net_income": company.get("net_income")
            }
        })
    
    # Sort by score (highest first)
    scored.sort(key=lambda x: x["score"], reverse=True)
    
    # Save results
    with open(SCORES_FILE, "w") as f:
        json.dump(scored, f, indent=2)
    
    # Display top opportunities
    print(f"\n{'='*80}")
    print("TOP MICRO-CAP OPPORTUNITIES")
    print(f"{'='*80}\n")
    
    for i, company in enumerate(scored[:10], 1):
        print(f"{i}. {company['company']} ({company.get('ticker', 'N/A')})")
        print(f"   Score: {company['score']}/100")
        print(f"   Market Cap: ${company.get('market_cap', 0):,}")
        
        metrics = company['metrics']
        if metrics.get('revenue'):
            print(f"   Revenue: ${metrics['revenue']/1e6:.1f}M")
        if metrics.get('net_margin'):
            print(f"   Net Margin: {metrics['net_margin']:.1f}%")
        if metrics.get('debt_to_assets') is not None:
            print(f"   Debt/Assets: {metrics['debt_to_assets']:.1f}%")
        
        if company['reasons']:
            print(f"   Why: {', '.join(company['reasons'])}")
        print()
    
    print(f"✓ Scored {len(scored)} companies")
    print(f"✓ Results saved to {SCORES_FILE}")
    
    return scored

if __name__ == "__main__":
    score_companies()
