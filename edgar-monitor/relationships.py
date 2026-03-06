#!/usr/bin/env python3
"""
Relationship extractor - parse 10-Ks for company relationships.
Extracts: major customers, suppliers, strategic partners.
"""

import re
import json
import requests
from pathlib import Path
from html.parser import HTMLParser

DATA_DIR = Path(__file__).parent / "data"
FILINGS_FILE = DATA_DIR / "filings.json"
RELATIONSHIPS_FILE = DATA_DIR / "relationships.json"

SEC_BASE = "https://www.sec.gov"
HEADERS = {"User-Agent": "EDGAR Monitor research@apexexotics.com"}

class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
    def handle_data(self, data):
        self.text.append(data)
    def get_text(self):
        return ' '.join(self.text)

def strip_html(html):
    """Remove HTML tags."""
    stripper = HTMLStripper()
    stripper.feed(html)
    return stripper.get_text()

def get_filing_text(filing_url):
    """Fetch full text of a filing."""
    try:
        # Convert index URL to actual document URL
        doc_url = filing_url.replace("-index.htm", ".txt")
        
        print(f"  Fetching document...", end="", flush=True)
        resp = requests.get(doc_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        print(" done")
        
        # Strip HTML tags and limit to first 500KB
        text = resp.text[:500000]
        return strip_html(text)
    except Exception as e:
        print(f" failed: {e}")
        return None

def extract_relationships(text):
    """
    Extract company relationships from filing text.
    Focus on concentration risk - companies with major customer dependencies.
    """
    relationships = {
        'customer_concentration': [],  # % of revenue from top customers
        'has_major_customers': False
    }
    
    # Pattern: "X% of revenue" or "X% of sales"
    concentration_pattern = r'(\d+)%\s+of\s+(?:our\s+)?(?:total\s+)?(?:revenue|sales|net revenue|net sales)'
    
    percentages = []
    for match in re.finditer(concentration_pattern, text):
        pct = int(match.group(1))
        if 10 <= pct <= 100:  # Reasonable range
            percentages.append(pct)
    
    if percentages:
        relationships['customer_concentration'] = sorted(set(percentages), reverse=True)[:5]
        relationships['has_major_customers'] = any(p >= 20 for p in percentages)
    
    return relationships

def load_relationships():
    """Load existing relationships database."""
    if not RELATIONSHIPS_FILE.exists():
        return {}
    with open(RELATIONSHIPS_FILE) as f:
        return json.load(f)

def save_relationships(relationships_db):
    """Save relationships database."""
    DATA_DIR.mkdir(exist_ok=True)
    with open(RELATIONSHIPS_FILE, "w") as f:
        json.dump(relationships_db, f, indent=2)

def extract_all_relationships():
    """Extract relationships for all filings."""
    print("Loading filings database...")
    filings_db = json.load(open(FILINGS_FILE))
    relationships_db = load_relationships()
    
    print(f"Found {len(filings_db)} filings, {len(relationships_db)} already processed")
    
    extracted = 0
    
    for i, (key, filing) in enumerate(filings_db.items(), 1):
        cik = filing.get("cik")
        
        # Skip if already extracted
        if cik in relationships_db:
            print(f"[{i}/{len(filings_db)}] Skipping {filing['company']} (already processed)")
            continue
        
        print(f"[{i}/{len(filings_db)}] {filing['company']} (CIK: {cik})")
        
        # Fetch filing text
        filing_url = filing.get("url")
        if not filing_url:
            print("  ! No URL")
            continue
        
        text = get_filing_text(filing_url)
        if not text:
            continue
        
        print(f"  Parsing {len(text)} chars...")
        
        # Extract relationships
        relationships = extract_relationships(text)
        
        # Store
        relationships_db[cik] = {
            'company': filing['company'],
            'cik': cik,
            'relationships': relationships,
            'filing_url': filing_url
        }
        
        extracted += 1
        
        # Display results
        if relationships['has_major_customers']:
            print(f"  ✓ Customer concentration: {relationships['customer_concentration'][:3]}")
        else:
            print(f"  - No major customer concentration")
        
        # Rate limit
        import time
        time.sleep(0.12)
    
    save_relationships(relationships_db)
    print(f"\n✓ Extracted relationships for {extracted} companies")
    return relationships_db

if __name__ == "__main__":
    extract_all_relationships()
