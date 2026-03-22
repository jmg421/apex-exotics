#!/bin/bash
# Ultra-low-latency Elgato capture — direct MJPEG stream, no HLS
# Audio via Loopback
echo "🎥 Low-latency stream at http://localhost:8082"

ffmpeg -f avfoundation -pixel_format nv12 -framerate 30 -video_size 1920x1080 \
    -probesize 10M -thread_queue_size 1024 -i "0:none" \
    -vf "fps=30" \
    -c:v libx264 -preset ultrafast -tune zerolatency -b:v 15000k \
    -an -f mpegts "tcp://0.0.0.0:8082?listen"
