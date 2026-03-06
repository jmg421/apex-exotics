#!/usr/bin/env python3
"""Revenue quality checker - detects channel stuffing and accounting games."""

import json

def check_revenue_quality(ticker, financials):
    """Check revenue quality metrics."""
    flags = []
    
    # Get current year data
    current = financials.get('current_year', {})
    prior = financials.get('prior_year', {})
    
    revenue = current.get('revenue', 0)
    ocf = current.get('operating_cash_flow', 0)
    net_income = current.get('net_income', 0)
    ar = current.get('accounts_receivable', 0)
    
    prior_revenue = prior.get('revenue', 0)
    prior_ar = prior.get('accounts_receivable', 0)
    
    # 1. OCF vs Net Income (should be close for quality earnings)
    if net_income > 0:
        ocf_ratio = ocf / net_income
        if ocf_ratio < 0.8:
            flags.append(f"⚠️ Low cash conversion: OCF/NI = {ocf_ratio:.2f} (expect >0.8)")
    
    # 2. DSO Trend (Days Sales Outstanding)
    if revenue > 0 and prior_revenue > 0:
        dso = (ar / revenue) * 365
        prior_dso = (prior_ar / prior_revenue) * 365
        dso_change = dso - prior_dso
        
        if dso_change > 10:
            flags.append(f"⚠️ DSO increasing: {prior_dso:.0f} → {dso:.0f} days (+{dso_change:.0f})")
    
    # 3. AR Growth vs Revenue Growth
    if prior_revenue > 0 and prior_ar > 0:
        rev_growth = (revenue - prior_revenue) / prior_revenue
        ar_growth = (ar - prior_ar) / prior_ar
        
        if ar_growth > rev_growth * 1.2 and rev_growth > 0:
            flags.append(f"⚠️ AR growing faster than revenue: AR +{ar_growth*100:.0f}% vs Rev +{rev_growth*100:.0f}%")
    
    return {
        'ticker': ticker,
        'quality_score': 'PASS' if len(flags) == 0 else 'FAIL',
        'flags': flags,
        'metrics': {
            'ocf_ni_ratio': round(ocf / net_income, 2) if net_income > 0 else None,
            'dso': round((ar / revenue) * 365, 0) if revenue > 0 else None,
            'revenue_growth': round((revenue - prior_revenue) / prior_revenue * 100, 1) if prior_revenue > 0 else None
        }
    }

if __name__ == '__main__':
    # Load financials
    with open('data/financials.json') as f:
        data = json.load(f)
    
    # Check our 3 alpha ideas
    targets = ['MKTW', 'INUV', 'AFCG']
    
    print("Revenue Quality Check")
    print("=" * 60)
    
    for ticker in targets:
        if ticker in data:
            result = check_revenue_quality(ticker, data[ticker])
            print(f"\n{ticker}: {result['quality_score']}")
            
            if result['flags']:
                for flag in result['flags']:
                    print(f"  {flag}")
            else:
                print("  ✓ No red flags")
            
            print(f"  Metrics: {result['metrics']}")
        else:
            print(f"\n{ticker}: No data")
