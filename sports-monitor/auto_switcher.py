#!/usr/bin/env python3
"""
Auto-Switcher - Changes VSeeBox channel based on upset alerts
Uses Broadlink RM4 Mini to send IR commands
"""
import broadlink
import time
import json

def should_auto_switch(game):
    """Check if game meets auto-switch criteria"""
    if not game.get('live', False):
        return False, None
    
    upset_score = game.get('Upset_Score', 0)
    if upset_score >= 7:
        return True, f"High upset potential (score: {upset_score})"
    
    return False, None

def get_top_upset_game(games, min_score=7):
    """Get highest priority game for auto-switching"""
    live_games = [g for g in games if g.get('live', False) and g.get('Upset_Score', 0) >= min_score]
    
    if not live_games:
        return None
    
    # Sort by upset score (highest first)
    return max(live_games, key=lambda g: g.get('Upset_Score', 0))

def check_and_switch(current_channel=None, auto_enabled=True):
    """Check for high-priority games and switch if needed"""
    if not auto_enabled:
        return {'switched': False, 'reason': 'Auto-switching disabled'}
    
    from march_madness_integration import get_upset_alerts
    
    games = get_upset_alerts()
    top_game = get_top_upset_game(games, min_score=7)
    
    if not top_game:
        return {'switched': False, 'reason': 'No high-priority games'}
    
    target_channel = top_game.get('channel')
    
    if not target_channel:
        return {'switched': False, 'reason': 'Game not on mapped channel'}
    
    if target_channel == current_channel:
        return {'switched': False, 'reason': 'Already on target channel'}
    
    # Return switch recommendation (actual switching done by frontend)
    return {
        'switched': True,
        'from_channel': current_channel,
        'to_channel': target_channel,
        'game': top_game['Matchup'],
        'upset_score': top_game['Upset_Score'],
        'reason': f"High upset potential (score: {top_game['Upset_Score']})"
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
