#!/usr/bin/env python3
"""
VSeeBox Channel Monitor - Integration with Dashboard
Logs current channel based on manual input + peer patterns
"""
import subprocess
import json
import time
from datetime import datetime
from collections import deque

class ChannelMonitor:
    def __init__(self, device_ip="192.168.100.55", interface="en9"):
        self.device_ip = device_ip
        self.interface = interface
        self.peer_history = deque(maxlen=10)
        self.current_channel = None
        self.log_file = "/Users/apple/apex-exotics/sports-monitor/data/current_channel.json"
        self.channels = self.load_channels()
        
    def load_channels(self):
        """Load VSeeBox channel database"""
        try:
            with open('/Users/apple/apex-exotics/sports-monitor/data/vseebox_channels.json', 'r') as f:
                return json.load(f)
        except:
            return {}
        
    def get_peer_count(self):
        """Get current peer count"""
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
        
        return len(peers)
    
    def detect_change(self):
        """Detect if channel likely changed based on peer count variance"""
        if len(self.peer_history) < 5:
            return False
        
        recent = list(self.peer_history)[-5:]
        avg = sum(recent) / len(recent)
        current = self.peer_history[-1]
        
        # Large deviation = likely channel change
        if abs(current - avg) > 5:
            return True
        return False
    
    def log_channel(self, channel_input):
        """Log current channel to file for dashboard"""
        # Try to parse as number
        try:
            channel_num = int(channel_input)
            if str(channel_num) in self.channels:
                channel_info = self.channels[str(channel_num)]
                channel_name = f"{channel_num} - {channel_info['name']}"
            else:
                channel_name = str(channel_num)
        except:
            channel_name = channel_input
        
        data = {
            'channel': channel_name,
            'channel_number': channel_input,
            'timestamp': datetime.now().isoformat(),
            'peer_count': self.peer_history[-1] if self.peer_history else 0
        }
        
        with open(self.log_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def run(self):
        """Interactive monitoring"""
        print("VSeeBox Channel Monitor")
        print(f"Loaded {len(self.channels)} channels from database")
        print("\nCommands:")
        print("  Type channel number to log (e.g., 815)")
        print("  'status' - show current status")
        print("  'quit' - exit")
        print()
        
        import threading
        import sys
        
        def monitor_peers():
            while True:
                count = self.get_peer_count()
                self.peer_history.append(count)
                
                if self.detect_change():
                    print(f"\n⚠️  Peer count changed significantly ({count} peers) - channel may have changed")
                    print(f"Current: {self.current_channel or 'UNKNOWN'}")
                    print(">>> ", end='', flush=True)
                
                time.sleep(5)
        
        # Start background monitoring
        thread = threading.Thread(target=monitor_peers, daemon=True)
        thread.start()
        
        print("Monitoring started. Type channel name when you change channels:\n")
        
        try:
            while True:
                user_input = input(">>> ").strip()
                
                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'status':
                    print(f"Current channel: {self.current_channel or 'UNKNOWN'}")
                    print(f"Peer count: {self.peer_history[-1] if self.peer_history else 0}")
                    print(f"Recent history: {list(self.peer_history)[-5:]}")
                elif user_input:
                    self.current_channel = user_input
                    self.log_channel(user_input)
                    print(f"✓ Logged channel: {user_input}")
        
        except KeyboardInterrupt:
            pass
        
        print("\nStopped.")

if __name__ == "__main__":
    monitor = ChannelMonitor()
    monitor.run()
