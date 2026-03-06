#!/usr/bin/env python3
"""
ENIS scorer - combine financial metrics + network metrics.
"""

import json
from pathlib import Path
from network import load_network
from mgf import calculate_mgf_metrics, calculate_network_metrics

DATA_DIR = Path(__file__).parent / "data"
SCORES_FILE = DATA_DIR / "scores.json"
FINANCIALS_FILE = DATA_DIR / "financials.json"
ENIS_SCORES_FILE = DATA_DIR / "enis_scores.json"

def load_scores():
    """Load existing financial scores."""
    if not SCORES_FILE.exists():
        return []
    with open(SCORES_FILE) as f:
        return json.load(f)

def calculate_enis_score(financial_score, network_metrics):
    """
    Calculate combined ENIS score.
    
    Weights:
    - Financial quality: 60%
    - Network position: 40%
    """
    # Financial component (0-100)
    financial_component = financial_score * 0.6
    
    # Network component (0-100)
    # Normalize network metrics to 0-100 scale
    systemic_importance = network_metrics.get('systemic_importance', 0)
    network_value = network_metrics.get('network_value', 0)
    contagion_risk = network_metrics.get('contagion_risk', 0)
    
    # Higher systemic importance = higher score
    # Higher network value = higher score
    # Higher contagion risk = lower score
    network_score = min(100, (systemic_importance * 20 + network_value * 10 - contagion_risk * 5))
    network_component = max(0, network_score) * 0.4
    
    return financial_component + network_component

def score_with_network():
    """Score all companies using financial + network metrics."""
    # Load data
    scores = load_scores()
    G = load_network()
    
    if not G:
        print("! No network graph found. Run network.py first.")
        return []
    
    enis_scores = []
    
    for company in scores:
        cik = company['cik']
        
        # Calculate MGF metrics
        mgf = calculate_mgf_metrics(G, cik)
        network_metrics = calculate_network_metrics(mgf)
        
        # Calculate combined score
        financial_score = company['score']
        enis_score = calculate_enis_score(financial_score, network_metrics)
        
        enis_scores.append({
            **company,
            'financial_score': financial_score,
            'network_metrics': network_metrics,
            'mgf': mgf,
            'enis_score': enis_score
        })
    
    # Sort by ENIS score
    enis_scores.sort(key=lambda x: x['enis_score'], reverse=True)
    
    # Save results
    with open(ENIS_SCORES_FILE, 'w') as f:
        json.dump(enis_scores, f, indent=2)
    
    # Display top opportunities
    print(f"\n{'='*80}")
    print("TOP ENIS OPPORTUNITIES (Financial + Network Intelligence)")
    print(f"{'='*80}\n")
    
    for i, company in enumerate(enis_scores[:10], 1):
        print(f"{i}. {company['company']} ({company.get('ticker', 'N/A')})")
        print(f"   ENIS Score: {company['enis_score']:.1f}/100")
        print(f"   Financial: {company['financial_score']}/100")
        print(f"   Network Metrics:")
        print(f"     - Systemic Importance: {company['network_metrics']['systemic_importance']:.3f}")
        print(f"     - Contagion Risk: {company['network_metrics']['contagion_risk']:.3f}")
        print(f"     - Network Value: {company['network_metrics']['network_value']:.3f}")
        print()
    
    print(f"✓ Scored {len(enis_scores)} companies with network intelligence")
    print(f"✓ Results saved to {ENIS_SCORES_FILE}")
    
    return enis_scores

if __name__ == "__main__":
    score_with_network()
