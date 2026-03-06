#!/usr/bin/env python3
"""
Financial metrics parser - extract key metrics from XBRL filings.
Uses SEC CompanyFacts API (free, no key required).
"""

import json
import time
import requests
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
FILINGS_FILE = DATA_DIR / "filings.json"
MARKET_CAP_FILE = DATA_DIR / "market_caps.json"
FINANCIALS_FILE = DATA_DIR / "financials.json"

SEC_BASE = "https://data.sec.gov"
HEADERS = {"User-Agent": "EDGAR Monitor research@apexexotics.com"}

def get_company_facts(cik):
    """Fetch all XBRL facts for a company via SEC CompanyFacts API."""
    cik_padded = str(cik).zfill(10)
    url = f"{SEC_BASE}/api/xbrl/companyfacts/CIK{cik_padded}.json"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  ! Error fetching facts for CIK {cik}: {e}")
        return None

def extract_metric(facts, concept, taxonomy="us-gaap"):
    """Extract most recent annual value for a concept."""
    try:
        concept_data = facts["facts"][taxonomy][concept]
        units = concept_data.get("units", {})
        values = units.get("USD", units.get("shares", []))
        
        # Filter to annual filings (10-K)
        annual = [v for v in values if v.get("form") == "10-K" and v.get("fp") == "FY"]
        if not annual:
            return None
        
        # Get most recent
        annual.sort(key=lambda x: x.get("filed", ""), reverse=True)
        return annual[0].get("val")
    except (KeyError, IndexError):
        return None

def parse_financials():
    """Parse financial metrics for all filings."""
    filings_db = json.load(open(FILINGS_FILE))
    market_caps = json.load(open(MARKET_CAP_FILE))
    
    financials = {}
    checked = 0
    
    for key, filing in filings_db.items():
        cik = filing.get("cik")
        
        # Skip if no market cap data or not micro-cap
        if cik not in market_caps:
            continue
        cap_data = market_caps[cik]
        if not cap_data.get("market_cap") or cap_data["market_cap"] >= 100_000_000:
            continue
        
        # Skip if already parsed
        if cik in financials:
            continue
        
        print(f"Parsing {filing['company']} (CIK: {cik})...")
        
        # Fetch XBRL facts
        facts = get_company_facts(cik)
        if not facts:
            continue
        
        # Extract key metrics
        metrics = {
            "cik": cik,
            "company": filing["company"],
            "revenue": extract_metric(facts, "Revenues"),
            "net_income": extract_metric(facts, "NetIncomeLoss"),
            "total_assets": extract_metric(facts, "Assets"),
            "total_liabilities": extract_metric(facts, "Liabilities"),
            "cash": extract_metric(facts, "CashAndCashEquivalentsAtCarryingValue"),
            "stockholders_equity": extract_metric(facts, "StockholdersEquity"),
        }
        
        # Calculate derived metrics
        if metrics["revenue"] and metrics["net_income"]:
            metrics["net_margin"] = (metrics["net_income"] / metrics["revenue"]) * 100
        
        if metrics["total_assets"] and metrics["total_liabilities"]:
            metrics["debt_to_assets"] = (metrics["total_liabilities"] / metrics["total_assets"]) * 100
        
        financials[cik] = metrics
        checked += 1
        
        print(f"  ✓ Revenue: ${metrics.get('revenue') or 0:,}")
        print(f"  ✓ Net Margin: {metrics.get('net_margin') or 0:.1f}%")
        
        # Rate limit: 10 req/sec max, use 0.12s for safety
        time.sleep(0.12)
    
    # Save results
    DATA_DIR.mkdir(exist_ok=True)
    with open(FINANCIALS_FILE, "w") as f:
        json.dump(financials, f, indent=2)
    
    print(f"\n✓ Parsed {len(financials)} companies")
    return financials

if __name__ == "__main__":
    parse_financials()
