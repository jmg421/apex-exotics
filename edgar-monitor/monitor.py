#!/usr/bin/env python3
"""Automated Market Monitor - Stocks + Futures every 5 minutes"""
import subprocess
import time
from datetime import datetime

def is_market_hours():
    """Check if market is open (9:30 AM - 4:00 PM ET, Mon-Fri)"""
    now = datetime.now()
    
    # Skip weekends
    if now.weekday() >= 5:
        return False
    
    # Market hours: 9:30 AM - 4:00 PM ET
    market_open = now.replace(hour=9, minute=30, second=0)
    market_close = now.replace(hour=16, minute=0, second=0)
    
    return market_open <= now <= market_close

def run_scan(scan_type):
    """Run a market scan"""
    print(f"\n{'='*60}")
    print(f"🔴 {scan_type.upper()} SCAN - {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    
    if scan_type == 'stocks':
        subprocess.run(['python3', 'market_open_synthetic.py'])
        subprocess.run(['python3', 'detect_patterns.py'])
    elif scan_type == 'futures':
        subprocess.run(['python3', 'futures_scanner.py'])
        subprocess.run(['python3', 'futures_patterns.py'])

if __name__ == '__main__':
    print("🤖 AUTOMATED MARKET MONITOR")
    print("="*60)
    print("Scanning stocks + futures every 5 minutes")
    print("Press Ctrl+C to stop")
    print("="*60)
    
    scan_count = 0
    
    try:
        while True:
            if is_market_hours():
                scan_count += 1
                print(f"\n\n📊 SCAN #{scan_count}")
                
                # Run both scans
                run_scan('stocks')
                run_scan('futures')
                
                print(f"\n✅ Scan #{scan_count} complete. Next scan in 5 minutes...")
                time.sleep(300)  # 5 minutes
            else:
                print(f"\n⏸️  Market closed. Waiting... (checked at {datetime.now().strftime('%H:%M:%S')})")
                time.sleep(60)  # Check every minute
    
    except KeyboardInterrupt:
        print(f"\n\n🛑 Monitor stopped after {scan_count} scans")
