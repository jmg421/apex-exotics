#!/bin/bash
# Watch autonomous trading system in real-time

echo "🤖 AUTONOMOUS TRADING SYSTEM - LIVE MONITOR"
echo "============================================================"
echo "Scanning every 5 minutes during market hours (9:30 AM - 4:00 PM ET)"
echo "Press Ctrl+C to stop"
echo "============================================================"
echo ""

# Function to check if market is open
is_market_open() {
    hour=$(date +%H)
    minute=$(date +%M)
    day=$(date +%u)  # 1=Monday, 7=Sunday
    
    # Skip weekends
    if [ $day -gt 5 ]; then
        return 1
    fi
    
    # Market hours: 9:30 AM (09:30) to 4:00 PM (16:00)
    if [ $hour -eq 9 ] && [ $minute -ge 30 ]; then
        return 0
    elif [ $hour -ge 10 ] && [ $hour -lt 16 ]; then
        return 0
    else
        return 1
    fi
}

# Run continuously
scan_count=0

while true; do
    if is_market_open; then
        scan_count=$((scan_count + 1))
        
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📊 SCAN #$scan_count - $(date '+%Y-%m-%d %H:%M:%S ET')"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        # Run autonomous system
        python3 autonomous.py 2>&1 | grep -v "NotOpenSSLWarning" | grep -v "urllib3"
        
        echo ""
        echo "⏰ Next scan in 5 minutes..."
        sleep 300  # 5 minutes
    else
        echo "⏸️  Market closed - waiting... ($(date '+%H:%M:%S'))"
        sleep 60  # Check every minute
    fi
done
