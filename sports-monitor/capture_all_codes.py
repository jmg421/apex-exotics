#!/usr/bin/env python3
"""
Capture IR codes for all VSeeBox remote buttons
"""
import sounddevice as sd
import numpy as np
from scipy import signal
import json

SAMPLE_RATE = 48000

def capture_button(button_name, duration=2):
    """Capture IR code for a specific button"""
    print(f"\n=== Capturing: {button_name} ===")
    print("Point remote at IR receiver and press the button NOW")
    input("Press Enter when ready...")
    
    # Record
    recording = sd.rec(int(duration * SAMPLE_RATE), 
                       samplerate=SAMPLE_RATE, 
                       channels=1,
                       dtype='float32')
    sd.wait()
    
    # Save raw signal
    signal_data = recording.flatten()
    
    print(f"✓ Captured {button_name}")
    return signal_data.tolist()

if __name__ == "__main__":
    print("=== VSeeBox Remote IR Code Capture ===\n")
    print("We'll capture codes for:")
    print("- CHANNEL_UP")
    print("- CHANNEL_DOWN")
    print("- Numbers 0-9")
    print()
    
    codes = {}
    
    # Capture essential buttons
    buttons = ['CHANNEL_UP', 'CHANNEL_DOWN', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    
    for button in buttons:
        codes[button] = capture_button(button)
    
    # Save to file
    with open('vseebox_ir_codes.json', 'w') as f:
        json.dump(codes, f)
    
    print("\n✓ All codes saved to vseebox_ir_codes.json")
    print("\nNow you need an IR transmitter to replay these codes.")
