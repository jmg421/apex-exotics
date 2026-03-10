#!/usr/bin/env python3
"""
Step 1: List all HID devices to find the VSeeBox remote
"""
import hid

print("Scanning for HID devices...\n")

for device in hid.enumerate():
    print(f"Device: {device['product_string']}")
    print(f"  Manufacturer: {device['manufacturer_string']}")
    print(f"  Vendor ID: 0x{device['vendor_id']:04x}")
    print(f"  Product ID: 0x{device['product_id']:04x}")
    print(f"  Path: {device['path']}")
    print()
