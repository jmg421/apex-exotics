#!/usr/bin/env python3
"""
Continuous OCR Monitor - Captures headlines every 30 seconds
"""
import time
import requests
from datetime import datetime

DASHBOARD_URL = "http://localhost:5001"
CAPTURE_INTERVAL = 30

def capture_headline():
    """Trigger OCR capture and save to database"""
    try:
        response = requests.get(f"{DASHBOARD_URL}/api/stream_ocr", timeout=60)
        data = response.json()
        
        if data.get('success'):
            headline = data.get('game_info', {}).get('next_game', '')
            if headline and '📰' in headline:
                headline = headline.replace('📰 ', '').strip()
                timestamp = datetime.now().strftime('%H:%M:%S')
                print(f"[{timestamp}] ✅ {headline[:60]}...")
                return True
        
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🎥 OCR Monitor - Capturing every 30 seconds")
    print("=" * 60)
    print()
    
    cycle = 0
    while True:
        cycle += 1
        print(f"Cycle {cycle}")
        capture_headline()
        print(f"   Waiting {CAPTURE_INTERVAL}s...\n")
        time.sleep(CAPTURE_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 OCR Monitor Stopped")
