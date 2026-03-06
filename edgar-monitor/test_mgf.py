#!/usr/bin/env python3
"""
Test suite for MGF algorithm.
"""

import pytest
import networkx as nx
from mgf import (
    threshold_function,
    calculate_degree_distribution,
    calculate_mgf_metrics,
    calculate_network_metrics
)

def test_threshold_function():
    """Test threshold function behavior."""
    assert threshold_function(0) == 0
    assert threshold_function(1) == 1
    assert threshold_function(0.5) == 0.5
    assert threshold_function(-1) == 0
    assert threshold_function(2) == 1

def test_degree_distribution_empty():
    """Test degree distribution for isolated node."""
    G = nx.DiGraph()
    G.add_node('A')
    
    dist = calculate_degree_distribution(G, 'A')
    
    assert dist == {0: 1.0}

def test_degree_distribution_simple():
    """Test degree distribution calculation."""
    G = nx.DiGraph()
    G.add_edges_from([('A', 'B'), ('A', 'C')])
    G.add_edge('B', 'D')
    
    dist = calculate_degree_distribution(G, 'A')
    
    # A has 2 neighbors: B (degree 1) and C (degree 0)
    assert 0 in dist
    assert 1 in dist

def test_mgf_isolated_node():
    """Test MGF for isolated node."""
    G = nx.DiGraph()
    G.add_node('A')
    
    mgf = calculate_mgf_metrics(G, 'A')
    
    assert mgf['G0'] == 1.0  # Only k=0 term
    assert mgf['G1'] == 0.0
    assert mgf['G2'] == 0.0

def test_mgf_simple_network():
    """Test MGF calculation on simple network."""
    G = nx.DiGraph()
    G.add_edges_from([('A', 'B'), ('A', 'C')])
    
    mgf = calculate_mgf_metrics(G, 'A')
    
    assert mgf['G0'] > 0
    assert mgf['G1'] >= 0
    assert mgf['G2'] >= 0

def test_network_metrics_zero_mgf():
    """Test network metrics with zero MGF."""
    mgf = {'G0': 0, 'G1': 0, 'G2': 0}
    
    metrics = calculate_network_metrics(mgf)
    
    assert metrics['systemic_importance'] == 0
    assert metrics['contagion_risk'] == 0
    assert metrics['network_value'] == 0

def test_network_metrics_positive():
    """Test network metrics with positive MGF values."""
    mgf = {'G0': 1.0, 'G1': 2.0, 'G2': 4.0}
    
    metrics = calculate_network_metrics(mgf)
    
    assert metrics['systemic_importance'] == 2.0  # G1/G0
    assert metrics['network_value'] == 2.0  # G0*G1
    assert metrics['contagion_risk'] >= 0

def test_mgf_nonexistent_node():
    """Test MGF for node not in graph."""
    G = nx.DiGraph()
    G.add_node('A')
    
    mgf = calculate_mgf_metrics(G, 'Z')
    
    assert mgf['G0'] == 0
    assert mgf['G1'] == 0
    assert mgf['G2'] == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
