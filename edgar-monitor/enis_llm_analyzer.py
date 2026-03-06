#!/usr/bin/env python3
"""
ENIS + LLM integration - connects ENIS screening with LLM analysis.
"""

from goldman_analyzer import goldman_analysis
from bridgewater_analyzer import bridgewater_risk_analysis
import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent / "data"
REPORTS_FILE = DATA_DIR / "llm_reports.json"

def load_company_data(cik):
    """Load company data from ENIS databases."""
    # Load from enis_scores.json
    with open(DATA_DIR / "enis_scores.json") as f:
        scores = json.load(f)
    
    company = next((c for c in scores if c['cik'] == cik), None)
    if not company:
        raise ValueError(f"Company {cik} not found in ENIS database")
    
    # Load concentration data from relationships
    try:
        with open(DATA_DIR / "relationships.json") as f:
            relationships = json.load(f)
        
        if cik in relationships:
            rels = relationships[cik]['relationships']
            conc_list = rels.get('customer_concentration', [])
            company['concentration'] = max(conc_list) if conc_list else 0
        else:
            company['concentration'] = 0
    except FileNotFoundError:
        company['concentration'] = 0
    
    return company

def analyze_company_from_enis(cik):
    """Analyze company from ENIS database using LLM."""
    
    # Load company data
    company = load_company_data(cik)
    
    # Determine analysis type based on ENIS metrics
    financial_score = company.get('financial_score', 0)
    concentration = company.get('concentration', 0)
    
    if concentration >= 40:
        # High concentration = risk analysis (Bridgewater)
        result = bridgewater_risk_analysis(company)
        result['analysis_type'] = 'bridgewater_risk'
        
    elif financial_score >= 40:
        # Decent financial score = fundamental analysis (Goldman)
        result = goldman_analysis(company)
        result['analysis_type'] = 'goldman_sachs'
        
    else:
        # Low score = quick summary
        result = quick_summary(company)
        result['analysis_type'] = 'quick_summary'
    
    result['cik'] = cik
    result['enis_score'] = company.get('enis_score', 0)
    result['financial_score'] = financial_score
    
    return result

def quick_summary(company_data):
    """Generate quick summary for low-score companies."""
    return {
        'ticker': company_data['ticker'],
        'company': company_data.get('company', 'Unknown'),
        'recommendation': 'PASS',
        'conviction': 'LOW',
        'analysis_date': datetime.now().isoformat(),
        'summary': f"Low ENIS score ({company_data.get('enis_score', 0)}/100). Not actionable."
    }

def save_report(report):
    """Save LLM analysis report."""
    reports = load_all_reports()
    reports[report['cik']] = report
    
    DATA_DIR.mkdir(exist_ok=True)
    with open(REPORTS_FILE, 'w') as f:
        json.dump(reports, f, indent=2)

def load_all_reports():
    """Load all saved reports."""
    if not REPORTS_FILE.exists():
        return {}
    
    with open(REPORTS_FILE) as f:
        return json.load(f)

def load_report(cik):
    """Load specific company report."""
    reports = load_all_reports()
    return reports.get(cik)

if __name__ == "__main__":
    # Test with AFCG
    print("Analyzing AFCG from ENIS database...")
    result = analyze_company_from_enis('0001822523')
    
    print("\n" + "="*60)
    print(f"ENIS + LLM Analysis: {result['ticker']}")
    print("="*60)
    print(f"ENIS Score: {result['enis_score']}/100")
    print(f"Analysis Type: {result['analysis_type']}")
    print(f"Recommendation: {result['recommendation']}")
    
    # Save report
    save_report(result)
    print(f"\n✓ Report saved to {REPORTS_FILE}")
