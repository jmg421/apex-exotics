#!/usr/bin/env python3
"""
Export ENIS network to Nodes.bio format.
"""

import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent / "data"
NETWORK_FILE = DATA_DIR / "network.json"
ENIS_SCORES_FILE = DATA_DIR / "enis_scores.json"
OUTPUT_FILE = DATA_DIR / "enis_network_nodesbio.json"

def export_to_nodesbio():
    """Export ENIS network to Nodes.bio graph format."""
    
    # Load data
    with open(NETWORK_FILE) as f:
        network = json.load(f)
    
    with open(ENIS_SCORES_FILE) as f:
        scores_list = json.load(f)
    
    # Convert scores list to dict
    scores = {s['cik']: s for s in scores_list}
    
    def score_to_color(score):
        """Map ENIS score to color: red (low) -> yellow -> green (high)."""
        if score >= 60: return "#10b981"  # green
        if score >= 40: return "#f59e0b"  # yellow
        if score >= 20: return "#f97316"  # orange
        return "#ef4444"  # red
    
    # Build nodes
    nodes = []
    for i, node in enumerate(network['nodes']):
        cik = node['id']
        company = node['company']
        concentration = node.get('customer_concentration', 0)
        
        # Get ENIS score if available
        score_data = scores.get(cik, {})
        enis_score = score_data.get('enis_score', 0)
        market_cap = score_data.get('market_cap', 0)
        
        # Size by market cap (log scale)
        import math
        size = 40 + (math.log10(market_cap + 1) * 10) if market_cap > 0 else 40
        
        nodes.append({
            "data": {
                "id": cik,
                "label": company,
                "type": "company",
                "color": score_to_color(enis_score),
                "description": f"ENIS Score: {enis_score}/100\nMarket Cap: ${market_cap:,.0f}\nConcentration: {concentration}%",
                "customData": {
                    "enis_score": enis_score,
                    "customer_concentration": concentration,
                    "financial_score": score_data.get('financial_score', 0),
                    "network_metrics": score_data.get('network_metrics', {}),
                    "market_cap": market_cap,
                    "size": size
                }
            },
            "position": {"x": i * 200, "y": i * 100}
        })
    
    # Build edges
    edges = []
    for i, link in enumerate(network.get('links', [])):
        edges.append({
            "data": {
                "id": f"e{i}",
                "source": link['source'],
                "target": link['target'],
                "edge_type": link.get('relationship', 'related'),
                "label": link.get('relationship', 'related')
            }
        })
    
    # Build legend
    legend = {
        "nodes": [
            {
                "type": "company",
                "label": "High Score (60+)",
                "description": "Strong ENIS score",
                "style": {
                    "backgroundColor": "#10b981",
                    "borderColor": "#059669",
                    "borderWidth": 3,
                    "shape": "ellipse",
                    "color": "#ffffff"
                }
            },
            {
                "type": "company_medium",
                "label": "Medium Score (40-59)",
                "description": "Moderate ENIS score",
                "style": {
                    "backgroundColor": "#f59e0b",
                    "borderColor": "#d97706",
                    "borderWidth": 3,
                    "shape": "ellipse",
                    "color": "#ffffff"
                }
            },
            {
                "type": "company_low",
                "label": "Low Score (<40)",
                "description": "Weak ENIS score",
                "style": {
                    "backgroundColor": "#ef4444",
                    "borderColor": "#dc2626",
                    "borderWidth": 3,
                    "shape": "ellipse",
                    "color": "#ffffff"
                }
            }
        ],
        "edges": [{
            "type": "concentration_risk",
            "label": "Concentration Risk",
            "description": "Shared customer concentration risk (>40%)",
            "style": {
                "lineColor": "#ef4444",
                "lineStyle": "dashed",
                "targetArrowShape": "triangle",
                "targetArrowColor": "#ef4444",
                "width": 3
            }
        }]
    }
    
    # Build output
    output = {
        "elements": {
            "nodes": nodes,
            "edges": edges
        },
        "legend": legend,
        "exportedAt": datetime.utcnow().isoformat() + "Z",
        "metadata": {
            "source": "ENIS - EDGAR Network Intelligence System",
            "patents": ["US 10,176,442", "US 10,997,540"],
            "description": "Micro-cap company network with MGF-based risk analysis"
        }
    }
    
    # Save
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"✓ Exported to {OUTPUT_FILE}")
    print(f"  Nodes: {len(nodes)}")
    print(f"  Edges: {len(edges)}")
    print(f"\nImport this file into Nodes.bio to visualize the network.")

if __name__ == "__main__":
    export_to_nodesbio()
