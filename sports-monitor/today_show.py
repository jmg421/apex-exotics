#!/usr/bin/env python3
"""
Quick switch to Today Show for Christina
"""
from channel_switcher import change_channel, get_device

device = get_device()
print("📺 Switching to NBC for Today Show...")
change_channel(119)
print("✅ Enjoy the Today Show!")
