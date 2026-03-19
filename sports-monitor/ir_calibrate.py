#!/Users/apple/apex-exotics/venv/bin/python
"""
Autonomous IR calibration - send buttons, screenshot, analyze results.
Tests each button and records what happened on screen.
"""
import subprocess
import time
import json
import os
from datetime import datetime
from channel_switcher import send_ir_code, get_device, change_channel, send_command
from broadlink_config import IR_CODES

SCREENSHOT_DIR = "data/calibration"
RESULTS_FILE = "data/calibration/results.json"

def screenshot(label):
    """Capture screen and return path."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%H%M%S")
    path = f"{SCREENSHOT_DIR}/{ts}_{label}.png"
    subprocess.run(["screencapture", "-x", path], check=True)
    return path

def wait_and_capture(label, delay=2.0):
    """Wait for VseeBox to respond, then screenshot."""
    time.sleep(delay)
    return screenshot(label)

def test_single_button(name, delay=2.0):
    """Send one button press and capture result."""
    print(f"\n--- Testing: {name} ---")
    before = screenshot(f"{name}_before")
    print(f"  Before: {before}")
    
    if name.startswith("CH:"):
        # Direct channel entry
        ch = name.split(":")[1]
        change_channel(int(ch))
    else:
        send_ir_code(IR_CODES[name])
    
    after = wait_and_capture(f"{name}_after", delay)
    print(f"  After:  {after}")
    return {"button": name, "before": before, "after": after}

def calibration_sequence():
    """Run full calibration test."""
    results = []
    print("=== IR Calibration Start ===")
    print(f"Time: {datetime.now()}")
    print(f"Screenshots: {SCREENSHOT_DIR}/\n")

    # Ensure device is connected
    get_device()
    print("✅ Broadlink connected\n")

    # Phase 1: Navigation buttons (safe, non-destructive)
    print("== Phase 1: Navigation ==")
    for btn in ["EPG", "OK", "UP", "DOWN", "LEFT", "RIGHT", "BACK", "HOME"]:
        results.append(test_single_button(btn))
        time.sleep(1)

    # Phase 2: Direct channel entry
    print("\n== Phase 2: Direct Channel Entry ==")
    for ch in ["0815", "0809", "0812"]:
        results.append(test_single_button(f"CH:{ch}"))
        time.sleep(2)

    # Phase 3: Channel up/down (known problematic)
    print("\n== Phase 3: Channel Up/Down ==")
    results.append(test_single_button("CHANNEL-UP", delay=3))
    results.append(test_single_button("CHANNEL-DOWN", delay=3))

    # Save results
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n=== Calibration Complete ===")
    print(f"Results: {RESULTS_FILE}")
    print(f"Screenshots: {len(results) * 2} images in {SCREENSHOT_DIR}/")
    return results

if __name__ == "__main__":
    calibration_sequence()
