#!/usr/bin/env python3
"""
IR Transmitter via Headphone Jack
Sends IR commands to VSeeBox using audio output
"""
import numpy as np
import sounddevice as sd

# IR carrier frequency (standard for most remotes)
CARRIER_FREQ = 38000  # 38kHz
SAMPLE_RATE = 192000  # High sample rate for accuracy

def generate_carrier(duration_ms):
    """Generate 38kHz carrier wave"""
    duration_s = duration_ms / 1000.0
    t = np.linspace(0, duration_s, int(SAMPLE_RATE * duration_s))
    carrier = np.sin(2 * np.pi * CARRIER_FREQ * t)
    return carrier

def encode_nec_command(address, command):
    """
    Encode NEC IR protocol (common for Android TV remotes)
    Format: 9ms burst, 4.5ms space, then data bits
    """
    signal = []
    
    # Start burst: 9ms on, 4.5ms off
    signal.append(generate_carrier(9))
    signal.append(np.zeros(int(SAMPLE_RATE * 0.0045)))
    
    # Encode address (8 bits) + inverse
    data = address | (address ^ 0xFF) << 8 | command << 16 | (command ^ 0xFF) << 24
    
    # Send 32 bits
    for i in range(32):
        bit = (data >> i) & 1
        # Bit encoding: 0.56ms burst + (0.56ms space for 0, 1.69ms space for 1)
        signal.append(generate_carrier(0.56))
        if bit:
            signal.append(np.zeros(int(SAMPLE_RATE * 0.00169)))
        else:
            signal.append(np.zeros(int(SAMPLE_RATE * 0.00056)))
    
    # Final burst
    signal.append(generate_carrier(0.56))
    
    return np.concatenate(signal)

def send_ir_command(address, command):
    """Send IR command through headphone jack"""
    signal = encode_nec_command(address, command)
    
    # Normalize to prevent clipping
    signal = signal / np.max(np.abs(signal)) * 0.9
    
    print(f"Sending IR command: Address=0x{address:02X}, Command=0x{command:02X}")
    # Use External Headphones device
    sd.play(signal, samplerate=SAMPLE_RATE, device=5, blocking=True)
    print("✓ Sent")

# Common Android TV NEC codes (you'll need to find VSeeBox specific ones)
COMMANDS = {
    'CHANNEL_UP': 0x1B,
    'CHANNEL_DOWN': 0x1F,
    'VOLUME_UP': 0x02,
    'VOLUME_DOWN': 0x03,
    'POWER': 0x12,
    'OK': 0x17,
    'UP': 0x40,
    'DOWN': 0x41,
    'LEFT': 0x42,
    'RIGHT': 0x43,
}

if __name__ == "__main__":
    # Test: Send channel up command
    # Address 0x00 is common for generic Android TV remotes
    # You may need to find the correct address for VSeeBox
    
    print("Testing IR transmitter...")
    print("Make sure IR LED is pointed at VSeeBox")
    print()
    
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1].upper()
        if cmd in COMMANDS:
            send_ir_command(0x00, COMMANDS[cmd])
        else:
            print(f"Unknown command: {cmd}")
            print(f"Available: {', '.join(COMMANDS.keys())}")
    else:
        print("Usage: python ir_transmitter.py CHANNEL_UP")
        print(f"Available commands: {', '.join(COMMANDS.keys())}")
