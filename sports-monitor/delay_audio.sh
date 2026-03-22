#!/bin/bash
# Delay Loopback audio to sync with HLS video latency
# Adjust DELAY_SECONDS to match your video latency
DELAY_SECONDS=${1:-5.1}
DELAY_MS=$(python3 -c "print(int(float($DELAY_SECONDS)*1000))")

echo "🔊 Delaying Loopback audio by ${DELAY_SECONDS}s (${DELAY_MS}ms)"
echo "   Adjust: ./delay_audio.sh <seconds>"

if [ "$DELAY_MS" -gt 0 ]; then
    ffmpeg -f avfoundation -i ":0" -af "adelay=${DELAY_MS}|${DELAY_MS}" -f audiotoolbox "" -loglevel quiet
else
    ffmpeg -f avfoundation -i ":0" -f audiotoolbox "" -loglevel quiet
fi
