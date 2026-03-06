#!/usr/bin/env python3
"""
MGF (Moment Generating Function) algorithm implementation.
Core patent algorithm from US Patents 10,176,442 & 10,997,540.
"""

import numpy as np
import networkx as nx

def threshold_function(x):
    """
    Threshold distribution function F.
    For financial networks: probability of connection activation.
    
    Simple implementation: linear threshold.
    Can be customized based on domain knowledge.
    """
    if x <= 0:
        return 0
    if x >= 1:
        return 1
    return x  # Linear between 0 and 1

def calculate_degree_distribution(G, node):
    """
    Calculate degree distribution p(k) for a node's neighborhood.
    
    Returns: dict mapping degree k to probability p(k)
    """
    if node not in G:
        return {}
    
    # Get neighbors
    neighbors = list(G.neighbors(node))
    
    if not neighbors:
        return {0: 1.0}
    
    # Calculate degree for each neighbor
    degrees = [G.degree(n) for n in neighbors]
    
    # Build distribution
    max_degree = max(degrees) if degrees else 0
    distribution = {}
    
    for k in range(max_degree + 1):
        count = sum(1 for d in degrees if d == k)
        distribution[k] = count / len(degrees) if degrees else 0
    
    return distribution

def calculate_mgf_metrics(G, node, threshold_func=threshold_function):
    """
    Calculate Moment Generating Function metrics for a node.
    
    Core patent algorithm from US Patents 10,176,442 & 10,997,540.
    
    Args:
        G: Network graph
        node: Node to analyze
        threshold_func: Threshold distribution function F
    
    Returns:
        dict with G0, G1, G2 values
    """
    if node not in G:
        return {'G0': 0, 'G1': 0, 'G2': 0}
    
    # Get degree distribution
    p = calculate_degree_distribution(G, node)
    
    if not p:
        return {'G0': 0, 'G1': 0, 'G2': 0}
    
    # Maximum degree
    N = max(p.keys())
    
    # Initialize MGF values
    G0 = G1 = G2 = 0.0
    
    # Core algorithm from patent
    for k in range(N + 1):
        # Threshold calculation
        if k <= 0:
            rhok = 1.0
        else:
            rhok = threshold_func(1.0 / k)
        
        # Weighted by degree distribution
        sk = rhok * p.get(k, 0)
        
        # MGF and derivatives
        G0 += sk
        G1 += k * sk
        G2 += k * (k - 1) * sk
    
    return {
        'G0': G0,
        'G1': G1,
        'G2': G2
    }

def calculate_network_metrics(mgf_results):
    """
    Calculate financial network metrics from MGF results.
    
    Args:
        mgf_results: dict with G0, G1, G2 values
    
    Returns:
        dict with systemic_importance, contagion_risk, network_value
    """
    G0 = mgf_results['G0']
    G1 = mgf_results['G1']
    G2 = mgf_results['G2']
    
    # Systemic importance (expected propagation)
    systemic_importance = G1 / G0 if G0 > 0 else 0
    
    # Contagion risk (variance indicates instability)
    variance = G2 - (G1 ** 2)
    contagion_risk = variance / (G1 + 1) if G1 > -1 else 0
    
    # Network value (simplified - based on connectivity strength)
    network_value = G0 * G1 if G0 > 0 and G1 > 0 else 0
    
    return {
        'systemic_importance': systemic_importance,
        'contagion_risk': contagion_risk,
        'network_value': network_value,
        'variance': variance
    }

if __name__ == "__main__":
    # Example usage
    G = nx.DiGraph()
    G.add_edges_from([
        ('A', 'B'), ('A', 'C'), ('A', 'D'),
        ('B', 'C'), ('C', 'D'), ('D', 'E')
    ])
    
    for node in ['A', 'B', 'C', 'D', 'E']:
        mgf = calculate_mgf_metrics(G, node)
        metrics = calculate_network_metrics(mgf)
        
        print(f"\n{node}:")
        print(f"  MGF: G0={mgf['G0']:.3f}, G1={mgf['G1']:.3f}, G2={mgf['G2']:.3f}")
        print(f"  Systemic Importance: {metrics['systemic_importance']:.3f}")
        print(f"  Contagion Risk: {metrics['contagion_risk']:.3f}")
        print(f"  Network Value: {metrics['network_value']:.3f}")
