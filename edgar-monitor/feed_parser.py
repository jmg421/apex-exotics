#!/usr/bin/env python3
"""
EDGAR RSS feed parser - monitor new 10-K/10-Q filings.
"""

import feedparser
import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent / "data"
FILINGS_FILE = DATA_DIR / "filings.json"

EDGAR_RSS = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type=&company=&dateb=&owner=exclude&start=0&count=100&output=atom"
HEADERS = {"User-Agent": "EDGAR Monitor research@apexexotics.com"}

def parse_feed():
    """Fetch and parse EDGAR RSS feed."""
    import requests
    resp = requests.get(EDGAR_RSS, headers=HEADERS)
    feed = feedparser.parse(resp.content)
    filings = []
    
    for entry in feed.entries:
        title = entry.title
        
        # Parse title format: "10-K - COMPANY NAME (CIK)"
        if " - " not in title:
            continue
            
        parts = title.split(" - ", 1)
        filing_type = parts[0].strip()
        
        # Only track 10-K and 10-Q
        if filing_type not in ["10-K", "10-Q"]:
            continue
        
        # Extract company and CIK
        company_part = parts[1]
        if "(" in company_part:
            # Format: "COMPANY NAME (CIK) (Filer)" or "COMPANY NAME (0001234567)"
            cik_match = company_part.split("(")[1].split(")")[0].strip()
            # Remove "Filer" text if present
            if cik_match == "Filer":
                cik = None
            else:
                cik = cik_match
            company_name = company_part[:company_part.find("(")].strip()
        else:
            company_name = company_part.strip()
            cik = None
        
        filings.append({
            "cik": cik,
            "company": company_name,
            "filing_type": filing_type,
            "filed_date": entry.get("published", ""),
            "url": entry.link,
            "discovered": datetime.now().isoformat()
        })
    
    return filings

def load_filings():
    """Load existing filings database."""
    if not FILINGS_FILE.exists():
        return {}
    with open(FILINGS_FILE) as f:
        return json.load(f)

def save_filings(filings_db):
    """Save filings database."""
    DATA_DIR.mkdir(exist_ok=True)
    with open(FILINGS_FILE, "w") as f:
        json.dump(filings_db, f, indent=2)

def update_filings():
    """Fetch new filings and update database."""
    print("Fetching EDGAR RSS feed...")
    new_filings = parse_feed()
    
    filings_db = load_filings()
    added = 0
    
    for filing in new_filings:
        key = f"{filing['cik']}_{filing['filing_type']}_{filing['filed_date']}"
        if key not in filings_db:
            filings_db[key] = filing
            added += 1
            print(f"  + {filing['filing_type']}: {filing['company']} (CIK: {filing['cik']})")
    
    save_filings(filings_db)
    print(f"\n✓ Added {added} new filings (total: {len(filings_db)})")
    
    return added

if __name__ == "__main__":
    update_filings()
