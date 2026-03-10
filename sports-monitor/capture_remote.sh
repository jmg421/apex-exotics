#!/bin/bash
# Capture Bluetooth HID traffic from VSeeBox remote

echo "Starting Bluetooth packet capture..."
echo "Press buttons on the VSeeBox remote now"
echo "Press Ctrl+C when done"
echo ""

# Capture for 60 seconds or until interrupted
sudo tcpdump -i any -w /tmp/vseebox_bt_capture.pcap 'bluetooth' 2>&1 &
PID=$!

echo "Capturing... (PID: $PID)"
echo "Press remote buttons, then Ctrl+C"

wait $PID

echo ""
echo "Capture saved to /tmp/vseebox_bt_capture.pcap"
echo "Analyzing..."

tshark -r /tmp/vseebox_bt_capture.pcap -Y "bthid" 2>/dev/null | head -20
