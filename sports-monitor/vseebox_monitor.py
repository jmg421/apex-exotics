#!/usr/bin/env python3
"""
VSeeBox Channel Monitor
Watches logcat for channel changes and identifies the game
"""

import subprocess
import json
import requests
import re
import sys

CHANNEL_OFFSET = 1800

def get_live_games():
    """Get current NHL games from ESPN"""
    try:
        resp = requests.get("http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard", timeout=5)
        data = resp.json()
        
        games = {}
        for i, event in enumerate(data.get('events', []), 1):
            game_id = event['id']
            away = event['competitions'][0]['competitors'][1]['team']['abbreviation']
            home = event['competitions'][0]['competitors'][0]['team']['abbreviation']
            
            channel = CHANNEL_OFFSET + i
            games[channel] = {
                'game_id': game_id,
                'matchup': f"{away} @ {home}"
            }
        
        return games
    except Exception as e:
        print(f"Error fetching games: {e}", file=sys.stderr)
        return {}

def main():
    print("VSeeBox Channel Monitor")
    print("=" * 50)
    print("Watching for channel changes...")
    print("(Press CH⬇️ on VSeeBox to detect current channel)")
    print()
    
    games = get_live_games()
    
    # Stream logcat and watch for SourceId
    proc = subprocess.Popen(
        ["adb", "-s", "192.168.0.241:5555", "shell", "logcat"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1
    )
    
    try:
        for line in proc.stdout:
            if "getCurSourceId" in line:
                match = re.search(r'SourceId:(\d+)', line)
                if match:
                    channel = int(match.group(1))
                    
                    if channel in games:
                        game = games[channel]
                        print(f"\n🏒 Channel {channel}: {game['matchup']}")
                        print(f"   Game ID: {game['game_id']}")
                    else:
                        print(f"\n📺 Channel {channel} (not an NHL game)")
    
    except KeyboardInterrupt:
        print("\n\nStopped.")
    finally:
        proc.terminate()

if __name__ == "__main__":
    main()
