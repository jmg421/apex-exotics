#!/usr/bin/env python3
"""
Demo: Cycle through ESPN channels automatically
"""
import time
from channel_switcher import change_channel, get_device

# Very diverse channels - different content types
CHANNELS = [
    (37, "CNN - News"),
    (26, "Cartoon Network - Kids"),
    (61, "Food Network - Cooking"),
    (94, "HGTV - Home"),
    (180, "Weather Channel"),
    (220, "Turner Classic Movies"),
    (828, "ESPN - Sports"),
    (48, "Discovery - Nature"),
    (66, "Fox News - News"),
    (52, "Disney Channel - Kids"),
]

def demo_channel_switching():
    """Demo automatic channel switching"""
    device = get_device()
    
    print("🎬 ESPN Channel Switching Demo")
    print("=" * 50)
    print("\nCycling through sports channels... (Press Ctrl+C to stop)\n")
    
    cycle = 0
    while True:
        cycle += 1
        print(f"\n--- Cycle {cycle} ---\n")
        
        for channel, name in CHANNELS:
            print(f"📺 Switching to {name} (Channel {channel})")
            time.sleep(1)  # Wait before starting channel change
            change_channel(channel)
            print(f"   ⏱️  Showing for 5 seconds...\n")
            time.sleep(5)

if __name__ == '__main__':
    try:
        demo_channel_switching()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo stopped")
