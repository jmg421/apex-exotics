#!/usr/bin/env python3
"""
VSeeBox <-> Dashboard Auto-Sync
Polls VSeeBox channel and auto-selects matching game on dashboard
"""

import subprocess
import time
import json
import requests
import re

VSEEBOX_IP = "192.168.0.241:5555"
DASHBOARD_URL = "http://192.168.0.180:5001"
CHANNEL_OFFSET = 1800  # Channel 1805 = Event 5

def get_current_channel():
    """Get current VSeeBox channel by triggering logcat"""
    try:
        # Clear logcat
        subprocess.run(f"adb -s {VSEEBOX_IP} shell logcat -c", shell=True, capture_output=True, timeout=2)
        
        # Press channel down to trigger getCurSourceId
        subprocess.run(f"adb -s {VSEEBOX_IP} shell input keyevent KEYCODE_CHANNEL_DOWN", shell=True, capture_output=True, timeout=2)
        time.sleep(0.3)
        
        # Read logcat
        result = subprocess.run(f"adb -s {VSEEBOX_IP} shell logcat -d", shell=True, capture_output=True, text=True, timeout=2)
        
        # Extract SourceId
        match = re.search(r'SourceId:(\d+)', result.stdout)
        if match:
            return int(match.group(1))
    except subprocess.TimeoutExpired:
        print("  [timeout]")
    except Exception as e:
        print(f"  [error: {e}]")
    return None

def get_live_games():
    """Get current NHL games from ESPN"""
    try:
        resp = requests.get("http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard", timeout=5)
        data = resp.json()
        
        games = []
        for i, event in enumerate(data.get('events', []), 1):
            game_id = event['id']
            away = event['competitions'][0]['competitors'][1]['team']['abbreviation']
            home = event['competitions'][0]['competitors'][0]['team']['abbreviation']
            status = event['status']['type']['state']
            
            games.append({
                'event_num': i,
                'channel': CHANNEL_OFFSET + i,
                'game_id': game_id,
                'matchup': f"{away} @ {home}",
                'status': status
            })
        
        return games
    except Exception as e:
        print(f"Error fetching games: {e}")
        return []

def main():
    print("VSeeBox <-> Dashboard Auto-Sync")
    print("=" * 50)
    print()
    
    last_channel = None
    
    while True:
        try:
            # Get current channel
            channel = get_current_channel()
            
            if channel and channel != last_channel:
                # Calculate event number
                event_num = channel - CHANNEL_OFFSET
                
                # Get live games
                games = get_live_games()
                
                # Find matching game
                matching_game = next((g for g in games if g['event_num'] == event_num), None)
                
                if matching_game:
                    print(f"\n[{time.strftime('%H:%M:%S')}] Channel {channel} → {matching_game['matchup']}")
                    print(f"  Game ID: {matching_game['game_id']}")
                    print(f"  Status: {matching_game['status']}")
                    
                    # TODO: Send to dashboard to auto-select this game
                    # This would require adding an endpoint to dashboard.py
                    
                else:
                    print(f"\n[{time.strftime('%H:%M:%S')}] Channel {channel} (Event {event_num}) - No matching game")
                
                last_channel = channel
            
            time.sleep(5)  # Poll every 5 seconds
            
        except KeyboardInterrupt:
            print("\n\nStopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
