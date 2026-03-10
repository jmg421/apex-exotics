#!/bin/bash
# Continuous scan for VSeeBox remote and auto-pair

echo "Scanning for VSeeBox Remoter..."
echo "Unpair it from VSeeBox now, then press any button on the remote"
echo ""

while true; do
    # Scan for 3 seconds
    result=$(blueutil --inquiry 3 2>&1 | grep -i "remoter\|vseebox")
    
    if [ ! -z "$result" ]; then
        echo "Found: $result"
        
        # Extract MAC address
        mac=$(echo "$result" | grep -oE "[0-9a-f]{2}-[0-9a-f]{2}-[0-9a-f]{2}-[0-9a-f]{2}-[0-9a-f]{2}-[0-9a-f]{2}")
        
        if [ ! -z "$mac" ]; then
            echo "Pairing with $mac..."
            blueutil --pair "$mac"
            
            if [ $? -eq 0 ]; then
                echo "✓ Paired successfully!"
                echo "Testing connection..."
                blueutil --connect "$mac"
                exit 0
            fi
        fi
    fi
    
    echo -n "."
    sleep 1
done
