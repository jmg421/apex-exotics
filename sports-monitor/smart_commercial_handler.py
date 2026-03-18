#!/usr/bin/env python3
"""
Smart Commercial Break Handler
Detects commercials and switches to most exciting game
"""
import json
import time
from commercial_integration import check_commercial_break
from excitement_engine import get_excitement_rankings
from channel_switcher import change_channel

# Channel to sport mapping
CHANNEL_MAP = {
    809: 'ESPN',
    810: 'ESPN',
    811: 'ESPN2',
    812: 'ESPNU',
    813: 'ESPN Deportes',
    814: 'ESPNews',
    815: 'MLB Network'
}

def get_current_channel():
    """Get currently tuned channel"""
    try:
        with open('data/current_channel.json', 'r') as f:
            data = json.load(f)
            return data.get('channel')
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error reading channel state: {e}")
        return None

def save_original_channel(channel):
    """Save the channel we're switching away from"""
    with open('data/original_channel.json', 'w') as f:
        json.dump({'channel': channel, 'timestamp': time.time()}, f)

def get_original_channel():
    """Get the channel we switched away from"""
    try:
        with open('data/original_channel.json', 'r') as f:
            data = json.load(f)
            # Only return if less than 10 minutes old
            if time.time() - data.get('timestamp', 0) < 600:
                return data.get('channel')
    except:
        pass
    return None

def find_best_alternative_channel():
    """Find most exciting game on a different channel"""
    current = get_current_channel()
    
    # Hardcoded channel options for demo
    alternative_channels = {
        809: {'name': 'ESPN', 'game': 'Live Game'},
        810: {'name': 'ESPN', 'game': 'Live Game'},
        812: {'name': 'ESPNU', 'game': 'Live Game'},
        813: {'name': 'ESPN Deportes', 'game': 'Live Game'},
        814: {'name': 'ESPNews', 'game': 'Live Game'}
    }
    
    # Remove current channel
    if current in alternative_channels:
        del alternative_channels[current]
    
    # Pick first alternative
    if alternative_channels:
        channel = list(alternative_channels.keys())[0]
        info = alternative_channels[channel]
        return {
            'channel': channel,
            'game': f"{info['name']} - {info['game']}",
            'excitement': 75,
            'score': 'Live'
        }
    
    return None

def detect_break_type(image_path=None):
    """Detect what type of break this is (timeout, halftime, commercial)"""
    import subprocess
    import re
    from lower_third_ocr import capture_lower_third
    
    # Capture scoreboard area (lower third has game status)
    if not image_path:
        image_path = capture_lower_third()
        if not image_path:
            return {'break_type': 'unknown', 'duration_estimate': 120}
    
    prompt = f"Look at {image_path}. What does the game status say? Answer with ONE of: HALFTIME, TIMEOUT, COMMERCIAL, LIVE, or UNKNOWN"
    
    try:
        result = subprocess.run(
            ['timeout', '30', 'kiro-cli', 'chat', '--no-interactive', '--trust-all-tools', prompt],
            capture_output=True,
            text=True,
            cwd='/Users/apple/apex-exotics/sports-monitor'
        )
        
        output = result.stdout.strip().upper()
        output = re.sub(r'\x1b\[[0-9;]*m', '', output)
        
        # Determine break type and estimated duration
        if 'HALFTIME' in output or 'HALF TIME' in output:
            return {'break_type': 'halftime', 'duration_estimate': 900}  # 15 min
        elif 'TIMEOUT' in output or 'TIME OUT' in output:
            return {'break_type': 'timeout', 'duration_estimate': 60}  # 1 min
        elif 'COMMERCIAL' in output:
            return {'break_type': 'commercial', 'duration_estimate': 180}  # 3 min
        elif 'LIVE' in output:
            return {'break_type': 'live', 'duration_estimate': 0}
        else:
            return {'break_type': 'unknown', 'duration_estimate': 120}  # 2 min default
            
    except Exception as e:
        return {'break_type': 'unknown', 'duration_estimate': 120, 'error': str(e)}

def handle_commercial_break():
    """Main logic: detect commercial and switch channels"""
    print("🔍 Checking for commercial...")
    
    # Detect commercial
    result = check_commercial_break()
    
    if not result.get('is_commercial'):
        print(f"✅ Game content detected: {result.get('commercial_type', 'Live')}")
        return {
            'action': 'none',
            'reason': 'No commercial detected'
        }
    
    commercial_name = result.get('commercial_type', 'Unknown').lower()
    print(f"🚫 COMMERCIAL DETECTED: {commercial_name}")
    
    # Pharmaceutical commercial blacklist - instant switch
    pharma_keywords = ['skyrizi', 'humira', 'ozempic', 'wegovy', 'dupixent', 
                       'rinvoq', 'xeljanz', 'otezla', 'tremfya', 'cosentyx',
                       'pharmaceutical', 'prescription', 'side effects']
    
    is_pharma = any(keyword in commercial_name for keyword in pharma_keywords)
    
    if is_pharma:
        print("💊 PHARMACEUTICAL AD DETECTED - INSTANT SWITCH!")
        duration = 180  # Assume 3 min
        break_type = 'pharma_commercial'
    else:
        # Detect break type and duration for other commercials
        break_info = detect_break_type()
        break_type = break_info['break_type']
        duration = break_info['duration_estimate']
        
        print(f"⏱️  Break type: {break_type.upper()} (estimated {duration}s)")
        
        # Decision logic based on break duration
        if duration < 90:
            print("⏭️  Short break - staying on current channel")
            return {
                'action': 'stay',
                'reason': f'Break too short ({duration}s)',
                'break_type': break_type,
                'commercial': commercial_name
            }
    
    # Save current channel before switching
    current_channel = get_current_channel()
    if current_channel:
        save_original_channel(current_channel)
    
    # Find best alternative
    alternative = find_best_alternative_channel()
    
    if not alternative:
        print("⚠️  No alternative games found")
        return {
            'action': 'none',
            'reason': 'No alternative games available',
            'break_type': break_type
        }
    
    print(f"🎯 Switching to: {alternative['game']} (Channel {alternative['channel']})")
    print(f"   Excitement: {alternative['excitement']}/100 | Score: {alternative['score']}")
    
    if is_pharma:
        print(f"   🚫 Censoring pharmaceutical ad")
    else:
        print(f"   Will monitor for {duration}s before checking return")
    
    # Switch channel
    change_channel(alternative['channel'])
    
    return {
        'action': 'switched',
        'from_channel': current_channel,
        'to_channel': alternative['channel'],
        'commercial': commercial_name,
        'break_type': break_type,
        'duration_estimate': duration,
        'new_game': alternative['game'],
        'excitement': alternative['excitement'],
        'pharma_blocked': is_pharma
    }

if __name__ == "__main__":
    result = handle_commercial_break()
    print(f"\n📊 Result: {json.dumps(result, indent=2)}")
