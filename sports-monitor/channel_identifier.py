#!/usr/bin/env python3
"""
VSeeBox Channel Identifier
Uses peer signatures to identify what channel is playing
"""
import subprocess
import json
import time
from datetime import datetime

class ChannelIdentifier:
    def __init__(self, map_file="/tmp/channel_map.json", device_ip="192.168.100.55", interface="en9"):
        self.device_ip = device_ip
        self.interface = interface
        self.channel_map = self.load_map(map_file)
        
    def load_map(self, map_file):
        """Load channel-to-peer mapping"""
        try:
            with open(map_file, 'r') as f:
                data = json.load(f)
            
            # Build peer signature database
            signatures = {}
            for entry in data:
                channel = entry['channel_name']
                # Extract just IPs (remove ports)
                peers = set([p.rsplit('.', 1)[0] if '.' in p else p for p in entry['peers']])
                
                if channel not in signatures:
                    signatures[channel] = []
                signatures[channel].append(peers)
            
            return signatures
        except Exception as e:
            print(f"Error loading map: {e}")
            return {}
    
    def get_current_peers(self):
        """Get current peer IPs"""
        cmd = f"sudo timeout 3 tcpdump -i {self.interface} -n -c 150 host {self.device_ip} 2>/dev/null"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        peers = set()
        for line in result.stdout.split('\n'):
            parts = line.split()
            if len(parts) < 5:
                continue
            
            if self.device_ip in parts[2]:
                remote = parts[4]
            else:
                remote = parts[2]
            
            if ':' in remote:
                ip = remote.rsplit(':', 1)[0]
                # Filter CDN/control
                if not any(x in ip for x in ['172.67', '104.26', '23.220', '8.8', '192.168']):
                    # Remove port from IP
                    clean_ip = '.'.join(ip.split('.')[:4])
                    peers.add(clean_ip)
        
        return peers
    
    def identify_channel(self, current_peers):
        """Match current peers to known channel"""
        if not current_peers:
            return None, 0
        
        best_match = None
        best_score = 0
        
        for channel, peer_sets in self.channel_map.items():
            for known_peers in peer_sets:
                # Calculate overlap
                overlap = len(current_peers & known_peers)
                total = len(current_peers | known_peers)
                
                if total > 0:
                    score = overlap / total
                    if score > best_score:
                        best_score = score
                        best_match = channel
        
        return best_match, best_score
    
    def run(self):
        """Monitor and identify channel in real-time"""
        print("VSeeBox Channel Identifier")
        print(f"Loaded {len(self.channel_map)} channels from map")
        print(f"\n{'Time':<12} {'Channel':<15} {'Confidence':<12} {'Peers'}")
        print("-" * 60)
        
        last_channel = None
        
        try:
            while True:
                peers = self.get_current_peers()
                channel, confidence = self.identify_channel(peers)
                now = datetime.now()
                
                if channel and confidence > 0.3:  # 30% confidence threshold
                    if channel != last_channel:
                        print(f"{now.strftime('%H:%M:%S'):<12} {channel:<15} {confidence*100:>5.1f}%       {len(peers)}")
                        last_channel = channel
                elif peers:
                    print(f"{now.strftime('%H:%M:%S'):<12} {'UNKNOWN':<15} {'---':<12} {len(peers)}")
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n\nStopped.")

if __name__ == "__main__":
    identifier = ChannelIdentifier()
    identifier.run()
