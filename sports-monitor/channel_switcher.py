#!/usr/bin/env python3
"""
Channel switcher for VSeeBox via Broadlink
"""
import broadlink
import time
import sys
from broadlink_config import IR_CODES, BROADLINK_HOST

# Global device connection
_device = None

def get_device():
    """Get or create Broadlink device connection"""
    global _device
    if _device is None:
        devices = broadlink.discover(timeout=3)
        if not devices:
            raise Exception("Broadlink device not found")
        _device = devices[0]
        _device.auth()
    return _device

def send_ir_code(code_hex):
    """Send a single IR code"""
    device = get_device()
    code_bytes = bytes.fromhex(code_hex)
    device.send_data(code_bytes)
    time.sleep(0.3)  # Small delay after every IR send

def change_channel(channel, send_ok=False):
    """Change to specified channel number"""
    # Pad 3-digit channels with leading 0
    channel_str = str(channel).zfill(4) if len(str(channel)) == 3 else str(channel)
    
    print(f"Changing to channel {channel_str}...")
    
    # Send each digit
    for digit in channel_str:
        if digit in IR_CODES:
            print(f"  Sending digit: {digit}")
            send_ir_code(IR_CODES[digit])
            time.sleep(0.4)  # Faster digit entry
        else:
            print(f"  ❌ Digit {digit} not in IR_CODES!")
    
    # Optional OK (not needed for VSeeBox - auto-switches after 4 digits)
    if send_ok:
        time.sleep(2.0)
        send_ir_code(IR_CODES['OK'])
        print("  Sent OK")
    
    # Save current channel
    save_current_channel(int(channel))
    
    print(f"✅ Sent channel {channel_str}")
    return True

def save_current_channel(channel):
    """Save current channel to file with sport context"""
    import json
    
    # Map channels to sports
    channel_sport_map = {
        809: 'nba',      # ESPN - usually NBA
        810: 'nba',      # ESPN backup
        811: 'ncaa-basketball',  # ESPNU - college basketball
        812: 'ncaa-basketball',  # ESPN2 - college basketball  
        813: 'nba',      # ESPN Deportes
        814: 'ncaa-basketball',  # ESPNews - college basketball
        815: 'mlb',      # MLB Network
    }
    
    sport = channel_sport_map.get(channel, 'ncaa-basketball')
    
    try:
        with open('current_channel.json', 'w') as f:
            json.dump({
                'channel': channel, 
                'sport': sport,
                'timestamp': time.time()
            }, f)
    except:
        pass

def send_command(command):
    """Send a single command (UP, DOWN, LEFT, RIGHT, OK, etc)"""
    command = command.upper()
    if command in IR_CODES:
        print(f"Sending {command}...")
        send_ir_code(IR_CODES[command])
        time.sleep(1.0)  # Longer delay for UI to respond
        print(f"✅ Sent {command}")
        return True
    else:
        print(f"❌ Unknown command: {command}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 channel_switcher.py <channel_number|command>")
        print("Commands: UP, DOWN, LEFT, RIGHT, OK, HOME, BACK, MENU, EPG, CHANNEL-UP, CHANNEL-DOWN")
        sys.exit(1)
    
    arg = sys.argv[1]
    try:
        # Check if it's a command or channel number
        if arg.upper() in IR_CODES:
            send_command(arg)
        else:
            change_channel(arg)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
