#!/usr/bin/env python3
"""
Alert system - notify when high-score micro-cap companies file.
"""

import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent / "data"
SCORES_FILE = DATA_DIR / "scores.json"
ALERTS_FILE = DATA_DIR / "alerts.json"

MIN_SCORE = 50  # Only alert on companies scoring 50+

def load_alert_history():
    """Load history of sent alerts to avoid duplicates."""
    if not ALERTS_FILE.exists():
        return {"alerts": []}
    with open(ALERTS_FILE) as f:
        return json.load(f)

def save_alert(company):
    """Record that we sent an alert for this company."""
    history = load_alert_history()
    history["alerts"].append({
        "timestamp": datetime.now().isoformat(),
        "cik": company["cik"],
        "company": company["company"],
        "score": company["score"]
    })
    with open(ALERTS_FILE, "w") as f:
        json.dump(history, f, indent=2)

def already_alerted(cik):
    """Check if we already alerted on this company."""
    history = load_alert_history()
    for alert in history["alerts"]:
        if alert["cik"] == cik:
            return True
    return False

def format_alert(company):
    """Format company as readable alert."""
    metrics = company["metrics"]
    
    msg = f"""
{'='*80}
🚨 HIGH-QUALITY MICRO-CAP DETECTED
{'='*80}

Company: {company['company']} ({company.get('ticker', 'N/A')})
CIK: {company['cik']}
Market Cap: ${company.get('market_cap', 0):,}

SCORE: {company['score']}/100

KEY METRICS:
"""
    
    if metrics.get('revenue'):
        msg += f"  Revenue: ${metrics['revenue']/1e6:.1f}M\n"
    if metrics.get('net_margin'):
        msg += f"  Net Margin: {metrics['net_margin']:.1f}%\n"
    if metrics.get('debt_to_assets') is not None:
        msg += f"  Debt/Assets: {metrics['debt_to_assets']:.1f}%\n"
    if metrics.get('net_income'):
        msg += f"  Net Income: ${metrics['net_income']/1e6:.1f}M\n"
    
    if company['reasons']:
        msg += f"\nWHY THIS IS INTERESTING:\n"
        for reason in company['reasons']:
            msg += f"  • {reason}\n"
    
    msg += f"\nSEC Filings: https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={company['cik']}&type=&dateb=&owner=exclude&count=40\n"
    msg += f"{'='*80}\n"
    
    return msg

def check_and_alert(min_score=MIN_SCORE):
    """Check for high-score companies and alert on new ones."""
    if not SCORES_FILE.exists():
        print("No scores file found. Run scorer.py first.")
        return []
    
    scores = json.load(open(SCORES_FILE))
    
    # Filter for high-score companies
    high_scores = [c for c in scores if c["score"] >= min_score]
    
    new_alerts = []
    
    for company in high_scores:
        if not already_alerted(company["cik"]):
            print(format_alert(company))
            save_alert(company)
            new_alerts.append(company)
    
    return new_alerts

if __name__ == "__main__":
    import sys
    
    min_score = MIN_SCORE
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        min_score = int(sys.argv[1])
    
    print(f"Checking for high-score companies (min score: {min_score})...\n")
    
    new_alerts = check_and_alert(min_score)
    
    if new_alerts:
        print(f"\n✓ Sent {len(new_alerts)} new alerts")
    else:
        print("\n✓ No new high-score companies found")
