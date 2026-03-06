#!/usr/bin/env python3
"""
Comprehensive SEC EDGAR scraper.
Uses multiple RSS feeds and bulk download for better coverage.
"""

import requests
import feedparser
import json
import time
from pathlib import Path
from datetime import datetime

HEADERS = {'User-Agent': 'ENIS research@apexexotics.com'}
DATA_DIR = Path(__file__).parent / 'data'
FILINGS_FILE = DATA_DIR / 'filings.json'

def scrape_rss_feed(form_type='10-K', count=100):
    """
    Scrape SEC RSS feed for specific form type.
    
    Available feeds:
    - 10-K: Annual reports
    - 10-Q: Quarterly reports
    - 8-K: Current events
    - All: All filings
    """
    url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type={form_type}&count={count}&output=atom"
    
    print(f"Fetching {form_type} filings from RSS...")
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        feed = feedparser.parse(resp.content)
        
        filings = []
        for entry in feed.entries:
            title = entry.title
            link = entry.link
            updated = entry.get('updated', '')
            
            # Parse title: "10-K - COMPANY NAME (CIK)"
            if ' - ' not in title:
                continue
            
            parts = title.split(' - ', 1)
            filing_type = parts[0].strip()
            company_part = parts[1]
            
            # Extract CIK
            if '(' in company_part:
                company_name = company_part[:company_part.find('(')].strip()
                cik_part = company_part[company_part.find('(')+1:company_part.find(')')].strip()
                # CIK is numeric
                if cik_part.isdigit() or cik_part.startswith('000'):
                    cik = cik_part.zfill(10)
                else:
                    cik = None
            else:
                company_name = company_part.strip()
                cik = None
            
            if not cik:
                continue
            
            filing = {
                'cik': cik,
                'company': company_name,
                'filing_type': filing_type,
                'filed_date': updated,
                'url': link,
                'discovered': datetime.now().isoformat()
            }
            filings.append(filing)
        
        print(f"  Found {len(filings)} {form_type} filings")
        return filings
    
    except Exception as e:
        print(f"  Error: {e}")
        return []

def scrape_company_tickers_list():
    """
    Download SEC's complete company tickers list.
    This gives us ALL public companies with their CIKs and tickers.
    """
    url = "https://www.sec.gov/files/company_tickers.json"
    
    print("Fetching complete company list from SEC...")
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        companies = resp.json()
        
        print(f"  Found {len(companies)} total companies")
        return companies
    
    except Exception as e:
        print(f"  Error: {e}")
        return {}

def filter_by_market_cap_estimate(companies, max_companies=200):
    """
    Filter companies likely to be micro-caps.
    Strategy: Skip obvious mega-caps, take from middle/end of list.
    """
    mega_cap_keywords = [
        'APPLE', 'MICROSOFT', 'AMAZON', 'ALPHABET', 'GOOGLE', 'META', 
        'TESLA', 'NVIDIA', 'BERKSHIRE', 'WALMART', 'JPMORGAN', 'VISA',
        'JOHNSON', 'EXXON', 'UNITEDHEALTH', 'PROCTER', 'MASTERCARD',
        'HOME DEPOT', 'CHEVRON', 'ABBVIE', 'MERCK', 'PFIZER', 'COCA-COLA',
        'PEPSICO', 'COSTCO', 'CISCO', 'INTEL', 'NETFLIX', 'DISNEY',
        'VERIZON', 'AT&T', 'COMCAST', 'ORACLE', 'ADOBE', 'SALESFORCE',
        'BANK OF AMERICA', 'WELLS FARGO', 'MORGAN STANLEY', 'GOLDMAN SACHS'
    ]
    
    filtered = []
    company_list = list(companies.items())
    
    # Take from middle and end of list (smaller companies)
    for idx, company in company_list[1000:]:  # Skip first 1000 (largest)
        name = company.get('title', '').upper()
        
        # Skip mega-caps
        if any(keyword in name for keyword in mega_cap_keywords):
            continue
        
        filtered.append(company)
        
        if len(filtered) >= max_companies:
            break
    
    print(f"  Filtered to {len(filtered)} likely micro/small-caps")
    return filtered

def import_to_database(filings):
    """Import filings to database."""
    DATA_DIR.mkdir(exist_ok=True)
    
    # Load existing
    existing = {}
    if FILINGS_FILE.exists():
        with open(FILINGS_FILE) as f:
            existing = json.load(f)
    
    # Add new
    added = 0
    for filing in filings:
        cik = filing.get('cik')
        filing_type = filing.get('filing_type', '10-K')
        key = f"{cik}_{filing_type}_"
        
        if key not in existing:
            existing[key] = filing
            added += 1
    
    # Save
    with open(FILINGS_FILE, 'w') as f:
        json.dump(existing, f, indent=2)
    
    print(f"\n✓ Added {added} new filings (total: {len(existing)})")
    return added

if __name__ == '__main__':
    print("="*60)
    print("ENIS Comprehensive Scraper")
    print("="*60)
    print()
    
    all_filings = []
    
    # Method 1: RSS feeds (most recent filings)
    print("Method 1: RSS Feeds")
    print("-"*60)
    for form_type in ['10-K', '10-Q']:
        filings = scrape_rss_feed(form_type, count=100)
        all_filings.extend(filings)
        time.sleep(1)  # Be nice to SEC
    print()
    
    # Method 2: Company tickers list (comprehensive but need to check market caps)
    print("Method 2: Company Tickers List")
    print("-"*60)
    companies = scrape_company_tickers_list()
    if companies:
        filtered = filter_by_market_cap_estimate(companies, max_companies=100)
        
        # Convert to filings format
        for company in filtered:
            cik = str(company['cik_str']).zfill(10)
            filing = {
                'cik': cik,
                'company': company.get('title', ''),
                'ticker': company.get('ticker', ''),
                'filing_type': '10-K',
                'filed_date': '',
                'url': f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=10-K&count=1",
                'discovered': datetime.now().isoformat()
            }
            all_filings.append(filing)
    print()
    
    # Import all
    print("Importing to database...")
    print("-"*60)
    import_to_database(all_filings)
    print()
    print("Next steps:")
    print("  1. Run market_cap.py to filter for micro-caps")
    print("  2. Run financials.py to parse metrics")
    print("  3. Run full pipeline: ./run_full.sh")
