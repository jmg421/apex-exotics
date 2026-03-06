#!/usr/bin/env python3
"""
Network graph builder - construct company relationship network.
"""

import json
import networkx as nx
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
RELATIONSHIPS_FILE = DATA_DIR / "relationships.json"
NETWORK_FILE = DATA_DIR / "network.json"

def build_network_graph():
    """Build network graph from relationship data."""
    # Load relationships
    with open(RELATIONSHIPS_FILE) as f:
        relationships_db = json.load(f)
    
    # Create directed graph
    G = nx.DiGraph()
    
    # Add nodes (companies) with concentration risk
    for cik, data in relationships_db.items():
        rels = data['relationships']
        concentration = rels.get('customer_concentration', [])
        max_concentration = max(concentration) if concentration else 0
        
        G.add_node(cik, 
                  company=data['company'],
                  customer_concentration=max_concentration,
                  has_major_customers=rels.get('has_major_customers', False))
    
    # Add edges based on concentration (companies with similar risk profiles)
    # High concentration = higher systemic risk
    ciks = list(relationships_db.keys())
    for i, cik1 in enumerate(ciks):
        data1 = relationships_db[cik1]
        conc1 = data1['relationships'].get('customer_concentration', [])
        
        if not conc1:
            continue
            
        for cik2 in ciks[i+1:]:
            data2 = relationships_db[cik2]
            conc2 = data2['relationships'].get('customer_concentration', [])
            
            if not conc2:
                continue
            
            # If both have high concentration, they share systemic risk
            if max(conc1) >= 40 and max(conc2) >= 40:
                G.add_edge(cik1, cik2, relationship='concentration_risk')
    
    return G

def calculate_network_stats(G):
    """Calculate basic network statistics."""
    return {
        'num_nodes': G.number_of_nodes(),
        'num_edges': G.number_of_edges(),
        'density': nx.density(G),
        'avg_degree': sum(dict(G.degree()).values()) / G.number_of_nodes() if G.number_of_nodes() > 0 else 0
    }

def get_node_metrics(G, node):
    """Calculate metrics for a specific node."""
    if node not in G:
        return None
    
    return {
        'degree': G.degree(node),
        'in_degree': G.in_degree(node),
        'out_degree': G.out_degree(node),
        'neighbors': list(G.neighbors(node))
    }

def save_network(G):
    """Save network graph to JSON."""
    # Convert to node-link format for JSON serialization
    data = nx.node_link_data(G)
    
    with open(NETWORK_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ Network saved to {NETWORK_FILE}")

def load_network():
    """Load network graph from JSON."""
    if not NETWORK_FILE.exists():
        return None
    
    with open(NETWORK_FILE) as f:
        data = json.load(f)
    
    return nx.node_link_graph(data)

if __name__ == "__main__":
    print("Building network graph...")
    G = build_network_graph()
    
    stats = calculate_network_stats(G)
    print(f"\nNetwork Statistics:")
    print(f"  Nodes: {stats['num_nodes']}")
    print(f"  Edges: {stats['num_edges']}")
    print(f"  Density: {stats['density']:.4f}")
    print(f"  Avg Degree: {stats['avg_degree']:.2f}")
    
    save_network(G)
