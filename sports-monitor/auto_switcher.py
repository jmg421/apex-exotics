#!/usr/bin/env python3
"""
Auto-Switcher - Changes VSeeBox channel based on excitement scores
Uses Broadlink RM4 Mini to send IR commands
"""
import broadlink
import time
import json
from excitement_engine import get_excitement_rankings

# Channel mapping (you'll need to map game IDs to VSeeBox channels)
CHANNEL_MAP = {
    # Example: 'game_id': 1805
}

def discover_broadlink():
    """Find Broadlink device on network"""
    print("Discovering Broadlink device...")
    devices = broadlink.discover(timeout=5)
    if not devices:
        print("No Broadlink device found!")
        return None
    
    device = devices[0]
    device.auth()
    print(f"✓ Found Broadlink at {device.host}")
    return device

def learn_ir_code(device, button_name):
    """Learn IR code from remote"""
    print(f"\nLearning {button_name}...")
    print("Press the button on VSeeBox remote now...")
    
    device.enter_learning()
    time.sleep(5)  # Wait for button press
    
    ir_code = device.check_data()
    if ir_code:
        print(f"✓ Learned {button_name}")
        return ir_code
    else:
        print(f"✗ Failed to learn {button_name}")
        return None

def send_channel_command(device, channel_number):
    """Send channel number via IR"""
    # Load learned codes
    with open('broadlink_codes.json', 'r') as f:
        codes = json.load(f)
    
    # Send each digit
    for digit in str(channel_number):
        device.send_data(codes[digit])
        time.sleep(0.3)
    
    print(f"✓ Sent channel {channel_number}")

def auto_switch_loop(device):
    """Main loop - check excitement and switch channels"""
    current_channel = None
    
    while True:
        # Get excitement rankings
        games = get_excitement_rankings()
        
        if not games:
            print("No live games")
            time.sleep(30)
            continue
        
        # Get most exciting game
        top_game = games[0]
        
        # Check if we need to switch
        if top_game['excitement'] > 80 and top_game.get('channel') != current_channel:
            print(f"\n🔥 Switching to {top_game['away']} @ {top_game['home']}")
            print(f"   Excitement: {top_game['excitement']}")
            print(f"   Channel: {top_game['channel']}")
            
            send_channel_command(device, top_game['channel'])
            current_channel = top_game['channel']
        
        time.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    print("=== VSeeBox Auto-Switcher ===\n")
    
    # Discover Broadlink
    device = discover_broadlink()
    if not device:
        exit(1)
    
    # Learn codes (run once)
    if input("Learn IR codes? (y/n): ").lower() == 'y':
        codes = {}
        for button in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'CHANNEL_UP', 'CHANNEL_DOWN']:
            code = learn_ir_code(device, button)
            if code:
                codes[button] = code.hex()
        
        with open('broadlink_codes.json', 'w') as f:
            json.dump(codes, f, indent=2)
        
        print("\n✓ All codes saved to broadlink_codes.json")
    
    # Start auto-switching
    print("\n🚀 Starting auto-switcher...")
    auto_switch_loop(device)
