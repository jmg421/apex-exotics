#!/usr/bin/env python3
"""Quick demo: rotate through sports channels every N seconds."""
import time, sys
from channel_switcher import change_channel

DEMO_CHANNELS = [
    (809, 'ESPN'),
    (811, 'ESPN2'),
    (812, 'ESPNU'),
    (156, 'TBS'),
    (162, 'TNT'),
    (166, 'truTV'),
    (816, 'NBA TV'),
    (860, 'FS1'),
]

interval = int(sys.argv[1]) if len(sys.argv) > 1 else 20

print(f"🎬 Demo mode: rotating {len(DEMO_CHANNELS)} channels every {interval}s")
print("   Ctrl+C to stop\n")

try:
    while True:
        for ch, name in DEMO_CHANNELS:
            print(f"📺 {name} (ch {ch})")
            change_channel(ch)
            time.sleep(interval)
except KeyboardInterrupt:
    print("\n🛑 Demo stopped")
