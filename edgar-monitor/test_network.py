#!/usr/bin/env python3
"""
Test suite for network graph builder.
"""

import pytest
import networkx as nx
from network import build_network_graph, calculate_network_stats, get_node_metrics

def test_empty_network():
    """Test empty network creation."""
    G = nx.DiGraph()
    stats = calculate_network_stats(G)
    
    assert stats['num_nodes'] == 0
    assert stats['num_edges'] == 0
    assert stats['avg_degree'] == 0

def test_simple_network():
    """Test simple network with 2 nodes."""
    G = nx.DiGraph()
    G.add_node('A', company='Company A')
    G.add_node('B', company='Company B')
    G.add_edge('A', 'B', relationship='customer')
    
    stats = calculate_network_stats(G)
    
    assert stats['num_nodes'] == 2
    assert stats['num_edges'] == 1

def test_node_metrics():
    """Test node metrics calculation."""
    G = nx.DiGraph()
    G.add_edge('A', 'B')
    G.add_edge('A', 'C')
    G.add_edge('D', 'A')
    
    metrics = get_node_metrics(G, 'A')
    
    assert metrics['degree'] == 3  # 2 out + 1 in
    assert metrics['in_degree'] == 1
    assert metrics['out_degree'] == 2
    assert len(metrics['neighbors']) == 2

def test_node_not_in_graph():
    """Test metrics for non-existent node."""
    G = nx.DiGraph()
    G.add_node('A')
    
    metrics = get_node_metrics(G, 'Z')
    
    assert metrics is None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
