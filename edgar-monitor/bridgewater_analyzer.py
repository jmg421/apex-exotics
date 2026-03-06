#!/usr/bin/env python3
"""
Bridgewater-style risk analyzer for customer concentration.
"""

from llm_client import call_llm
from datetime import datetime
import re

def bridgewater_risk_analysis(company_data):
    """Run Bridgewater-style risk assessment."""
    
    prompt = f"""You are a senior portfolio risk analyst at Bridgewater Associates trained in Ray Dalio's All Weather principles.

Assess the risk profile of this company:

**Company:** {company_data.get('company', 'Unknown')}
**Ticker:** {company_data['ticker']}
**Customer Concentration:** {company_data['concentration']}% from top customers
**Market Cap:** ${company_data['market_cap']:,.0f}
**Debt/Assets:** {company_data.get('debt_to_assets', 0):.1f}%

Focus on:
1. **Revenue Fragility:** What happens if they lose their largest customer?
2. **Risk Score:** Rate 1-10 (where 10 = extreme risk)
3. **Price Decline Scenario:** Estimated % drop if largest customer leaves
4. **Recommendation:** AVOID, HEDGE, or SHORT
5. **Hedging Strategy:** Specific options or position recommendations

Format as Bridgewater risk memo with clear sections."""
    
    print(f"Analyzing risk for {company_data['ticker']}...")
    response = call_llm(prompt)
    
    # Parse response
    result = parse_risk_assessment(response)
    result['ticker'] = company_data['ticker']
    result['company'] = company_data.get('company', 'Unknown')
    result['concentration'] = company_data['concentration']
    result['analysis_date'] = datetime.now().isoformat()
    result['full_analysis'] = response
    
    return result


def parse_risk_assessment(response):
    """Extract risk metrics from response."""
    
    # Extract risk score - try multiple patterns
    risk_match = re.search(r'Risk\s+Score:?\s*[*]*\s*(\d+(?:\.\d+)?)', response, re.IGNORECASE)
    if not risk_match:
        # Try format like "9.0/10"
        risk_match = re.search(r'(\d+(?:\.\d+)?)/10', response)
    
    risk_score = float(risk_match.group(1)) if risk_match else None
    if risk_score:
        risk_score = int(round(risk_score))
    
    # Extract recommendation - try multiple patterns
    rec_match = re.search(r'RECOMMENDATION:?\s*[*]*\s*(AVOID|HEDGE|SHORT)', response, re.IGNORECASE)
    if not rec_match:
        # Try standalone
        rec_match = re.search(r'\b(AVOID|HEDGE|SHORT)\b', response, re.IGNORECASE)
    
    recommendation = rec_match.group(1).upper() if rec_match else None
    
    # Extract price decline estimate
    decline_match = re.search(r'(\d+)[-–](\d+)%\s+(?:drop|decline|fall)', response, re.IGNORECASE)
    if decline_match:
        # Take the midpoint of range
        estimated_decline = (int(decline_match.group(1)) + int(decline_match.group(2))) // 2
    else:
        decline_match = re.search(r'(\d+)%\s+(?:drop|decline|fall)', response, re.IGNORECASE)
        estimated_decline = int(decline_match.group(1)) if decline_match else None
    
    return {
        'risk_score': risk_score,
        'recommendation': recommendation,
        'estimated_decline': estimated_decline
    }

if __name__ == "__main__":
    # Quick test
    test_company = {
        'ticker': 'TASK',
        'company': 'TaskUs, Inc.',
        'concentration': 87,
        'market_cap': 100000000,
        'debt_to_assets': 30
    }
    
    result = bridgewater_risk_analysis(test_company)
    
    print("\n" + "="*60)
    print(f"Bridgewater Risk Analysis: {result['ticker']}")
    print("="*60)
    print(f"Concentration: {result['concentration']}%")
    print(f"Risk Score: {result['risk_score']}/10")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Estimated Decline: {result.get('estimated_decline', 'N/A')}%")
