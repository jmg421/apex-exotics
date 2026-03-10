#!/usr/bin/env python3
"""
VSeeBox Channel Detector - No ADB Required
Detects channel changes by monitoring P2P peer rotation
"""
import subprocess
import time
from datetime import datetime
from collections import defaultdict

class ChannelDetector:
    def __init__(self, device_ip="192.168.100.55", interface="en9"):
        self.device_ip = device_ip
        self.interface = interface
        self.current_peers = set()
        self.peer_history = []
        self.channel_changes = []
        
    def get_active_peers(self):
        """Get current set of peer IPs"""
        cmd = f"sudo timeout 2 tcpdump -i {self.interface} -n -c 100 host {self.device_ip} 2>/dev/null"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        peers = set()
        for line in result.stdout.split('\n'):
            parts = line.split()
            if len(parts) < 5:
                continue
            
            # Extract remote IP
            if self.device_ip in parts[2]:
                remote = parts[4]
            else:
                remote = parts[2]
            
            if ':' in remote:
                ip = remote.rsplit(':', 1)[0]
                # Filter out CDN/control IPs
                if not any(x in ip for x in ['172.67', '104.26', '23.220', '8.8.8.8', '192.168']):
                    peers.add(ip)
        
        return peers
    
    def detect_channel_change(self, new_peers):
        """Detect if peer set changed significantly (likely channel change)"""
        if not self.current_peers:
            return False
        
        # Calculate peer churn
        added = new_peers - self.current_peers
        removed = self.current_peers - new_peers
        
        # If >50% of peers changed, likely a channel change
        total_change = len(added) + len(removed)
        total_peers = len(self.current_peers) + len(new_peers)
        
        if total_peers == 0:
            return False
        
        churn_rate = total_change / total_peers
        
        return churn_rate > 0.5 and len(added) > 3
    
    def run(self):
        """Monitor peer changes in real-time"""
        print(f"Monitoring {self.device_ip} on {self.interface}")
        print("Detecting channel changes via P2P peer rotation...")
        print("\nInstructions:")
        print("  - Change channels on VSeeBox")
        print("  - When prompted, type the channel name/number")
        print("  - Press Ctrl+C when done to save results\n")
        print(f"{'Time':<12} {'Event':<15} {'Active Peers':<15} {'Churn %'}")
        print("-" * 60)
        
        channel_num = 1
        pending_input = False
        
        try:
            while True:
                new_peers = self.get_active_peers()
                now = datetime.now()
                
                if new_peers:
                    if self.detect_channel_change(new_peers):
                        added = new_peers - self.current_peers
                        removed = self.current_peers - new_peers
                        total_change = len(added) + len(removed)
                        total_peers = len(self.current_peers) + len(new_peers)
                        churn_pct = int((total_change / total_peers) * 100) if total_peers > 0 else 0
                        
                        print(f"\n{now.strftime('%H:%M:%S'):<12} {'🔴 CHANNEL_CHANGE':<15} {len(new_peers):<15} {churn_pct}%")
                        print(f"    Sample peers: {list(new_peers)[:3]}")
                        
                        # Get user input
                        channel_name = input("    >>> Channel name/number: ").strip()
                        
                        # Log the event
                        self.channel_changes.append({
                            'time': now,
                            'channel_num': channel_num,
                            'channel_name': channel_name,
                            'peers': list(new_peers),
                            'peer_count': len(new_peers),
                            'sample_peers': list(new_peers)[:5]
                        })
                        
                        print(f"    ✓ Logged as channel #{channel_num}: {channel_name}\n")
                        channel_num += 1
                    
                    self.current_peers = new_peers
                
                time.sleep(5)  # Longer interval for stability
                
        except KeyboardInterrupt:
            self.save_results()
    
    def save_results(self):
        """Save channel change log"""
        print("\n\n=== Session Summary ===")
        print(f"Detected {len(self.channel_changes)} channel changes\n")
        
        # Display summary
        for change in self.channel_changes:
            print(f"  {change['channel_num']}. {change['channel_name']:<20} ({change['peer_count']} peers)")
        
        # Save detailed log
        with open('/tmp/channel_changes.log', 'w') as f:
            f.write("VSeeBox Channel Mapping\n")
            f.write("=" * 60 + "\n\n")
            for change in self.channel_changes:
                f.write(f"Channel: {change['channel_name']}\n")
                f.write(f"  Time: {change['time'].isoformat()}\n")
                f.write(f"  Peer Count: {change['peer_count']}\n")
                f.write(f"  Sample Peers: {change['sample_peers']}\n")
                f.write("\n")
        
        # Save JSON for programmatic use
        import json
        with open('/tmp/channel_map.json', 'w') as f:
            json.dump(self.channel_changes, f, indent=2, default=str)
        
        print("\nLogs saved:")
        print("  /tmp/channel_changes.log")
        print("  /tmp/channel_map.json")

if __name__ == "__main__":
    detector = ChannelDetector()
    detector.run()
