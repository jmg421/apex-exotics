#!/usr/bin/env python3
"""
VSeeBox Background Monitor - Logs peer changes automatically
"""
import subprocess
import json
import time
from datetime import datetime
from collections import deque

class BackgroundMonitor:
    def __init__(self, device_ip="192.168.100.55", interface="en9"):
        self.device_ip = device_ip
        self.interface = interface
        self.peer_history = deque(maxlen=10)
        self.change_log = []
        self.log_file = "/Users/apple/apex-exotics/sports-monitor/data/peer_changes.log"
        
    def get_peers(self):
        """Get current peer set"""
        cmd = f"sudo timeout 2 tcpdump -i {self.interface} -n -c 100 host {self.device_ip} 2>/dev/null"
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
                if not any(x in ip for x in ['172.67', '104.26', '23.220', '8.8', '192.168']):
                    peers.add(ip)
        
        return peers
    
    def detect_change(self, new_peers):
        """Detect significant peer change based on IP overlap"""
        if not self.peer_history or len(self.peer_history) < 3:
            return False
        
        # Get recent peer set (last 3 samples combined)
        recent_peers = set()
        for peer_set in list(self.peer_history)[-3:]:
            recent_peers.update(peer_set)
        
        if not recent_peers or not new_peers:
            return False
        
        # Calculate overlap percentage
        overlap = len(new_peers & recent_peers)
        total = len(new_peers | recent_peers)
        
        if total == 0:
            return False
        
        overlap_pct = overlap / total
        
        # Need stable peer counts to detect reliably
        if len(new_peers) < 5 or len(recent_peers) < 10:
            return False
        
        # If less than 20% overlap, it's a real channel change
        return overlap_pct < 0.2
    
    def log_change(self, peers):
        """Log peer change"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'peer_count': len(peers),
            'sample_peers': list(peers)[:5]
        }
        
        self.change_log.append(entry)
        
        # Append to file
        with open(self.log_file, 'a') as f:
            f.write(f"\n{entry['timestamp']} - {entry['peer_count']} peers\n")
            f.write(f"  Sample: {entry['sample_peers']}\n")
        
        print(f"{entry['timestamp']}: Channel change detected ({entry['peer_count']} peers)")
    
    def run(self):
        """Run background monitoring"""
        print(f"VSeeBox Background Monitor")
        print(f"Logging to: {self.log_file}")
        print(f"Monitoring {self.device_ip} on {self.interface}")
        print("Press Ctrl+C to stop\n")
        
        # Clear log file
        with open(self.log_file, 'w') as f:
            f.write(f"VSeeBox Peer Change Log - Started {datetime.now().isoformat()}\n")
            f.write("=" * 60 + "\n")
        
        try:
            while True:
                peers = self.get_peers()
                
                if peers:
                    # Calculate overlap for debugging
                    if len(self.peer_history) >= 3:
                        recent_peers = set()
                        for peer_set in list(self.peer_history)[-3:]:
                            recent_peers.update(peer_set)
                        
                        overlap = len(peers & recent_peers)
                        total = len(peers | recent_peers)
                        overlap_pct = (overlap / total * 100) if total > 0 else 0
                        
                        print(f"{datetime.now().strftime('%H:%M:%S')} - {len(peers)} peers, {overlap_pct:.0f}% overlap", flush=True)
                    else:
                        print(f"{datetime.now().strftime('%H:%M:%S')} - {len(peers)} peers (warming up)", flush=True)
                    
                    if self.detect_change(peers):
                        self.log_change(peers)
                    
                    self.peer_history.append(peers)
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print(f"\n\nStopped. Logged {len(self.change_log)} channel changes.")
            print(f"Log saved to: {self.log_file}")

if __name__ == "__main__":
    monitor = BackgroundMonitor()
    monitor.run()
