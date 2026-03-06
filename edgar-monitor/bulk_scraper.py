#!/usr/bin/env python3
"""
Bulk scraper for SEC EDGAR 10-K filings.
Fetches recent 10-Ks to build initial database.
"""

import json
import time
import requests
from pathlib import Path
from datetime import datetime, timedelta

# SEC requires User-Agent header
HEADERS = {
    'User-Agent': 'Apex Exotics ENIS john@nodes.bio'
}

def fetch_recent_10k_filings(days_back=90, max_results=100):
    """
    Fetch recent 10-K filings from SEC EDGAR.
    
    Uses SEC's full-text search API to find 10-Ks filed in last N days.
    """
    filings = []
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    print(f"Searching for 10-K filings from {start_date.date()} to {end_date.date()}...")
    print(f"Target: {max_results} filings")
    print()
    
    # SEC EDGAR search endpoint
    # Note: This is a simplified approach. For production, use the official EDGAR API
    base_url = "https://www.sec.gov/cgi-bin/browse-edgar"
    
    # Search parameters
    params = {
        'action': 'getcompany',
        'type': '10-K',
        'dateb': end_date.strftime('%Y%m%d'),
        'owner': 'exclude',
        'start': 0,
        'count': 100,
        'output': 'atom'
    }
    
    try:
        response = requests.get(base_url, params=params, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            # Parse RSS/Atom feed
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            # Extract entries
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            entries = root.findall('.//atom:entry', ns)
            
            print(f"Found {len(entries)} recent 10-K filings")
            
            for entry in entries[:max_results]:
                title = entry.find('atom:title', ns)
                link = entry.find('atom:link', ns)
                updated = entry.find('atom:updated', ns)
                
                if title is not None and link is not None:
                    # Extract company name and CIK from title
                    title_text = title.text
                    # Format: "10-K - Company Name (CIK)"
                    
                    filing = {
                        'title': title_text,
                        'link': link.get('href'),
                        'date': updated.text if updated is not None else '',
                        'type': '10-K'
                    }
                    filings.append(filing)
        
        else:
            print(f"Error: HTTP {response.status_code}")
    
    except Exception as e:
        print(f"Error fetching filings: {e}")
    
    return filings

def search_by_sic_code(sic_code, max_results=50):
    """
    Search for companies by SIC code.
    Useful for targeting specific industries.
    """
    print(f"Searching SIC code {sic_code}...")
    
    base_url = "https://www.sec.gov/cgi-bin/browse-edgar"
    params = {
        'action': 'getcompany',
        'SIC': sic_code,
        'type': '10-K',
        'owner': 'exclude',
        'count': max_results,
        'output': 'atom'
    }
    
    try:
        response = requests.get(base_url, params=params, headers=HEADERS, timeout=10)
        # Parse similar to above
        # ... (implementation similar to fetch_recent_10k_filings)
        
    except Exception as e:
        print(f"Error: {e}")
    
    return []

def import_filings_to_database(filings):
    """Import scraped filings into ENIS database."""
    db_file = Path(__file__).parent / 'data' / 'filings.json'
    
    # Load existing
    existing = {}
    if db_file.exists():
        with open(db_file) as f:
            existing = json.load(f)
    
    # Add new filings
    added = 0
    for filing in filings:
        cik = filing.get('cik', '')
        filing_type = filing.get('type', '10-K')
        key = f"{cik}_{filing_type}_"
        
        # Check if already exists
        if key not in existing:
            existing[key] = {
                'cik': cik,
                'company': filing.get('company', filing.get('title', '')),
                'filing_type': filing_type,
                'filed_date': filing.get('date', ''),
                'url': filing.get('link', ''),
                'discovered': datetime.now().isoformat()
            }
            added += 1
    
    # Save
    with open(db_file, 'w') as f:
        json.dump(existing, f, indent=2)
    
    print(f"\n✓ Added {added} new filings (total: {len(existing)})")
    return added

def bulk_scrape_simple():
    """
    Simple bulk scraper using SEC company tickers list.
    Downloads list of all companies, filters for likely micro-caps.
    """
    print("Fetching SEC company tickers list...")
    
    # SEC provides a JSON file with all company tickers
    url = "https://www.sec.gov/files/company_tickers.json"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        companies = response.json()
        
        print(f"Found {len(companies)} total companies")
        print("Filtering for likely micro-caps (skipping mega-caps)...")
        print()
        
        # Skip obvious mega-caps by name
        mega_cap_keywords = [
            'APPLE', 'MICROSOFT', 'AMAZON', 'ALPHABET', 'GOOGLE', 'META', 
            'TESLA', 'NVIDIA', 'BERKSHIRE', 'WALMART', 'JPMORGAN', 'VISA',
            'JOHNSON', 'EXXON', 'UNITEDHEALTH', 'PROCTER', 'MASTERCARD',
            'HOME DEPOT', 'CHEVRON', 'ABBVIE', 'MERCK', 'PFIZER', 'COCA-COLA',
            'PEPSICO', 'COSTCO', 'CISCO', 'INTEL', 'NETFLIX', 'DISNEY',
            'VERIZON', 'AT&T', 'COMCAST', 'ORACLE', 'ADOBE', 'SALESFORCE'
        ]
        
        # Convert to filings format - start from END of list (smaller companies)
        filings = []
        company_list = list(companies.items())
        
        # Reverse to get smaller companies first
        for idx, company in reversed(company_list[-200:]):  # Last 200 companies
            cik = str(company['cik_str']).zfill(10)
            ticker = company.get('ticker', '')
            name = company.get('title', '').upper()
            
            # Skip mega-caps
            if any(keyword in name for keyword in mega_cap_keywords):
                continue
            
            # Create filing entry
            filing = {
                'company': company.get('title', ''),
                'cik': cik,
                'ticker': ticker,
                'type': '10-K',
                'link': f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=10-K&count=1",
                'date': datetime.now().isoformat(),
                'title': f"10-K - {company.get('title', '')}"
            }
            filings.append(filing)
            
            if len(filings) >= 50:  # Reduced to 50
                break
        
        print(f"Prepared {len(filings)} companies for import (from smaller end of list)")
        return filings
    
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == '__main__':
    print("="*60)
    print("ENIS Bulk Scraper")
    print("="*60)
    print()
    
    # Use simple approach: get company list
    filings = bulk_scrape_simple()
    
    if filings:
        added = import_filings_to_database(filings)
        print()
        print("Next steps:")
        print("  1. Run market_cap.py to filter for micro-caps")
        print("  2. Run financials.py to parse metrics")
        print("  3. Run full pipeline: ./run_full.sh")
    else:
        print("No filings found")
