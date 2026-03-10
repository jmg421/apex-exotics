#!/usr/bin/env python3
"""
Real-time Channel Identifier using trained model
"""
import json
import subprocess
import time
from datetime import datetime

def get_current_peers(device_ip="192.168.100.55", interface="en9"):
    """Get current peer IPs"""
    cmd = f"sudo timeout 2 tcpdump -i {interface} -n -c 100 host {device_ip} 2>/dev/null"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    peers = set()
    for line in result.stdout.split('\n'):
        parts = line.split()
        if len(parts) < 5:
            continue
        
        if device_ip in parts[2]:
            remote = parts[4]
        else:
            remote = parts[2]
        
        if ':' in remote:
            ip = '.'.join(remote.rsplit(':', 1)[0].split('.')[:4])
            if not any(x in ip for x in ['172.67', '104.26', '23.220', '8.8', '192.168']):
                peers.add(ip)
    
    return peers

def load_model(model_file="/Users/apple/apex-exotics/sports-monitor/data/channel_model.json"):
    """Load trained model"""
    with open(model_file, 'r') as f:
        return json.load(f)

def identify_channel(current_peers, model):
    """Identify channel from current peers"""
    best_match = None
    best_overlap = 0
    
    for cluster in model['clusters']:
        cluster_peers = set(cluster['peer_set'])
        
        overlap = len(current_peers & cluster_peers)
        total = len(current_peers | cluster_peers)
        
        if total > 0:
            overlap_pct = overlap / total
            if overlap_pct > best_overlap:
                best_overlap = overlap_pct
                best_match = cluster['id']
    
    return best_match, best_overlap

if __name__ == "__main__":
    print("Loading model...")
    model = load_model()
    print(f"Loaded {len(model['clusters'])} channel signatures\n")
    
    print(f"{'Time':<12} {'Cluster ID':<12} {'Confidence':<12} {'Peers'}")
    print("-" * 60)
    
    last_cluster = None
    
    try:
        while True:
            peers = get_current_peers()
            
            if len(peers) >= 3:
                cluster_id, confidence = identify_channel(peers, model)
                
                if confidence > 0.3:  # 30% confidence threshold
                    if cluster_id != last_cluster:
                        print(f"{datetime.now().strftime('%H:%M:%S'):<12} {cluster_id:<12} {confidence*100:>5.1f}%       {len(peers)}")
                        last_cluster = cluster_id
                else:
                    if last_cluster is not None:
                        print(f"{datetime.now().strftime('%H:%M:%S'):<12} {'UNKNOWN':<12} {'---':<12} {len(peers)}")
                        last_cluster = None
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\nStopped.")
