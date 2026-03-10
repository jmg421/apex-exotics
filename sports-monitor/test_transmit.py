#!/usr/bin/env python3
"""
Test IR transmit - replay captured code
"""
import sounddevice as sd
import numpy as np
import json

SAMPLE_RATE = 48000

# Load captured codes
with open('vseebox_ir_codes.json', 'r') as f:
    codes = json.load(f)

# Find External Headphones
devices = sd.query_devices()
for i, d in enumerate(devices):
    if 'External Headphones' in d['name']:
        output_device = i
        break

print("Testing IR transmit with OK button...")
print("Point IR diode at VSeeBox")
print("Sending OK command...")

# Get the captured signal
signal_data = np.array(codes['OK'])

# Amplify and play
signal_data = signal_data * 10  # Boost amplitude

sd.play(signal_data, samplerate=SAMPLE_RATE, device=output_device, blocking=True)

print("Done! Did the channel change?")
