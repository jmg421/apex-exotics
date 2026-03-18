#!/Users/apple/apex-exotics/venv/bin/python
"""
Channel switcher for VSeeBox via Broadlink
"""
import broadlink
import time
import sys
from broadlink_config import IR_CODES, BROADLINK_HOST

# Global device connection
_device = None

def get_device(retries=3):
    """Get or create Broadlink device connection, with retry on failure"""
    global _device
    if _device is None:
        for attempt in range(retries):
            try:
                _device = broadlink.hello(BROADLINK_HOST)
                _device.auth()
                return _device
            except Exception as e:
                if attempt < retries - 1:
                    print(f"⚠️  Connection failed ({e}), retrying in 5s... ({attempt+1}/{retries})")
                    time.sleep(5)
                else:
                    raise
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
        with open('data/current_channel.json', 'w') as f:
            json.dump({
                'channel': channel, 
                'sport': sport,
                'timestamp': time.time()
            }, f)
    except Exception as e:
        print(f"Error saving channel state: {e}")

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
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Control VSeeBox via Broadlink IR',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='action', help='Action to perform')
    
    # Channel subcommand
    channel_parser = subparsers.add_parser('channel', help='Change to a channel')
    channel_parser.add_argument('number', type=int, help='Channel number (e.g., 809)')
    channel_parser.add_argument('--ok', action='store_true', help='Send OK after digits')
    
    # Command subcommand
    cmd_parser = subparsers.add_parser('command', help='Send remote control command')
    cmd_parser.add_argument('name', choices=list(IR_CODES.keys()), help='Command name')
    
    args = parser.parse_args()
    
    if not args.action:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.action == 'channel':
            change_channel(args.number, send_ok=args.ok)
        elif args.action == 'command':
            send_command(args.name)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
