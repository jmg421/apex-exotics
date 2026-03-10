#!/usr/bin/env python3
"""
IR Receiver - Capture IR codes from VSeeBox remote
"""
import sounddevice as sd
import numpy as np
from scipy import signal

SAMPLE_RATE = 48000
CARRIER_FREQ = 38000

def capture_ir_signal(duration=5):
    """Capture IR signal from headphone jack"""
    print(f"Recording for {duration} seconds...")
    print("Press a button on the VSeeBox remote NOW (point at IR receiver)")
    
    # Find External Headphones (which is actually the input when IR receiver is plugged in)
    devices = sd.query_devices()
    input_device = None
    
    # IR receiver acts as microphone input
    for i, d in enumerate(devices):
        if d['max_input_channels'] > 0:
            print(f"Trying device {i}: {d['name']}")
    
    # Record from default input
    recording = sd.rec(int(duration * SAMPLE_RATE), 
                       samplerate=SAMPLE_RATE, 
                       channels=1,
                       dtype='float32')
    sd.wait()
    
    print("Recording complete!")
    return recording.flatten()

def decode_ir_signal(signal_data):
    """Decode IR signal to timing pattern"""
    # Detect 38kHz carrier
    # Demodulate to get timing pattern
    
    # High-pass filter to remove DC
    sos = signal.butter(4, 1000, 'hp', fs=SAMPLE_RATE, output='sos')
    filtered = signal.sosfilt(sos, signal_data)
    
    # Envelope detection
    analytic_signal = signal.hilbert(filtered)
    envelope = np.abs(analytic_signal)
    
    # Threshold detection
    threshold = np.max(envelope) * 0.3
    digital = envelope > threshold
    
    # Find transitions
    transitions = np.diff(digital.astype(int))
    transition_times = np.where(transitions != 0)[0]
    
    # Calculate pulse widths in microseconds
    pulse_widths = np.diff(transition_times) / SAMPLE_RATE * 1000000
    
    print(f"\nDetected {len(pulse_widths)} pulses")
    print("Pulse widths (μs):", pulse_widths[:20])
    
    return pulse_widths

if __name__ == "__main__":
    print("=== IR Code Capture ===\n")
    print("Point VSeeBox remote at IR receiver")
    print("Plug IR receiver into Mac headphone jack\n")
    
    signal_data = capture_ir_signal(duration=3)
    pulse_widths = decode_ir_signal(signal_data)
    
    # Save for later replay
    np.save('/tmp/ir_code.npy', pulse_widths)
    print("\n✓ IR code saved to /tmp/ir_code.npy")
