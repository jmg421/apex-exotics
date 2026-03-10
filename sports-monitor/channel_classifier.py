#!/usr/bin/env python3
"""
VSeeBox Channel Classifier - ML-based channel identification
Uses peer IP patterns to identify channels without manual labeling
"""
import json
import re
from collections import defaultdict, Counter
from datetime import datetime

class ChannelClassifier:
    def __init__(self, log_file="/Users/apple/apex-exotics/sports-monitor/data/peer_changes.log"):
        self.log_file = log_file
        self.samples = []
        self.clusters = []
        
    def parse_log(self):
        """Extract peer samples from log"""
        with open(self.log_file, 'r') as f:
            content = f.read()
        
        # Extract timestamp and peer samples
        pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+) - (\d+) peers\n  Sample: \[(.*?)\]'
        matches = re.findall(pattern, content)
        
        for timestamp, count, peers_str in matches:
            # Extract IPs (remove ports)
            peers = []
            for peer in re.findall(r"'([^']+)'", peers_str):
                ip = '.'.join(peer.split('.')[:4])  # Remove port
                peers.append(ip)
            
            self.samples.append({
                'timestamp': timestamp,
                'peer_count': int(count),
                'peers': set(peers)
            })
        
        print(f"Loaded {len(self.samples)} samples")
        return self.samples
    
    def cluster_by_similarity(self, threshold=0.3):
        """Group samples into clusters based on peer overlap"""
        clusters = []
        
        for sample in self.samples:
            # Find best matching cluster
            best_cluster = None
            best_overlap = 0
            
            for cluster in clusters:
                # Calculate overlap with cluster's peer set
                cluster_peers = set()
                for s in cluster['samples']:
                    cluster_peers.update(s['peers'])
                
                overlap = len(sample['peers'] & cluster_peers)
                total = len(sample['peers'] | cluster_peers)
                
                if total > 0:
                    overlap_pct = overlap / total
                    if overlap_pct > best_overlap:
                        best_overlap = overlap_pct
                        best_cluster = cluster
            
            # Add to cluster if overlap > threshold, else create new cluster
            if best_cluster and best_overlap > threshold:
                best_cluster['samples'].append(sample)
                best_cluster['peer_set'].update(sample['peers'])
            else:
                clusters.append({
                    'id': len(clusters),
                    'samples': [sample],
                    'peer_set': set(sample['peers'])
                })
        
        self.clusters = clusters
        print(f"Found {len(clusters)} distinct peer clusters (likely channels)")
        return clusters
    
    def analyze_clusters(self):
        """Analyze each cluster to identify characteristics"""
        results = []
        
        for cluster in self.clusters:
            samples = cluster['samples']
            peer_set = cluster['peer_set']
            
            # Calculate statistics
            peer_counts = [s['peer_count'] for s in samples]
            avg_peers = sum(peer_counts) / len(peer_counts)
            
            # Find most common peers (core peers for this channel)
            peer_frequency = Counter()
            for sample in samples:
                peer_frequency.update(sample['peers'])
            
            core_peers = [ip for ip, count in peer_frequency.most_common(5)]
            
            # Time range
            timestamps = [datetime.fromisoformat(s['timestamp']) for s in samples]
            duration = (max(timestamps) - min(timestamps)).total_seconds()
            
            results.append({
                'cluster_id': cluster['id'],
                'sample_count': len(samples),
                'avg_peer_count': round(avg_peers, 1),
                'total_unique_peers': len(peer_set),
                'core_peers': core_peers,
                'duration_seconds': round(duration),
                'first_seen': min(timestamps).isoformat(),
                'last_seen': max(timestamps).isoformat()
            })
        
        # Sort by sample count (most watched channels first)
        results.sort(key=lambda x: x['sample_count'], reverse=True)
        
        return results
    
    def identify_current_channel(self, current_peers):
        """Identify which cluster/channel current peers belong to"""
        best_match = None
        best_overlap = 0
        
        for i, cluster in enumerate(self.clusters):
            overlap = len(current_peers & cluster['peer_set'])
            total = len(current_peers | cluster['peer_set'])
            
            if total > 0:
                overlap_pct = overlap / total
                if overlap_pct > best_overlap:
                    best_overlap = overlap_pct
                    best_match = i
        
        return best_match, best_overlap
    
    def save_model(self, output_file="/Users/apple/apex-exotics/sports-monitor/data/channel_model.json"):
        """Save cluster model for real-time identification"""
        model = {
            'clusters': [
                {
                    'id': c['id'],
                    'peer_set': list(c['peer_set']),
                    'sample_count': len(c['samples'])
                }
                for c in self.clusters
            ],
            'created': datetime.now().isoformat()
        }
        
        with open(output_file, 'w') as f:
            json.dump(model, f, indent=2)
        
        print(f"Model saved to {output_file}")

if __name__ == "__main__":
    classifier = ChannelClassifier()
    
    print("=== VSeeBox Channel Classifier ===\n")
    
    # Parse log
    samples = classifier.parse_log()
    
    if len(samples) < 10:
        print("Not enough data. Run background_monitor.py for a while first.")
        exit(1)
    
    # Cluster
    print("\nClustering samples...")
    clusters = classifier.cluster_by_similarity(threshold=0.3)
    
    # Analyze
    print("\nAnalyzing clusters...\n")
    results = classifier.analyze_clusters()
    
    print(f"{'ID':<5} {'Samples':<10} {'Avg Peers':<12} {'Duration':<12} {'Core Peers'}")
    print("-" * 80)
    
    for r in results:
        duration_min = r['duration_seconds'] / 60
        print(f"{r['cluster_id']:<5} {r['sample_count']:<10} {r['avg_peer_count']:<12} {duration_min:.1f}m{'':<8} {r['core_peers'][:2]}")
    
    # Save model
    classifier.save_model()
    
    print("\n✓ Model trained and saved!")
    print("Use this to identify channels in real-time.")
