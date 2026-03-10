#!/usr/bin/env python3
"""
Test A/V jack control - send signals from Mac to VSeeBox A/V port
"""
import numpy as np
import sounddevice as sd

def send_test_signal():
    """Send various test frequencies to see if VSeeBox responds"""
    
    # Find External Headphones
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        if 'External Headphones' in d['name']:
            output_device = i
            break
    
    print("Connect 3.5mm cable: Mac headphone → VSeeBox A/V port")
    input("Press Enter when connected...")
    
    # Test various frequencies
    test_freqs = [38000, 40000, 56000, 455000]  # Common IR/control frequencies
    
    for freq in test_freqs:
        print(f"\nSending {freq}Hz signal for 2 seconds...")
        print("Watch VSeeBox for any response...")
        
        duration = 2.0
        sample_rate = 192000
        t = np.linspace(0, duration, int(sample_rate * duration))
        signal = np.sin(2 * np.pi * freq * t) * 0.8
        
        sd.play(signal, samplerate=sample_rate, device=output_device, blocking=True)
        
        response = input("Did VSeeBox respond? (y/n): ")
        if response.lower() == 'y':
            print(f"✓ VSeeBox responds to {freq}Hz!")
            return freq
    
    print("\nNo response detected. A/V port might not support control signals.")
    return None

if __name__ == "__main__":
    print("=== VSeeBox A/V Port Control Test ===\n")
    send_test_signal()
