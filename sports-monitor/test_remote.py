#!/usr/bin/env python3
"""
VSeeBox Android TV Remote Control
Sends channel commands over network
"""
import asyncio
from androidtvremote2 import AndroidTVRemote

VSEEBOX_IP = "10.0.0.55"

async def test_connection():
    """Test connection to VSeeBox"""
    print(f"Connecting to VSeeBox at {VSEEBOX_IP}...")
    
    remote = AndroidTVRemote(
        client_name="Sports Monitor",
        host=VSEEBOX_IP
    )
    
    try:
        await remote.async_connect()
        print("✓ Connected!")
        
        # Test: Send channel up command
        print("Sending CHANNEL_UP...")
        await remote.send_key_command("KEYCODE_CHANNEL_UP")
        
        await asyncio.sleep(1)
        
        print("Sending CHANNEL_DOWN...")
        await remote.send_key_command("KEYCODE_CHANNEL_DOWN")
        
        print("✓ Commands sent successfully!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nYou may need to pair first. Check VSeeBox for pairing prompt.")
    finally:
        await remote.async_disconnect()

if __name__ == "__main__":
    asyncio.run(test_connection())
