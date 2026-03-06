#!/usr/bin/env python3
"""
Goldman Sachs-style fundamental analyzer.
"""

from llm_client import call_llm, format_goldman_prompt, parse_recommendation
from datetime import datetime
import re

def goldman_analysis(company_data):
    """Run Goldman Sachs-style fundamental analysis."""
    
    # Format prompt with more detail
    metrics = company_data.get('metrics', {})
    revenue = metrics.get('revenue') or 0
    net_margin = metrics.get('net_margin') or 0
    debt_to_assets = metrics.get('debt_to_assets') or 0
    cash = metrics.get('cash') or 0
    net_income = metrics.get('net_income') or 0
    
    prompt = f"""You are a senior equity research analyst at Goldman Sachs with 20 years of experience.

Analyze this micro-cap company for institutional investors:

**Company:** {company_data.get('company', 'Unknown')}
**Ticker:** {company_data['ticker']}
**Market Cap:** ${company_data['market_cap']:,.0f}
**ENIS Score:** {company_data.get('enis_score', 0)}/100

**Financials:**
- Revenue: ${revenue:,.0f}
- Net Margin: {net_margin:.1f}%
- Debt/Assets: {debt_to_assets:.1f}%
- Cash: ${cash:,.0f}
- Net Income: ${net_income:,.0f}

Provide a concise research note with:

1. **Business Assessment** (2-3 sentences)
2. **Financial Health** (rate 1-10)
3. **Key Risks** (3-5 bullet points starting with -)
4. **Key Opportunities** (3-5 bullet points starting with -)
5. **Recommendation:** BUY, HOLD, or AVOID
6. **Conviction:** HIGH, MEDIUM, or LOW
7. **12-Month Price Target:** $X.XX

Format clearly with section headers."""
    
    # Call LLM
    print(f"Analyzing {company_data['ticker']}...")
    response = call_llm(prompt)
    
    # Parse response
    result = parse_recommendation(response)
    
    # Extract additional fields
    result['key_risks'] = extract_risks(response)
    result['key_opportunities'] = extract_opportunities(response)
    result['ticker'] = company_data['ticker']
    result['company'] = company_data.get('company', 'Unknown')
    result['market_cap'] = company_data['market_cap']
    result['enis_score'] = company_data.get('enis_score', 0)
    result['analysis_date'] = datetime.now().isoformat()
    result['full_analysis'] = response
    
    return result

def extract_risks(text):
    """Extract risk factors from analysis."""
    risks = []
    
    # Look for risk section
    risk_section = re.search(r'(?:Key\s+)?Risk[s]?:?(.*?)(?:Opportunit|Recommendation|$)', 
                            text, re.DOTALL | re.IGNORECASE)
    
    if risk_section:
        # Extract bullet points
        bullets = re.findall(r'[-•*]\s*(.+?)(?=\n|$)', risk_section.group(1))
        risks = [b.strip() for b in bullets if len(b.strip()) > 10]
    
    return risks[:5]  # Top 5 risks

def extract_opportunities(text):
    """Extract opportunities from analysis."""
    opps = []
    
    # Look for opportunities section
    opp_section = re.search(r'(?:Key\s+)?Opportunit(?:y|ies):?(.*?)(?:Risk|Recommendation|$)', 
                           text, re.DOTALL | re.IGNORECASE)
    
    if opp_section:
        # Extract bullet points
        bullets = re.findall(r'[-•*]\s*(.+?)(?=\n|$)', opp_section.group(1))
        opps = [b.strip() for b in bullets if len(b.strip()) > 10]
    
    return opps[:5]  # Top 5 opportunities

if __name__ == "__main__":
    # Quick test
    import json
    from pathlib import Path
    
    DATA_DIR = Path(__file__).parent / "data"
    
    with open(DATA_DIR / "enis_scores.json") as f:
        companies = json.load(f)
    
    # Test with AFCG
    afcg = next(c for c in companies if c.get('ticker') == 'AFCG')
    result = goldman_analysis(afcg)
    
    print("\n" + "="*60)
    print(f"Goldman Sachs Analysis: {result['ticker']}")
    print("="*60)
    print(f"Recommendation: {result['recommendation']} ({result['conviction']} conviction)")
    print(f"Price Target: ${result.get('price_target', 'N/A')}")
    print(f"\nRisks:")
    for r in result['key_risks']:
        print(f"  - {r}")
    print(f"\nOpportunities:")
    for o in result['key_opportunities']:
        print(f"  - {o}")
