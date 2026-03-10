#!/usr/bin/env python3
"""
VSeeBox Stream Metadata Monitor
Tracks P2P CDN connections to identify channel changes
"""
import subprocess
import json
from datetime import datetime
from collections import defaultdict

class StreamMonitor:
    def __init__(self, device_ip="192.168.100.55", interface="en9"):
        self.device_ip = device_ip
        self.interface = interface
        self.connections = defaultdict(lambda: {
            "first_seen": None,
            "last_seen": None,
            "packets": 0,
            "bytes": 0
        })
        
    def run(self):
        cmd = ["sudo", "tcpdump", "-i", self.interface, "-n", "-l", 
               "host", self.device_ip]
        
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                               stderr=subprocess.DEVNULL, text=True)
        
        print(f"Monitoring {self.device_ip} on {self.interface}...")
        print(f"{'Time':<10} {'Event':<8} {'Remote IP':<18} {'Port':<8} {'Active Peers'}")
        print("-" * 70)
        
        try:
            for line in proc.stdout:
                self._process_packet(line)
        except KeyboardInterrupt:
            self._print_summary()
        finally:
            proc.terminate()
    
    def _process_packet(self, line):
        now = datetime.now()
        parts = line.split()
        
        if len(parts) < 5:
            return
        
        # Extract remote IP and port
        if self.device_ip in parts[2]:
            remote = parts[4]
        else:
            remote = parts[2]
        
        if ":" not in remote:
            return
            
        remote_ip = remote.rsplit(":", 1)[0]
        remote_port = remote.rsplit(":", 1)[1].rstrip(":")
        
        key = f"{remote_ip}:{remote_port}"
        
        # New connection
        if self.connections[key]["first_seen"] is None:
            self.connections[key]["first_seen"] = now
            active = len([c for c in self.connections.values() 
                         if c["last_seen"] and 
                         (now - c["last_seen"]).seconds < 5])
            print(f"{now.strftime('%H:%M:%S'):<10} {'NEW':<8} {remote_ip:<18} {remote_port:<8} {active}")
        
        self.connections[key]["last_seen"] = now
        self.connections[key]["packets"] += 1
    
    def _print_summary(self):
        print("\n" + "=" * 70)
        print("Session Summary")
        print("=" * 70)
        print(f"Total unique peers: {len(self.connections)}")
        
        # Active connections (seen in last 10 seconds)
        now = datetime.now()
        active = [k for k, v in self.connections.items() 
                 if v["last_seen"] and (now - v["last_seen"]).seconds < 10]
        print(f"Currently active: {len(active)}")
        
        if active:
            print("\nActive peers:")
            for peer in active[:10]:
                print(f"  {peer}")

if __name__ == "__main__":
    monitor = StreamMonitor()
    monitor.run()
