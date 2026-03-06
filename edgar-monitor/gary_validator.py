#!/usr/bin/env python3
"""
Gary's Validation Checklist - Automated
Checks the key red flags an experienced trader would look for.
"""

import json
import re
from pathlib import Path

def load_company_10k(cik):
    """Load parsed 10-K data for a company."""
    # TODO: Implement 10-K text extraction
    # For now, return mock data
    return {
        'cik': cik,
        'text': '',
        'sections': {}
    }

def check_going_concern(text):
    """Check for going concern warnings in audit opinion."""
    patterns = [
        r'substantial doubt.*ability to continue as a going concern',
        r'going concern.*substantial doubt',
        r'may not be able to continue.*going concern'
    ]
    
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return {
                'flag': 'GOING_CONCERN',
                'severity': 'CRITICAL',
                'message': 'Auditor expressed substantial doubt about going concern'
            }
    
    return None

def check_cash_runway(financials):
    """Calculate cash runway in quarters."""
    cash = financials.get('cash', 0)
    net_income = financials.get('net_income', 0)
    
    # Estimate quarterly burn (if losing money)
    if net_income < 0:
        quarterly_burn = abs(net_income) / 4
        if quarterly_burn > 0:
            runway_quarters = cash / quarterly_burn
            
            if runway_quarters < 4:
                return {
                    'flag': 'LOW_CASH_RUNWAY',
                    'severity': 'HIGH',
                    'message': f'Only {runway_quarters:.1f} quarters of cash remaining',
                    'quarters': runway_quarters
                }
    
    return None

def check_death_spiral_debt(text):
    """Check for toxic convertible debt."""
    toxic_lenders = [
        'anson', 'lg capital', 'auctus', 'power up', 'st cloud',
        'labrys', 'cavalry', 'hudson bay', 'armistice'
    ]
    
    for lender in toxic_lenders:
        if lender in text.lower():
            return {
                'flag': 'TOXIC_LENDER',
                'severity': 'CRITICAL',
                'message': f'Toxic lender detected: {lender.title()}',
                'lender': lender
            }
    
    # Check for death spiral language
    if re.search(r'conversion.*discount to.*market', text, re.IGNORECASE):
        return {
            'flag': 'DEATH_SPIRAL_TERMS',
            'severity': 'HIGH',
            'message': 'Convertible debt with discount-to-market conversion'
        }
    
    return None

def validate_company(cik, financials):
    """Run Gary's validation checklist on a company."""
    print(f"\nValidating CIK {cik}...")
    print("="*60)
    
    # Load 10-K
    doc = load_company_10k(cik)
    text = doc.get('text', '')
    
    flags = []
    
    # Check 1: Going concern
    flag = check_going_concern(text)
    if flag:
        flags.append(flag)
        print(f"❌ {flag['message']}")
    else:
        print("✓ No going concern warning")
    
    # Check 2: Cash runway
    flag = check_cash_runway(financials)
    if flag:
        flags.append(flag)
        print(f"⚠️  {flag['message']}")
    else:
        print("✓ Adequate cash runway")
    
    # Check 3: Death spiral debt
    flag = check_death_spiral_debt(text)
    if flag:
        flags.append(flag)
        print(f"❌ {flag['message']}")
    else:
        print("✓ No toxic debt detected")
    
    # Summary
    critical = [f for f in flags if f['severity'] == 'CRITICAL']
    high = [f for f in flags if f['severity'] == 'HIGH']
    
    print()
    if critical:
        print(f"🚫 REJECT: {len(critical)} critical issues")
        return 'REJECT', flags
    elif high:
        print(f"⚠️  CAUTION: {len(high)} high-severity issues")
        return 'CAUTION', flags
    else:
        print("✅ PASS: No major red flags")
        return 'PASS', flags

if __name__ == '__main__':
    # Test with our 3 alpha ideas
    ideas = [
        ('0001805651', 'MKTW'),  # MarketWise
        ('0000829323', 'INUV'),  # Inuvo
        ('0001822523', 'AFCG'),  # Advanced Flower Capital
    ]
    
    # Load financials
    with open('data/financials.json') as f:
        financials_db = json.load(f)
    
    print("Gary's Validation Checklist")
    print("="*60)
    
    for cik, ticker in ideas:
        financials = financials_db.get(cik, {})
        result, flags = validate_company(cik, financials)
        print(f"\n{ticker}: {result}")
        print()
